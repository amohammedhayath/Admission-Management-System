from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import schemas, crud

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/programs")
def create_program(data: schemas.ProgramWithQuotas, db: Session = Depends(get_db)):
    try:
        program = crud.create_program_with_quotas(db, data)
        return {"message": "Program created successfully", "program_id": program.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
