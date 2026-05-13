"""Main Routes - Homepage, Doctor Listing, Doctor Profile, Reviews"""

from flask import Blueprint, render_template, request, jsonify
from models import Doctor, User, TimeSlot, Review
from datetime import date

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    doctors = Doctor.query.join(User).filter(Doctor.is_available == True).all()
    specializations = _distinct_specializations()
    return render_template("index.html", doctors=doctors, specializations=specializations)


@main_bp.route("/doctors")
def list_doctors():
    search = request.args.get("search", "")
    spec = request.args.get("specialization", "")
    query = Doctor.query.join(User).filter(Doctor.is_available == True)
    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))
    if spec:
        query = query.filter(Doctor.specialization.ilike(f"%{spec}%"))
    doctors = query.all()
    specializations = _distinct_specializations()
    return render_template("doctors.html", doctors=doctors, specializations=specializations,
                           search=search, selected_spec=spec)


@main_bp.route("/doctors/<int:doctor_id>")
def doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    today = date.today()
    available_slots = (
        TimeSlot.query.filter_by(doctor_id=doctor_id, is_available=True)
        .filter(TimeSlot.date >= today)
        .order_by(TimeSlot.date, TimeSlot.start_time)
        .all()
    )
    reviews = Review.query.filter_by(doctor_id=doctor_id).order_by(Review.created_at.desc()).all()
    return render_template("doctor_profile.html", doctor=doctor, slots=available_slots, reviews=reviews)


@main_bp.route("/reviews")
def all_reviews():
    """Public reviews page — all reviews across all doctors."""
    reviews = (
        Review.query
        .order_by(Review.created_at.desc())
        .all()
    )
    doctors = Doctor.query.join(User).filter(Doctor.is_available == True).all()
    return render_template("reviews.html", reviews=reviews, doctors=doctors)


@main_bp.route("/api/doctors/<int:doctor_id>/slots")
def api_doctor_slots(doctor_id):
    today = date.today()
    slots = (
        TimeSlot.query.filter_by(doctor_id=doctor_id, is_available=True)
        .filter(TimeSlot.date >= today)
        .order_by(TimeSlot.date, TimeSlot.start_time)
        .all()
    )
    data = [{"id": s.id, "date": s.date.strftime("%Y-%m-%d"),
              "start_time": s.start_time.strftime("%H:%M"),
              "end_time": s.end_time.strftime("%H:%M")} for s in slots]
    return jsonify(data)


def _distinct_specializations():
    from extensions import db
    rows = db.session.query(Doctor.specialization).distinct().all()
    return [r[0] for r in rows]
