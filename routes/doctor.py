"""Doctor Routes"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import Appointment, Doctor, TimeSlot, User
from datetime import datetime, date, time

doctor_bp = Blueprint("doctor", __name__)


def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        # TC20: Doctors can't access patient routes (enforced in patient_required)
        # TC19: Patients can't access doctor routes
        if current_user.role not in ("doctor", "admin"):
            flash("Access denied. Doctors only.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


def get_doctor_or_404():
    doc = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doc:
        flash("Doctor profile not found.", "danger")
        return None
    return doc


@doctor_bp.route("/dashboard")
@doctor_required
def dashboard():
    doctor = get_doctor_or_404()
    if not doctor:
        return redirect(url_for("main.index"))
    today = date.today()

    today_appts = (
        Appointment.query.filter_by(doctor_id=doctor.id)
        .join(TimeSlot)
        .filter(TimeSlot.date == today)
        .order_by(TimeSlot.start_time)
        .all()
    )
    pending = Appointment.query.filter_by(doctor_id=doctor.id, status="pending").count()
    total = Appointment.query.filter_by(doctor_id=doctor.id).count()

    return render_template(
        "doctor/dashboard.html",
        doctor=doctor,
        today_appts=today_appts,
        pending_count=pending,
        total_count=total,
        today=today,
    )


@doctor_bp.route("/appointments")
@doctor_required
def appointments():
    doctor = get_doctor_or_404()
    if not doctor:
        return redirect(url_for("main.index"))
    status_filter = request.args.get("status", "")

    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    appts = query.join(TimeSlot).order_by(TimeSlot.date.desc(), TimeSlot.start_time).all()
    return render_template("doctor/appointments.html", appts=appts, status_filter=status_filter)


@doctor_bp.route("/appointments/<int:appt_id>/action", methods=["POST"])
@doctor_required
def appointment_action(appt_id):
    doctor = get_doctor_or_404()
    if not doctor:
        return redirect(url_for("main.index"))
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first_or_404()
    action = request.form.get("action")

    if action == "approve" and appt.status == "pending":
        appt.status = "approved"
        flash("Appointment approved.", "success")
    elif action == "reject" and appt.status in ("pending", "approved"):
        appt.status = "rejected"
        if appt.time_slot:
            appt.time_slot.is_available = True
        flash("Appointment rejected.", "info")
    elif action == "complete" and appt.status == "approved":
        appt.status = "completed"
        appt.doctor_notes = request.form.get("doctor_notes", "")
        flash("Appointment marked as completed.", "success")
    else:
        flash("Invalid action.", "warning")

    db.session.commit()
    return redirect(url_for("doctor.appointments"))


@doctor_bp.route("/schedule", methods=["GET", "POST"])
@doctor_required
def schedule():
    doctor = get_doctor_or_404()
    if not doctor:
        return redirect(url_for("main.index"))
    today = date.today()

    if request.method == "POST":
        slot_date_str = request.form.get("date")
        start_str = request.form.get("start_time")
        end_str = request.form.get("end_time")

        try:
            slot_date = datetime.strptime(slot_date_str, "%Y-%m-%d").date()
            start_t = datetime.strptime(start_str, "%H:%M").time()
            end_t = datetime.strptime(end_str, "%H:%M").time()
        except (ValueError, TypeError):
            flash("Invalid date/time format.", "danger")
            return redirect(url_for("doctor.schedule"))

        if slot_date < today:
            flash("Cannot add slots in the past.", "warning")
            return redirect(url_for("doctor.schedule"))

        if start_t >= end_t:
            flash("End time must be after start time.", "warning")
            return redirect(url_for("doctor.schedule"))

        overlap = TimeSlot.query.filter_by(
            doctor_id=doctor.id, date=slot_date
        ).filter(
            TimeSlot.start_time < end_t,
            TimeSlot.end_time > start_t,
        ).first()

        if overlap:
            flash("This slot overlaps with an existing slot.", "danger")
            return redirect(url_for("doctor.schedule"))

        slot = TimeSlot(
            doctor_id=doctor.id,
            date=slot_date,
            start_time=start_t,
            end_time=end_t,
            is_available=True,
        )
        db.session.add(slot)
        db.session.commit()
        flash("Time slot added successfully.", "success")
        return redirect(url_for("doctor.schedule"))

    slots = (
        TimeSlot.query.filter_by(doctor_id=doctor.id)
        .filter(TimeSlot.date >= today)
        .order_by(TimeSlot.date, TimeSlot.start_time)
        .all()
    )
    return render_template("doctor/schedule.html", slots=slots, today=today)


@doctor_bp.route("/schedule/<int:slot_id>/delete", methods=["POST"])
@doctor_required
def delete_slot(slot_id):
    doctor = get_doctor_or_404()
    if not doctor:
        return redirect(url_for("main.index"))
    slot = TimeSlot.query.filter_by(id=slot_id, doctor_id=doctor.id).first_or_404()

    if slot.appointment and slot.appointment.status in ("pending", "approved"):
        flash("Cannot delete a slot with an active appointment.", "warning")
    else:
        db.session.delete(slot)
        db.session.commit()
        flash("Time slot deleted.", "info")

    return redirect(url_for("doctor.schedule"))


@doctor_bp.route("/appointments/<int:appt_id>/meeting-link", methods=["POST"])
@doctor_required
def set_meeting_link(appt_id):
    doctor = get_doctor_or_404()
    if not doctor:
        return redirect(url_for("main.index"))
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first_or_404()

    if appt.status != "approved":
        flash("Only approved appointments can have a meeting link.", "warning")
        return redirect(url_for("doctor.appointments"))

    link = request.form.get("meeting_link", "").strip()
    if not link:
        link = f"https://meet.jit.si/clinic-{appt.id}-{appt.doctor_id}"

    appt.meeting_link = link
    db.session.commit()
    flash("Meeting link saved.", "success")
    return redirect(url_for("doctor.appointments"))