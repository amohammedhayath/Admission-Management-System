# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack
- FastAPI (Backend API framework)
- SQLite (Database) via SQLAlchemy ORM
- Jinja2 + Bootstrap (Frontend templates)

## Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (auto-reloads on changes)
uvicorn app.main:app --reload

# API documentation (Swagger UI)
http://127.0.0.1:8000/docs

# Dashboard UI
http://127.0.0.1:8000/dashboard
```

## Architecture

### Entity Hierarchy
```
Institution → Department → Program → Quota
                              ↘ Applicant → Admission
```

### Admission Workflow
1. **Setup**: Create Institution, Department, AcademicYear via `/setup/*` endpoints
2. **Program**: Create Program with Quotas (total quota seats must equal intake) via `/programs`
3. **Applicant**: Register applicant with quota type via `/applicants`
4. **Allocation**: Allocate seat via `/admissions/allocate/{applicant_id}` (quota capacity enforced)
5. **Fee**: Update fee status via `PATCH /admissions/{id}/fee`
6. **Documents**: Verify documents via `PATCH /applicants/{id}/documents`
7. **Confirm**: Confirm admission via `/admissions/{id}/confirm` (generates admission number)

### Key Files
- `app/services/admission_service.py` — Core business logic (seat allocation, admission confirmation, admission number generation)
- `app/database.py` — SQLAlchemy engine and session setup
- `app/models.py` — SQLAlchemy ORM models
- `app/schemas.py` — Pydantic request/response schemas
- `app/routes/` — API route handlers (program, applicant, admission, dashboard, setup)

### Admission Number Format
`INST/2026/UG/CSE/KCET/0001` — constructed from Institution code, AcademicYear, course type, program name, quota type, and sequence number.

### Business Rules
- Total quota seats must equal program intake
- No duplicate allotment numbers
- No seat allocation if quota is full (checked dynamically)
- Admission confirmed only when fee="Paid" AND document_status="Verified"
- Fee and document status cannot be modified after admission confirmation
