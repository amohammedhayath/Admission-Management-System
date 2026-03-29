from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db
from app.services import admission_service


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


router = APIRouter(prefix="/admissions", tags=["Admission & Seat Allocation"])

@router.post("/allocate/{applicant_id}", response_model=schemas.AdmissionResponse)
def allocate_seat_endpoint(applicant_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Allocates a seat dynamically based on the applicant's program and quota.
    Enforces Rule: No seat allocation if quota full.
    """
    _check_officer_or_admin(request)
    return admission_service.allocate_seat(db, applicant_id)

@router.patch("/{admission_id}/fee", response_model=schemas.AdmissionResponse)
def update_fee_status(admission_id: int, fee_update: schemas.AdmissionUpdateFee, request: Request, db: Session = Depends(get_db)):
    """Updates fee status with row-level locking to prevent race conditions."""
    _check_officer_or_admin(request)
    admission = db.query(models.Admission).filter(
        models.Admission.id == admission_id
    ).with_for_update().first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission record not found. Please allocate a seat first.")

    # STRICT RULE: Prevent modifying fee if admission is fully confirmed
    if admission.is_confirmed:
        raise HTTPException(status_code=400, detail="Cannot modify fee. Admission is already officially confirmed.")

    # STRICT RULE: Prevent duplicate payments
    if admission.fee_status == "Paid" and fee_update.fee_status == "Paid":
        raise HTTPException(status_code=400, detail="Fee has already been marked as Paid for this admission.")

    admission.fee_status = fee_update.fee_status
    db.commit()
    db.refresh(admission)
    return admission

@router.post("/{admission_id}/confirm", response_model=schemas.AdmissionResponse)
def confirm_admission_endpoint(admission_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Confirms admission and generates the unique admission number.
    Enforces Rule: Admission confirmed only if fee paid & docs verified.
    """
    _check_officer_or_admin(request)
    return admission_service.confirm_admission(db, admission_id)

@router.get("/", response_model=List[schemas.AdmissionResponse])
def get_all_admissions(request: Request, db: Session = Depends(get_db)):
    """Lists all admission records."""
    _check_auth(request)
    return db.query(models.Admission).all()
