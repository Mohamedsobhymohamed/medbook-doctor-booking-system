"""Consultation Routes"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import Appointment

consultation_bp = Blueprint("consultation", __name__)


def consultation_access_required(f):
    @wraps(f)
    def decorated(appointment_id, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        appt = Appointment.query.get_or_404(appointment_id)
        if current_user.role == "patient" and appt.patient_id != current_user.id:
            flash("Access denied.", "danger")
            return redirect(url_for("main.index"))
        if current_user.role == "doctor" and appt.doctor.user_id != current_user.id:
            flash("Access denied.", "danger")
            return redirect(url_for("main.index"))
        return f(appt, *args, **kwargs)
    return decorated


@consultation_bp.route("/join/<int:appointment_id>")
@consultation_access_required
def join_consultation(appt):
    if appt.status != "approved":
        flash("Consultation is not available yet.", "warning")
        return redirect(url_for("main.index"))
    if not appt.meeting_link:
        flash("Meeting link is not set yet.", "danger")
        return redirect(url_for("main.index"))
    return render_template("consultation/join.html", appt=appt)


@consultation_bp.route("/start/<int:appointment_id>")
@consultation_access_required
def start_consultation(appt):
    if not appt.meeting_link:
        flash("No meeting link available.", "danger")
        return redirect(url_for("main.index"))
    return redirect(appt.meeting_link)


@consultation_bp.route("/details/<int:appointment_id>")
@consultation_access_required
def consultation_details(appt):
    return render_template("consultation/details.html", appt=appt)