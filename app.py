"""
Online Doctor Booking System - Main Application Entry Point
"""
import os
from flask import Flask, render_template
from dotenv import load_dotenv
from extensions import db, login_manager, bcrypt, mail

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///doctor_booking.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["STRIPE_PUBLISHABLE_KEY"] = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    app.config["STRIPE_SECRET_KEY"] = os.getenv("STRIPE_SECRET_KEY", "")
    app.config["STRIPE_WEBHOOK_SECRET"] = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    app.config["DEFAULT_CONSULTATION_FEE"] = int(os.getenv("DEFAULT_CONSULTATION_FEE", 5000))
    app.config["BASE_URL"] = os.getenv("BASE_URL", "http://localhost:5000")
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register blueprints
    from routes.auth import auth_bp
    from routes.patient import patient_bp
    from routes.doctor import doctor_bp
    from routes.admin import admin_bp
    from routes.payment import payment_bp
    from routes.consultation import consultation_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(patient_bp, url_prefix="/patient")
    app.register_blueprint(doctor_bp, url_prefix="/doctor")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(payment_bp, url_prefix="/payment")
    app.register_blueprint(consultation_bp, url_prefix="/consultation")

    # Custom 404
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    from models import User, Doctor, TimeSlot
    from datetime import date, time, timedelta

    if User.query.first():
        return

    admin = User(name="Admin", email="admin@clinic.com", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)

    doctors_data = [
        ("Dr. Sarah Ahmed", "Cardiology", "dr.sarah@clinic.com"),
        ("Dr. Mohamed Ali", "Dermatology", "dr.mohamed@clinic.com"),
        ("Dr. Layla Hassan", "General Practice", "dr.layla@clinic.com"),
        ("Dr. Omar Khaled", "Orthopedics", "dr.omar@clinic.com"),
    ]

    today = date.today()
    for name, spec, email in doctors_data:
        user = User(name=name, email=email, role="doctor")
        user.set_password("doctor123")
        db.session.add(user)
        db.session.flush()

        doc = Doctor(user_id=user.id, specialization=spec, fee=50.00)
        db.session.add(doc)
        db.session.flush()

        for day_offset in range(1, 8):
            slot_date = today + timedelta(days=day_offset)
            if slot_date.weekday() < 5:
                for hour in [9, 10, 11, 14, 15, 16]:
                    slot = TimeSlot(
                        doctor_id=doc.id,
                        date=slot_date,
                        start_time=time(hour, 0),
                        end_time=time(hour, 30),
                        is_available=True,
                    )
                    db.session.add(slot)

    patient = User(name="Test Patient", email="patient@test.com", role="patient")
    patient.set_password("patient123")
    db.session.add(patient)

    db.session.commit()
    print("Sample data seeded.")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)