from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db


def _check_auth(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def _check_officer_or_admin(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") not in ("admin", "officer"):
        raise HTTPException(status_code=403, detail="Officer or Admin access required")
    return user


router = APIRouter(prefix="/applicants", tags=["Applicant Management"])

@router.post("/", response_model=schemas.ApplicantResponse)
def create_applicant(applicant: schemas.ApplicantCreate, request: Request, db: Session = Depends(get_db)):
    """Creates a new applicant linked to a program with strict capacity checks."""
    _check_officer_or_admin(request)
    # 1. Check if Program exists
    program = db.query(models.Program).filter(models.Program.id == applicant.program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail=f"Program with ID {applicant.program_id} does not exist.")

    # 2. Check if Quota exists
    quota = db.query(models.Quota).filter(
        models.Quota.program_id == applicant.program_id,
        models.Quota.quota_type == applicant.quota_type
    ).first()
    
    if not quota:
        raise HTTPException(status_code=400, detail=f"Invalid Quota type for this program.")

    # --- Government Flow Validation: Require Allotment Number ---
    if applicant.quota_type in ("KCET", "COMEDK") and not applicant.allotment_number:
        raise HTTPException(
            status_code=400,
            detail=f"Allotment number is required for {applicant.quota_type} quota."
        )

    # --- 3. Check for Duplicate Allotment Number ---
    if applicant.allotment_number:
        existing_app = db.query(models.Applicant).filter(
            models.Applicant.allotment_number == applicant.allotment_number
        ).first()
        if existing_app:
            raise HTTPException(
                status_code=400,
                detail=f"Allotment number '{applicant.allotment_number}' is already registered to another applicant."
            )

    # 4. STRICT RULE: Block Registration if Quota is already completely full
    allocated_count = db.query(models.Admission).filter(
        models.Admission.program_id == applicant.program_id,
        models.Admission.quota_type == applicant.quota_type
    ).count()
    
    if allocated_count >= quota.total_seats:
        raise HTTPException(
            status_code=400, 
            detail=f"Registration Blocked: The {applicant.quota_type} quota for {program.name} is currently FULL ({allocated_count}/{quota.total_seats} seats filled)."
        )

    # 4. Save Applicant
    db_applicant = models.Applicant(**applicant.model_dump())
    db.add(db_applicant)
    db.commit()
    db.refresh(db_applicant)
    return db_applicant

@router.get("/", response_model=List[schemas.ApplicantResponse])
def get_applicants(request: Request, db: Session = Depends(get_db)):
    _check_auth(request)
    return db.query(models.Applicant).all()

@router.patch("/{applicant_id}/documents", response_model=schemas.ApplicantResponse)
def update_document_status(applicant_id: int, doc_update: schemas.ApplicantUpdateDocs, request: Request, db: Session = Depends(get_db)):
    """Updates the document verification status with duplicate protection."""
    _check_officer_or_admin(request)
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # STRICT RULE: Prevent double verification
    if applicant.document_status == "Verified" and doc_update.document_status == "Verified":
        raise HTTPException(status_code=400, detail="Documents are already verified for this applicant.")

    applicant.document_status = doc_update.document_status
    db.commit()
    db.refresh(applicant)
    return applicant
