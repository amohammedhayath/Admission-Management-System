# Admission Management System

## Overview

The **Admission Management System** is a backend-driven web application built using **FastAPI** that streamlines and automates the college admission process.

It allows institutions to:

* Configure academic programs and quota distribution
* Manage applicants efficiently
* Allocate seats with strict rule enforcement
* Validate and confirm admissions
* Monitor real-time admission insights via a dashboard

---

## Tech Stack

* **Backend:** FastAPI
* **Database:** SQLite (easily portable to PostgreSQL)
* **ORM:** SQLAlchemy
* **Frontend:** Jinja2 Templates + Bootstrap
* **Server:** Uvicorn

---

## Core Features

### Program & Quota Management

* Create programs with defined total intake
* Configure quota distribution (e.g., General, KCET, Management)
* Ensures:

  * Total quota equals program intake
  * No misconfiguration allowed

---

### Applicant Management

* Register applicants mapped to specific programs
* Validate quota selection based on program configuration
* Track document verification status

---

### Seat Allocation

* Allocate seats based on real-time quota availability
* Prevents:

  * Duplicate allocations
  * Quota overflow
* Uses dynamic validation instead of static counters

---

### Admission Confirmation

Admission is confirmed only when:

* Fee status = **Paid**

* Documents = **Verified**

* Generates a unique, immutable admission number:

  ```
  INST/2026/UG/CSE/KCET/0001
  ```

---

### Dashboard

Accessible at `/dashboard`

Provides:

* Total intake vs admitted students
* Remaining seats
* Program-wise quota utilization
* Pending:

  * Document verifications
  * Fee payments

---

## Business Rules Enforced

* No seat overbooking
* Strict quota-wise seat allocation
* One applicant → one admission
* Admission number is unique & immutable
* Admission confirmation only after all validations

---

## Key Design Decisions

### 1. Simplified Domain Model

Core entities:

* **Program**
* **Quota**
* **Applicant**
* **Admission**

Focused on clarity and core workflow rather than over-engineering.

---

### 2. Dynamic Seat Validation

* Seat availability is computed in real-time from admission records
* Avoids inconsistencies caused by stored counters

---

### 3. Controlled Admission Workflow

The system enforces a strict step-by-step process:

1. Applicant creation
2. Seat allocation
3. Document verification
4. Fee update
5. Admission confirmation

---

### 4. Lightweight Database Choice

* SQLite used for simplicity and quick setup
* Schema designed to be production-ready and portable to PostgreSQL

---

## Project Structure

```
app/
├── main.py                # FastAPI entry point
├── database.py            # DB connection setup
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── routes/                # API routes
│   ├── applicant.py
│   ├── admission.py
│   ├── dashboard.py
│   ├── program.py
│   └── setup.py
├── services/              # Business logic layer
│   └── admission_service.py
├── templates/             # UI templates
│   ├── admissions.html
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   └── setup.html
```

---

## 🛠️ Setup Instructions

```bash
# Clone repository
git clone https://github.com/amohammedhayath/Admission-Management-System
cd Admission-Management-System

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

---

## ▶️ How to Use

### 🔹 API Documentation

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

### 🔹 End-to-End Workflow

1. Create Program & Quotas → `/programs`
2. Register Applicant → `/applicants`
3. Allocate Seat → `/allocate-seat/{applicant_id}`
4. Verify Documents → `/verify-documents/{applicant_id}`
5. Update Fee Status → `/update-fee/{applicant_id}`
6. Confirm Admission → `/confirm-admission/{applicant_id}`

---

### 🔹 Dashboard View

```
http://127.0.0.1:8000/dashboard
```

---

## 🧪 Validation Highlights

* Real-time quota enforcement
* Strong input validation using Pydantic
* Clean separation of concerns (routes vs services)
* Error handling for invalid workflows

---

## 🔮 Future Enhancements

* 🔐 Authentication & role-based access (Admin/User)
* 📧 Email notifications for admission status
* 💳 Payment gateway integration
* 📈 Advanced analytics dashboard
* 🐘 PostgreSQL production deployment
* 🌐 REST client frontend (React / Vue)

---

## 🤖 AI Usage Disclosure

AI tools were used for:

* Backend architecture suggestions
* Code structuring and optimization
* Logic validation

All generated outputs were:

* Carefully reviewed
* Fully understood
* Manually tested before integration

---

## AI Usage Disclosure

AI tools were used to:

* Assist in backend architecture design
* Improve code organization
* Validate logic implementation

All outputs were reviewed, tested, and understood before use.

---

## Summary

This project demonstrates:

* Real-world backend system design
* Business rule enforcement
* Clean architecture practices
* FastAPI-based API development

It is designed to be **simple, scalable, and production-adaptable**.
