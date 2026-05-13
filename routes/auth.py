"""Auth Routes - Register, Login, Logout"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User, Doctor

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "patient")
        phone = request.form.get("phone", "").strip()

        errors = []
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if role not in ("patient", "doctor"):
            errors.append("Invalid role.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("auth/register.html")

        user = User(name=name, email=email, role=role, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == "doctor":
            specialization = request.form.get("specialization", "General Practice").strip() or "General Practice"
            try:
                fee = float(request.form.get("fee", 50.00))
            except (ValueError, TypeError):
                fee = 50.00
            bio = request.form.get("bio", "").strip()
            try:
                years = int(request.form.get("years_experience", 0))
            except (ValueError, TypeError):
                years = 0

            doctor = Doctor(
                user_id=user.id,
                specialization=specialization,
                fee=fee,
                bio=bio,
                years_experience=years,
                is_available=True,
            )
            db.session.add(doctor)

        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return _redirect_by_role(user)
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name).strip()
        current_user.phone = request.form.get("phone", current_user.phone)

        new_password = request.form.get("new_password", "")
        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return redirect(url_for("auth.profile"))
            current_user.set_password(new_password)

        if current_user.role == "doctor" and current_user.doctor_profile:
            dp = current_user.doctor_profile
            dp.bio = request.form.get("bio", dp.bio)
            try:
                dp.years_experience = int(request.form.get("years_experience", dp.years_experience))
            except (ValueError, TypeError):
                pass

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html")


def _redirect_by_role(user):
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif user.role == "doctor":
        return redirect(url_for("doctor.dashboard"))
    else:
        return redirect(url_for("patient.dashboard"))