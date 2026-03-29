from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.database import get_db
from app.services import admission_service


def _check_admin(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def _check_auth(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


router = APIRouter(prefix="/programs", tags=["Program & Quota Management"])

@router.post("/", response_model=schemas.ProgramResponse)
def create_program(program_data: schemas.ProgramCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a program along with its quotas.
    Enforces Rule: Total base quota must = intake.
    """
    _check_admin(request)
    return admission_service.create_program_with_quotas(db, program_data)

@router.get("/", response_model=List[schemas.ProgramResponse])
def get_programs(request: Request, db: Session = Depends(get_db)):
    _check_auth(request)
    from app.models import Program
    return db.query(Program).all()
