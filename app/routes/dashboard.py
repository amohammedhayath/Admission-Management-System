from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from app.database import SessionLocal
from app import models

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    # Total intake
    programs = db.query(models.Program).all()
    total_intake = sum(p.intake for p in programs)

    # Total admitted
    total_admitted = db.query(models.Admission).count()

    # Quota-wise grouped by program
    quota_summary = []

    for program in programs:
        quotas = db.query(models.Quota).filter(
            models.Quota.program_id == program.id
        ).all()

        quota_list = []

        for quota in quotas:
            filled = db.query(models.Admission).filter(
                models.Admission.program_id == program.id,
                models.Admission.quota_type == quota.quota_type
            ).count()

            quota_list.append({
                "quota_type": quota.quota_type,
                "filled": filled,
                "total": quota.total_seats
            })

        quota_summary.append({
            "program": program.name,
            "quotas": quota_list
        })
    # Pending documents
    pending_docs = db.query(models.Applicant).filter(
        models.Applicant.document_status == "Pending"
    ).count()

    # Pending fees
    pending_fees = db.query(models.Admission).filter(
        models.Admission.fee_status == "Pending"
    ).count()

    return templates.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={
        "request": request,
        "total_intake": total_intake,
        "total_admitted": total_admitted,
        "remaining_seats": total_intake - total_admitted,
        "quota_summary": quota_summary,
        "pending_docs": pending_docs,
        "pending_fees": pending_fees
    }
)
