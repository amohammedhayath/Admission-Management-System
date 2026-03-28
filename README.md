
# Admission Management System

## 📌 Overview
This is a simplified Admission Management System built as part of a take-home assignment.

The system enables colleges to:
- Configure programs and quota distribution
- Manage applicants
- Allocate seats with strict quota enforcement
- Confirm admissions with validation rules
- Monitor admissions through a dashboard

---

## 🚀 Tech Stack
- FastAPI (Backend)
- SQLite (Database)
- SQLAlchemy ORM
- Jinja2 + Bootstrap (UI)

---

## ⚙️ Features

### 1. Program & Quota Management
- Create programs with defined intake
- Configure quota distribution per program
- Enforces: total quota must equal intake

---

### 2. Applicant Management
- Create applicants linked to a program
- Validate quota selection per program
- Track document verification status

---

### 3. Seat Allocation  
- Allocate seats based on quota availability
- Prevents:
  - Duplicate allocation
  - Quota overflow

---

### 4. Admission Confirmation
- Admission is confirmed only when:
  - Fee is marked as **Paid**
  - Documents are **Verified**
- Generates unique admission number:


> INST/2026/UG/CSE/KCET/0001


---

### 5. Dashboard
- Total intake vs admitted
- Remaining seats
- Program-wise quota status (filled vs total)
- Pending documents and fees

---

## 🔒 Business Rules Enforced
- No seat overbooking
- Quota-wise seat control
- One applicant → one admission
- Admission number is unique and immutable
- Admission confirmation only after fee payment and document verification

---

## 🧠 Design Decisions

### Simplified Data Model
Entities used:
- Program
- Quota
- Applicant
- Admission

Focused on core workflow instead of over-engineering hierarchy.

---

### Dynamic Seat Validation
Seat availability is calculated dynamically using admission records instead of storing counters to avoid inconsistency.

---

### Controlled Admission Flow
Process is split into:
1. Applicant creation
2. Seat allocation
3. Fee update
4. Document verification
5. Admission confirmation

---

### SQLite Usage
Chosen for faster setup and simplicity for assignment scope.  
Schema is portable to PostgreSQL.

---


---



## 📁 Project Structure

````
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── routes/
│   ├── program.py
│   ├── applicant.py
│   ├── admission.py
│   ├── dashboard.py
├── services/
│   └── admission_service.py
├── templates/
│   └── dashboard.html
````


## 🛠️ Setup Instructions

```bash
git clone <your-repo-link>
cd admission-management-system

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

uvicorn app.main:app --reload
````

---

## ▶️ Working Demo (Local)

### Step 1: Open API Docs

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Step 2: Test Flow

1. Create Program + Quotas (`/programs`)
2. Create Applicant (`/applicants`)
3. Allocate Seat (`/allocate-seat/{id}`)
4. Verify Documents (`/verify-documents/{id}`)
5. Update Fee (`/update-fee/{id}`)
6. Confirm Admission (`/confirm-admission/{id}`)

---

### Step 3: View Dashboard

[http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)

---

## 🤖 AI Usage Disclosure

AI tools were used to:

* Assist in backend architecture design
* Improve code organization
* Validate logic implementation

All outputs were reviewed, tested, and understood before use.
