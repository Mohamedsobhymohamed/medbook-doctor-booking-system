"""
Admin Routes - Dashboard, User Management, System Overview
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import User, Doctor, Appointment, TimeSlot, Payment

admin_bp = Blueprint("admin", __name__)


# ─── Admin Access Control ──────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


# ─── Dashboard ─────────────────────────────────────────────────────────────────
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()

    recent_appointments = (
        Appointment.query.order_by(Appointment.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        recent_appointments=recent_appointments,
    )


# ─── Manage Users ──────────────────────────────────────────────────────────────
@admin_bp.route("/users")
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


# ─── Toggle User Active/Inactive ───────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>/toggle")
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("Cannot deactivate admin account.", "warning")
        return redirect(url_for("admin.manage_users"))

    user.is_active = not user.is_active
    db.session.commit()

    flash(f"User {'activated' if user.is_active else 'deactivated'}.", "success")
    return redirect(url_for("admin.manage_users"))


# ─── View All Appointments ─────────────────────────────────────────────────────
@admin_bp.route("/appointments")
@admin_required
def all_appointments():
    appointments = (
        Appointment.query.order_by(Appointment.created_at.desc()).all()
    )
    return render_template("admin/appointments.html", appointments=appointments)


# ─── Manage Doctors ────────────────────────────────────────────────────────────
@admin_bp.route("/doctors")
@admin_required
def manage_doctors():
    doctors = Doctor.query.join(User).order_by(User.name).all()
    return render_template("admin/doctors.html", doctors=doctors)


# ─── Delete Doctor ─────────────────────────────────────────────────────────────
@admin_bp.route("/doctors/<int:doctor_id>/delete", methods=["POST"])
@admin_required
def delete_doctor(doctor_id):
    """
    Safely delete a doctor and all related data.

    The IntegrityError happens because SQLAlchemy's ORM tries to SET doctor_id = NULL
    on appointments before deleting the Doctor row, violating the NOT NULL constraint.
    Fix: delete everything in the correct dependency order using direct DB-level deletes
    so the ORM never tries to nullify the FK.
    """
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor_name = doctor.user.name
    user_id = doctor.user_id

    try:
        # Step 1: Collect all appointment IDs for this doctor
        appt_ids = [
            row.id for row in
            Appointment.query.filter_by(doctor_id=doctor_id).with_entities(Appointment.id).all()
        ]

        if appt_ids:
            # Step 2: Delete payments linked to those appointments first
            Payment.query.filter(Payment.appointment_id.in_(appt_ids)).delete(
                synchronize_session="fetch"
            )

            # Step 3: Delete the appointments themselves
            Appointment.query.filter(Appointment.id.in_(appt_ids)).delete(
                synchronize_session="fetch"
            )

        # Step 4: Delete all time slots for this doctor
        TimeSlot.query.filter_by(doctor_id=doctor_id).delete(
            synchronize_session="fetch"
        )

        # Step 5: Delete the Doctor profile row
        Doctor.query.filter_by(id=doctor_id).delete(synchronize_session="fetch")

        # Step 6: Delete the User account
        User.query.filter_by(id=user_id).delete(synchronize_session="fetch")

        db.session.commit()
        flash(f"Doctor {doctor_name} has been permanently removed.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error removing doctor: {str(e)}", "danger")

    return redirect(url_for("admin.manage_doctors"))