"""Patient Routes"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import Appointment, Doctor, TimeSlot, Payment, Review
from datetime import datetime

patient_bp = Blueprint("patient", __name__)


def patient_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role not in ("patient", "admin"):
            flash("Access denied. Patients only.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


@patient_bp.route("/dashboard")
@patient_required
def dashboard():
    appointments = (
        Appointment.query.filter_by(patient_id=current_user.id)
        .order_by(Appointment.created_at.desc())
        .all()
    )
    upcoming = [a for a in appointments if a.status in ("pending", "approved")]
    past = [a for a in appointments if a.status in ("completed", "cancelled", "rejected")]

    # Build set of appointment IDs that already have a review
    reviewed_ids = {
        r.appointment_id
        for r in Review.query.filter_by(patient_id=current_user.id).all()
    }

    return render_template(
        "patient/dashboard.html",
        upcoming=upcoming,
        past=past,
        reviewed_ids=reviewed_ids,
    )


@patient_bp.route("/book/<int:doctor_id>", methods=["GET", "POST"])
@patient_required
def book_appointment(doctor_id):
    """
    Booking page for a specific doctor.
    GET  → shows the doctor's available slots for the patient to pick.
    POST → validates the chosen slot, checks time conflicts, then creates appointment.
    """
    from datetime import date as date_cls
    doctor = Doctor.query.get_or_404(doctor_id)
    today = date_cls.today()

    # All available future slots for this doctor
    slots = (
        TimeSlot.query
        .filter_by(doctor_id=doctor_id, is_available=True)
        .filter(TimeSlot.date >= today)
        .order_by(TimeSlot.date, TimeSlot.start_time)
        .all()
    )

    if request.method == "POST":
        slot_id = request.form.get("slot_id", "").strip()
        notes = request.form.get("notes", "").strip()

        if not slot_id:
            flash("Please select a time slot.", "warning")
            return render_template("patient/book.html", doctor=doctor, slots=slots)

        slot = TimeSlot.query.get(int(slot_id))

        # Slot must exist, belong to this doctor, and still be available
        if not slot or slot.doctor_id != doctor_id or not slot.is_available:
            flash("This slot is no longer available. Please choose another.", "warning")
            return render_template("patient/book.html", doctor=doctor, slots=slots)

        # Same patient booking same slot twice
        already_booked = Appointment.query.filter_by(
            patient_id=current_user.id,
            time_slot_id=slot.id,
        ).filter(Appointment.status.notin_(["cancelled", "rejected"])).first()
        if already_booked:
            flash("You have already booked this slot.", "warning")
            return redirect(url_for("patient.dashboard"))

        # ── Time-conflict check ─────────────────────────────────────────────
        # Find all active appointments for this patient on the same date
        patient_appts_that_day = (
            Appointment.query
            .filter_by(patient_id=current_user.id)
            .filter(Appointment.status.notin_(["cancelled", "rejected"]))
            .join(TimeSlot)
            .filter(TimeSlot.date == slot.date)
            .all()
        )
        for existing in patient_appts_that_day:
            ex_slot = existing.time_slot
            # Overlap: existing starts before new ends AND existing ends after new starts
            if ex_slot.start_time < slot.end_time and ex_slot.end_time > slot.start_time:
                conflict_doctor = existing.doctor.user.name
                conflict_time = ex_slot.start_time.strftime("%I:%M %p")
                flash(
                    f"You already have an appointment at {conflict_time} on {slot.date.strftime('%B %d, %Y')} "
                    f"with {conflict_doctor}. Please choose a different time.",
                    "danger"
                )
                return render_template("patient/book.html", doctor=doctor, slots=slots)

        # All checks passed — create the appointment
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            time_slot_id=slot.id,
            notes=notes,
            status="pending",
            payment_status="unpaid",
        )
        slot.is_available = False
        db.session.add(appointment)
        db.session.commit()

        flash("Appointment booked! Please complete payment.", "success")
        return redirect(url_for("payment.checkout", appointment_id=appointment.id))

    return render_template("patient/book.html", doctor=doctor, slots=slots)


@patient_bp.route("/cancel/<int:appointment_id>", methods=["POST"])
@patient_required
def cancel_appointment(appointment_id):
    appt = Appointment.query.filter_by(
        id=appointment_id, patient_id=current_user.id
    ).first_or_404()

    if appt.status not in ("pending", "approved"):
        flash("This appointment cannot be cancelled.", "warning")
        return redirect(url_for("patient.dashboard"))

    appt.status = "cancelled"
    if appt.time_slot:
        appt.time_slot.is_available = True

    if appt.payment and appt.payment.payment_status == "paid":
        appt.payment.payment_status = "refunded"
        appt.payment_status = "refunded"

    db.session.commit()
    flash("Appointment cancelled successfully.", "info")
    return redirect(url_for("patient.dashboard"))


@patient_bp.route("/appointment/<int:appointment_id>")
@patient_required
def appointment_detail(appointment_id):
    appt = Appointment.query.filter_by(
        id=appointment_id, patient_id=current_user.id
    ).first_or_404()
    return render_template("patient/appointment_detail.html", appt=appt)


@patient_bp.route("/review/<int:appointment_id>", methods=["GET", "POST"])
@patient_required
def submit_review(appointment_id):
    appt = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=current_user.id,
        status="completed",
    ).first_or_404()

    existing = Review.query.filter_by(
        patient_id=current_user.id, appointment_id=appointment_id
    ).first()
    if existing:
        flash("You have already reviewed this appointment.", "info")
        return redirect(url_for("patient.dashboard"))

    if request.method == "POST":
        try:
            rating = int(request.form.get("rating", 5))
            rating = max(1, min(5, rating))
        except (ValueError, TypeError):
            rating = 5
        comment = request.form.get("comment", "").strip()

        review = Review(
            patient_id=current_user.id,
            doctor_id=appt.doctor_id,
            appointment_id=appointment_id,
            rating=rating,
            comment=comment,
        )
        db.session.add(review)

        doc = appt.doctor
        total = doc.rating * doc.total_reviews + rating
        doc.total_reviews += 1
        doc.rating = round(total / doc.total_reviews, 1)

        db.session.commit()
        flash("Review submitted. Thank you!", "success")
        return redirect(url_for("patient.dashboard"))

    return render_template("patient/review.html", appt=appt)