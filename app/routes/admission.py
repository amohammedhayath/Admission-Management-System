from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal
from app.services import admission_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/allocate-seat/{applicant_id}")
def allocate_seat(applicant_id: int, db: Session = Depends(get_db)):
    try:
        admission = admission_service.allocate_seat(db, applicant_id)
        return {
            "message": "Seat allocated successfully",
            "admission_id": admission.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/update-fee/{applicant_id}")
def update_fee(applicant_id: int, db: Session = Depends(get_db)):
    admission = db.query(models.Admission).filter(
        models.Admission.applicant_id == applicant_id
    ).first()

    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    admission.fee_status = "Paid" #type: ignore
    db.commit()

    return {"message": "Fee updated to Paid"}

@router.post("/confirm-admission/{applicant_id}")
def confirm_admission(applicant_id: int, db: Session = Depends(get_db)):
    try:
        admission = admission_service.confirm_admission(db, applicant_id)
        return {
            "message": "Admission confirmed",
            "admission_number": admission.admission_number
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
