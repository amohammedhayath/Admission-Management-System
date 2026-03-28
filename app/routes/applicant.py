from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal
from app import schemas, crud

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/applicants")
def create_applicant(data: schemas.ApplicantCreate, db: Session = Depends(get_db)):
    try:
        applicant = crud.create_applicant(db, data)
        return {"message": "Applicant created", "applicant_id": applicant.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/verify-documents/{applicant_id}")
def verify_documents(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.query(models.Applicant).filter(
        models.Applicant.id == applicant_id
    ).first()

    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    applicant.document_status = "Verified" #type: ignore
    db.commit()

    return {"message": "Documents verified"}
