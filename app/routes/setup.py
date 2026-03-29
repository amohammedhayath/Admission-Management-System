from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app import models, schemas
from app.database import get_db


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


router = APIRouter(prefix="/setup", tags=["Master Setup"])

# --- Institution ---
@router.post("/institution", response_model=schemas.InstitutionResponse)
def create_institution(data: schemas.InstitutionCreate, request: Request, db: Session = Depends(get_db)):
    _check_admin(request)
    try:
        db_obj = models.Institution(**data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Institution with this code already exists")

@router.get("/institutions", response_model=List[schemas.InstitutionResponse])
def get_institutions(request: Request, db: Session = Depends(get_db)):
    _check_auth(request)
    return db.query(models.Institution).all()

# --- Department ---
@router.post("/department", response_model=schemas.DepartmentResponse)
def create_department(data: schemas.DepartmentCreate, request: Request, db: Session = Depends(get_db)):
    _check_admin(request)
    # Validate institution exists
    inst = db.query(models.Institution).filter(models.Institution.id == data.institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    try:
        db_obj = models.Department(**data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Department '{data.name}' already exists in {inst.name}")

@router.get("/departments", response_model=List[schemas.DepartmentResponse])
def get_departments(request: Request, db: Session = Depends(get_db)):
    _check_auth(request)
    return db.query(models.Department).all()

# --- Academic Year ---
@router.post("/academic-year", response_model=schemas.AcademicYearResponse)
def create_academic_year(data: schemas.AcademicYearCreate, request: Request, db: Session = Depends(get_db)):
    _check_admin(request)
    try:
        db_obj = models.AcademicYear(**data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Academic year already exists")

@router.get("/academic-years", response_model=List[schemas.AcademicYearResponse])
def get_academic_years(request: Request, db: Session = Depends(get_db)):
    _check_auth(request)
    return db.query(models.AcademicYear).all()

@router.get("/academic-year/current", response_model=schemas.AcademicYearResponse)
def get_current_academic_year(request: Request, db: Session = Depends(get_db)):
    _check_auth(request)
    current = db.query(models.AcademicYear).order_by(models.AcademicYear.year.desc()).first()
    if not current:
        raise HTTPException(status_code=404, detail="No academic year found")
    return current

@router.get("/academic-year/current", response_model=schemas.AcademicYearResponse)
def get_or_create_current_year(request: Request, db: Session = Depends(get_db)):
    """Returns the current academic year, creating it if it doesn't exist."""
    _check_auth(request)
    import datetime
    current_year = str(datetime.datetime.now().year)
    year_obj = db.query(models.AcademicYear).filter(models.AcademicYear.year == current_year).first()
    if not year_obj:
        year_obj = models.AcademicYear(year=current_year, is_active=True)
        db.add(year_obj)
        db.commit()
        db.refresh(year_obj)
    return year_obj
