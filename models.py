"""
Database Models - Online Doctor Booking System
"""

from datetime import datetime
from extensions import db, login_manager, bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="patient")
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    appointments = db.relationship("Appointment", foreign_keys="Appointment.patient_id", backref="patient", lazy=True)
    payments = db.relationship("Payment", backref="user", lazy=True)
    doctor_profile = db.relationship("Doctor", backref="user", uselist=False, lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    fee = db.Column(db.Float, default=50.00)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    profile_image = db.Column(db.String(200), nullable=True)
    years_experience = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)

    time_slots = db.relationship("TimeSlot", backref="doctor", lazy=True, cascade="all, delete-orphan")
    appointments = db.relationship("Appointment", backref="doctor", lazy=True)

    def __repr__(self):
        return f"<Doctor {self.user.name} - {self.specialization}>"


class TimeSlot(db.Model):
    __tablename__ = "time_slots"
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship("Appointment", backref="time_slot", uselist=False, lazy=True)

    def __repr__(self):
        return f"<TimeSlot {self.date} {self.start_time}>"


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    time_slot_id = db.Column(db.Integer, db.ForeignKey("time_slots.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    meeting_link = db.Column(db.String(300), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    doctor_notes = db.Column(db.Text, nullable=True)
    payment_status = db.Column(db.String(20), default="unpaid")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payment = db.relationship("Payment", backref="appointment", uselist=False, lazy=True)

    def __repr__(self):
        return f"<Appointment #{self.id} - {self.status}>"


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="usd")
    stripe_payment_intent_id = db.Column(db.String(200), nullable=True)
    stripe_charge_id = db.Column(db.String(200), nullable=True)
    payment_status = db.Column(db.String(20), default="pending")
    payment_method = db.Column(db.String(50), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payment #{self.id} - {self.payment_status}>"


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("Doctor", foreign_keys=[doctor_id])

    def __repr__(self):
        return f"<Review {self.rating}* for Doctor#{self.doctor_id}>"