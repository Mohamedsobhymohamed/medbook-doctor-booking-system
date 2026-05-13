"""Payment Routes"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Appointment, Payment
from datetime import datetime

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/checkout/<int:appointment_id>")
@login_required
def checkout(appointment_id):
    # TC21: Only the patient who owns this appointment can access
    appt = Appointment.query.filter_by(
        id=appointment_id, patient_id=current_user.id
    ).first_or_404()

    # TC26: Payment already done - redirect to dashboard
    if appt.payment_status == "paid":
        flash("This appointment is already paid.", "info")
        return redirect(url_for("patient.dashboard"))

    doctor = appt.doctor
    fee = doctor.fee

    return render_template(
        "payment/checkout.html",
        appt=appt,
        doctor=doctor,
        fee=fee,
    )


@payment_bp.route("/confirm/<int:appointment_id>", methods=["POST"])
@login_required
def confirm_payment(appointment_id):
    """Simple payment confirmation (no Stripe required for testing)."""
    appt = Appointment.query.filter_by(
        id=appointment_id, patient_id=current_user.id
    ).first_or_404()

    # TC26: Already paid
    if appt.payment_status == "paid":
        flash("Already paid.", "info")
        return redirect(url_for("patient.dashboard"))

    # Create payment record if not exists
    payment = Payment.query.filter_by(appointment_id=appt.id).first()
    if not payment:
        payment = Payment(
            user_id=current_user.id,
            appointment_id=appt.id,
            amount=appt.doctor.fee,
            payment_status="paid",
            payment_date=datetime.utcnow(),
        )
        db.session.add(payment)
    else:
        payment.payment_status = "paid"
        payment.payment_date = datetime.utcnow()

    # TC12: CRITICAL - payment_status=paid AND status=approved
    appt.payment_status = "paid"
    appt.status = "approved"

    db.session.commit()
    return redirect(url_for("payment.payment_success", appointment_id=appt.id))


@payment_bp.route("/success/<int:appointment_id>")
@login_required
def payment_success(appointment_id):
    appt = Appointment.query.filter_by(
        id=appointment_id, patient_id=current_user.id
    ).first_or_404()

    # Ensure marked paid if someone navigates here directly
    if appt.payment_status != "paid":
        appt.payment_status = "paid"
        appt.status = "approved"
        payment = Payment.query.filter_by(appointment_id=appt.id).first()
        if payment:
            payment.payment_status = "paid"
            payment.payment_date = datetime.utcnow()
        db.session.commit()

    flash("Payment successful! Your appointment is confirmed.", "success")
    return render_template("payment/success.html", appt=appt)


@payment_bp.route("/cancel/<int:appointment_id>")
@login_required
def payment_cancel(appointment_id):
    # TC13: Cancel payment - appointment still exists, status stays pending/unpaid
    appt = Appointment.query.filter_by(
        id=appointment_id, patient_id=current_user.id
    ).first_or_404()

    # Do NOT change status or payment_status - appointment stays pending/unpaid
    flash("Payment cancelled. Your appointment is still pending.", "warning")
    return render_template("payment/cancel.html", appt=appt)


@payment_bp.route("/history")
@login_required
def payment_history():
    payments = (
        Payment.query.filter_by(user_id=current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return render_template("payment/history.html", payments=payments)