<div align="center">

<img src="static/img/MEDBook.png" alt="MedBook Logo" width="120" height="120" style="border-radius:50%"/>

# MedBook — Online Doctor Booking System

**A full-stack web application for scheduling medical appointments online**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-0D9488?style=for-the-badge)](LICENSE)

[Features](#-features) · [Screenshots](#-screenshots) · [Quick Start](#-quick-start) · [Test Accounts](#-test-accounts) · [Project Structure](#-project-structure)

</div>

---

## 📋 Overview

MedBook is a complete online doctor booking platform built with Flask. Patients can discover verified doctors, pick available time slots, pay for consultations, and leave reviews — all in one place. Doctors manage their schedules and appointments through a dedicated dashboard. Administrators oversee the entire system including user and doctor management.

Built as a Software Engineering course project (CSE 327 · Spring 2025) demonstrating full SDLC implementation: requirements, design (UML), implementation, testing, and maintenance.

---

## ✨ Features

### 👤 Patient
- Register and log in with secure bcrypt-hashed passwords
- Browse and search doctors by name or specialization
- Select appointment slots shown with **day name + full date + time** on each card
- Automatic **time conflict detection** — blocked if you already have an appointment at that time with any doctor
- Pay for appointments and view a success confirmation
- Cancel appointments (slot freed automatically)
- Submit star ratings and written reviews for completed appointments
- Dashboard showing upcoming and past appointments with one-click Pay / Cancel / Leave Review

### 👨‍⚕️ Doctor
- Dedicated dashboard with today's appointments, pending count, and totals
- Add time slots (date, start time, end time) with overlap prevention
- Delete available slots; booked slots are protected
- Approve, reject, or mark appointments as completed
- Set video meeting links for approved appointments

### 🛡️ Admin
- Full user management — activate or deactivate any user
- Doctor management — view all doctors with slot counts and ratings
- **Remove doctor** — permanently deletes doctor account with all linked slots, appointments, and payments (safe cascading deletion)
- View all appointments across the entire system

### 🌟 Reviews Page
- Public reviews page at `/reviews`
- Live star-rating filter (1–5 stars) and name search — no page reload
- Average rating, total reviews, and doctor count displayed at the top

### 🔒 Security
- Role-based access control: patients can't access doctor routes and vice versa
- URL tampering protection — resource ownership verified on every route
- Double-booking and time-slot race conditions prevented at the database layer
- Re-payment blocked for already-paid appointments

---

## 🖥️ Screenshots

> _Place your screenshots in a `/screenshots` folder and update the paths below._

| Homepage | Book Appointment | Patient Dashboard |
|----------|-----------------|-------------------|
| ![Home](screenshots/home.png) | ![Book](screenshots/book.png) | ![Dashboard](screenshots/dashboard.png) |

| Reviews Page | Doctor Dashboard | Admin Panel |
|-------------|-----------------|-------------|
| ![Reviews](screenshots/reviews.png) | ![Doctor](screenshots/doctor.png) | ![Admin](screenshots/admin.png) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/medbook-doctor-booking.git
cd medbook-doctor-booking
```

### 2 — Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure environment variables

Copy the example env file and edit it:

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```env
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///doctor_booking.db
```

> Stripe and Mail keys are optional for local testing — the system works without them using the built-in simple payment flow.

### 5 — Run the application

```bash
python app.py
```

The app will:

1. Create the SQLite database automatically
2. Seed 4 sample doctors, 1 patient, and 120+ available time slots
3. Start the development server at **http://127.0.0.1:5000**

---

## 🔑 Test Accounts

These accounts are created automatically on first run:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@clinic.com` | `admin123` |
| Doctor | `dr.sarah@clinic.com` | `doctor123` |
| Doctor | `dr.mohamed@clinic.com` | `doctor123` |
| Doctor | `dr.layla@clinic.com` | `doctor123` |
| Doctor | `dr.omar@clinic.com` | `doctor123` |
| Patient | `patient@test.com` | `patient123` |

---

## 🗂️ Project Structure

```text
medbook-doctor-booking/
│
├── app.py                  # Application factory, blueprint registration, seed data
├── models.py               # SQLAlchemy ORM models (User, Doctor, TimeSlot, Appointment, Payment, Review)
├── extensions.py           # Flask extension instances (db, login_manager, bcrypt, mail)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Register, login, logout, profile
│   ├── patient.py          # Dashboard, booking, payment, reviews, cancellation
│   ├── doctor.py           # Dashboard, schedule, appointment actions
│   ├── admin.py            # User management, doctor management, all appointments
│   ├── payment.py          # Checkout, confirm, success, cancel pages
│   ├── main.py             # Homepage, doctor listing, public reviews page
│   └── consultation.py     # Video consultation join/details
│
├── templates/
│   ├── index.html          # Homepage with doctor cards and hero section
│   ├── reviews.html        # Public reviews page with live filtering
│   ├── doctor_profile.html # Individual doctor profile with slots
│   ├── 404.html / 403.html # Error pages
│   ├── auth/               # login.html, register.html, profile.html
│   ├── patient/            # dashboard.html, book.html, review.html, appointment_detail.html
│   ├── doctor/             # dashboard.html, schedule.html, appointments.html
│   ├── admin/              # dashboard.html, users.html, doctors.html, appointments.html
│   ├── payment/            # checkout.html, success.html, cancel.html, history.html
│   └── consultation/       # join.html, details.html
│
├── static/
│   ├── css/
│   │   └── style.css       # Full design system with CSS variables and dark theme
│   ├── js/
│   │   └── main.js         # Interactivity: slot picker, search filters, form validation
│   └── img/
│       ├── MEDBook.png     # Logo
│       └── doctor_img.jpeg # Hero illustration
│
└── instance/
    └── doctor_booking.db   # SQLite database (auto-created, git-ignored)
```

---

## 🗄️ Database Schema

```text
users ──────────────────────────────────────────────────────────┐
  id, name, email [unique], password_hash, role,                │
  phone, is_active, created_at                                  │
       │ 1                                                       │
       │ 0..1                                                    │
doctors ────────────────────────────────────────────────────────┤
  id, user_id (FK), specialization, fee, rating,               │
  total_reviews, years_experience, is_available                 │
       │ 1                                                       │
       ├──── * time_slots                                        │
       │       id, doctor_id (FK), date, start_time,            │
       │       end_time, is_available                            │
       │                │ 0..1                                   │
       └──── * appointments ◄──────────────────────────────────┘
               id, patient_id (FK→users), doctor_id (FK),
               time_slot_id (FK), status, payment_status,
               notes, doctor_notes, meeting_link
                    │ 1
                    ├──── 0..1 payments
                    │       id, user_id (FK), appointment_id (FK),
                    │       amount, payment_status, payment_date
                    │
                    └──── 0..1 reviews
                            id, patient_id (FK), doctor_id (FK),
                            appointment_id (FK), rating, comment
```

---

## 🧪 Test Coverage

All 32 test cases pass covering:

| Category | Tests |
|---|---|
| Authentication (register, login, validation) | TC01 – TC08 |
| Doctor & slot management | TC09 – TC11 |
| Booking flow (slot picker, conflict detection) | TC12 – TC15 |
| Payment flow (checkout, confirm, cancel, re-pay guard) | TC16 – TC19 |
| Dashboards (appointments, empty state, cancellation) | TC20 – TC22 |
| Doctor workflow (approve, complete, review trigger) | TC23 – TC25 |
| Reviews page (submit, filter, Reviewed badge) | TC25 – TC26 |
| Security (RBAC, URL tampering, double-booking) | TC27 – TC32 |

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Flask session secret key |
| `DATABASE_URL` | ✅ | `sqlite:///doctor_booking.db` | Database connection string |
| `STRIPE_PUBLISHABLE_KEY` | ❌ | — | Stripe public key for frontend |
| `STRIPE_SECRET_KEY` | ❌ | — | Stripe secret key for backend |
| `STRIPE_WEBHOOK_SECRET` | ❌ | — | Stripe webhook verification |
| `MAIL_SERVER` | ❌ | `smtp.gmail.com` | SMTP server for email notifications |
| `MAIL_PORT` | ❌ | `587` | SMTP port |
| `MAIL_USERNAME` | ❌ | — | Email sender address |
| `MAIL_PASSWORD` | ❌ | — | Email app password |
| `BASE_URL` | ❌ | `http://localhost:5000` | Base URL for links in emails |

---

## 🔄 Switching to MySQL (Production)

1. Install the MySQL driver:

```bash
pip install PyMySQL
```

2. Update `.env`:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/medbook
```

3. Import the schema into MySQL using phpMyAdmin or the MySQL CLI, then run the app — SQLAlchemy will use the existing tables.

---

## 🛠️ Built With

| Technology | Version | Role |
|---|---|---|
| Flask | 3.0.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM / database layer |
| Flask-Login | 0.6.3 | Session management |
| Flask-Bcrypt | 1.0.1 | Password hashing |
| Flask-Mail | 0.10.0 | Email notifications |
| Stripe SDK | 10.5.0 | Payment processing |
| python-dotenv | 1.0.1 | Environment configuration |
| SQLAlchemy | 2.0.31 | SQL toolkit |
| Werkzeug | 3.0.3 | WSGI utilities |
| Jinja2 | Flask built-in | HTML templating |


---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
</div>
