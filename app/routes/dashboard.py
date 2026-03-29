from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models
from app.database import get_db

router = APIRouter(prefix="/dashboard", tags=["Management Dashboard"])

@router.get("/stats")
def get_dashboard_stats(request: Request, institution_id: int = None, db: Session = Depends(get_db)):
    """Returns dashboard statistics, optionally filtered by institution. Requires user to be logged in."""
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Build list of program IDs filtered by institution
    def institution_program_ids():
        query = db.query(models.Program).join(models.Department)
        if institution_id:
            return [p.id for p in query.filter(models.Department.institution_id == institution_id).all()]
        return [p.id for p in query.all()]

    program_ids = institution_program_ids()

    # 1. Overview Stats (filtered by institution if provided)
    total_intake = db.query(func.sum(models.Program.intake)).filter(models.Program.id.in_(program_ids)).scalar() or 0
    total_allocated = db.query(models.Admission).filter(models.Admission.program_id.in_(program_ids)).count()
    total_confirmed = db.query(models.Admission).filter(
        models.Admission.program_id.in_(program_ids),
        models.Admission.is_confirmed == True
    ).count()
    remaining_seats = max(0, total_intake - total_allocated)

    # 2. Quota-wise Stats (filtered by institution)
    quota_stats = []
    if institution_id:
        quotas = db.query(models.Quota).join(models.Program).join(models.Department).filter(
            models.Department.institution_id == institution_id
        ).all()
    else:
        quotas = db.query(models.Quota).all()

    for q in quotas:
        filled = db.query(models.Admission).filter(
            models.Admission.program_id == q.program_id,
            models.Admission.quota_type == q.quota_type
        ).count()
        prog_name = q.program.name if q.program else "Unknown Program"
        inst_name = q.program.department.institution.name if (
            q.program and q.program.department and q.program.department.institution
        ) else "Unknown"

        quota_stats.append({
            "program": prog_name,
            "institution": inst_name,
            "quota_type": q.quota_type,
            "total_seats": q.total_seats,
            "filled": filled,
            "remaining": max(0, q.total_seats - filled)
        })

    # 3. Action Required (Pending Docs & Fees) — filtered by institution
    if institution_id:
        pending_docs = db.query(models.Applicant).filter(
            models.Applicant.document_status == "Pending",
            models.Applicant.program_id.in_(program_ids)
        ).all()
        pending_fees = db.query(models.Admission).filter(
            models.Admission.fee_status == "Pending",
            models.Admission.program_id.in_(program_ids)
        ).all()
    else:
        pending_docs = db.query(models.Applicant).filter(models.Applicant.document_status == "Pending").all()
        pending_fees = db.query(models.Admission).filter(models.Admission.fee_status == "Pending").all()

    pending_docs_list = [{"name": a.name, "program": a.program.name if a.program else "Unknown"} for a in pending_docs]
    pending_fees_list = [{
        "applicant_name": adm.applicant.name if adm.applicant else "Unknown",
        "program": adm.program.name if adm.program else "Unknown",
        "admission_id": adm.id
    } for adm in pending_fees]

    # 4. Candidate Details — filtered by institution
    if institution_id:
        recent_applicants = db.query(models.Applicant).filter(
            models.Applicant.program_id.in_(program_ids)
        ).order_by(models.Applicant.created_at.desc()).all()
    else:
        recent_applicants = db.query(models.Applicant).order_by(models.Applicant.created_at.desc()).all()

    candidate_list = []
    for app in recent_applicants:
        status = "Registered"
        adm_no = "N/A"

        if app.admission:
            if app.admission.is_confirmed:
                status = "Confirmed"
                adm_no = app.admission.admission_number
            else:
                status = "Seat Allocated"

        candidate_list.append({
            "id": app.id,
            "name": app.name,
            "program": app.program.name if app.program else "Unknown",
            "institution": app.program.department.institution.name if (
                app.program and app.program.department and app.program.department.institution
            ) else "Unknown",
            "quota": app.quota_type,
            "status": status,
            "admission_number": adm_no
        })

    return {
        "overview": {
            "total_intake": total_intake,
            "total_allocated": total_allocated,
            "total_confirmed_admissions": total_confirmed,
            "remaining_seats": remaining_seats
        },
        "quota_wise_status": quota_stats,
        "pending_documents": pending_docs_list,
        "pending_fees": pending_fees_list,
        "candidates": candidate_list
    }

@router.get("/institutions")
def get_dashboard_institutions(request: Request, db: Session = Depends(get_db)):
    """Returns institutions for the dashboard filter dropdown."""
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return db.query(models.Institution).all()
