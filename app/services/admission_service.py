from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app import models, schemas

# -------------------- Program & Quota Logic --------------------

def create_program_with_quotas(db: Session, program_data: schemas.ProgramCreate):
    """
    Creates a program and its quotas.
    Enforces Rule: Total base quota must = intake.
    """
    try:
        total_quota_seats = sum(q.total_seats for q in program_data.quotas)

        if total_quota_seats != program_data.intake:
            raise HTTPException(
                status_code=400,
                detail=f"Total quota seats ({total_quota_seats}) must equal program intake ({program_data.intake})."
            )

        # 1. Create Program
        new_program = models.Program(
            name=program_data.name,
            department_id=program_data.department_id,
            academic_year_id=program_data.academic_year_id,
            course_type=program_data.course_type,
            intake=program_data.intake
        )
        db.add(new_program)
        db.commit()
        db.refresh(new_program)

        # 2. Create Quotas
        for quota_data in program_data.quotas:
            new_quota = models.Quota(
                program_id=new_program.id,
                quota_type=quota_data.quota_type,
                total_seats=quota_data.total_seats
            )
            db.add(new_quota)

        db.commit()
        db.refresh(new_program)
        return new_program
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating program.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error while creating program.")


# -------------------- Seat Allocation Logic --------------------

def allocate_seat(db: Session, applicant_id: int):
    """
    Allocates a seat dynamically.
    Enforces Rule: No seat allocation if quota full.
    Uses SELECT FOR UPDATE to prevent race conditions.
    """
    try:
        applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
        if not applicant:
            raise HTTPException(status_code=404, detail="Applicant not found")

        # Check if applicant already has a seat
        existing_admission = db.query(models.Admission).filter(models.Admission.applicant_id == applicant_id).first()
        if existing_admission:
            raise HTTPException(status_code=400, detail="Applicant already has an allocated seat.")

        # Lock the quota row to prevent concurrent over-allocation
        quota = db.query(models.Quota).filter(
            models.Quota.program_id == applicant.program_id,
            models.Quota.quota_type == applicant.quota_type
        ).with_for_update().first()

        if not quota:
            raise HTTPException(status_code=404, detail=f"Quota {applicant.quota_type} not configured for this program.")

        # Dynamic Seat Counter: Count current allocations for this program + quota
        allocated_count = db.query(models.Admission).filter(
            models.Admission.program_id == applicant.program_id,
            models.Admission.quota_type == applicant.quota_type
        ).count()

        # Block allocation if full
        if allocated_count >= quota.total_seats:
            raise HTTPException(
                status_code=400,
                detail=f"Quota full. {allocated_count}/{quota.total_seats} seats already allocated for {applicant.quota_type}."
            )

        # Allocate Seat (Pending Confirmation)
        new_admission = models.Admission(
            applicant_id=applicant.id,
            program_id=applicant.program_id,
            quota_type=applicant.quota_type
        )
        db.add(new_admission)
        db.commit()
        db.refresh(new_admission)
        return new_admission
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during seat allocation.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error during seat allocation.")


# -------------------- Admission Confirmation Logic --------------------

def confirm_admission(db: Session, admission_id: int):
    """
    Confirms admission and generates the unique admission number.
    Enforces Rule: Admission confirmed only if fee paid & docs verified.
    Uses SELECT FOR UPDATE to prevent race conditions in sequence generation.
    """
    try:
        admission = db.query(models.Admission).filter(models.Admission.id == admission_id).with_for_update().first()
        if not admission:
            raise HTTPException(status_code=404, detail="Admission record not found")

        if admission.is_confirmed:
            raise HTTPException(status_code=400, detail="Admission is already confirmed.")

        applicant = admission.applicant
        program = admission.program

        # Validation Checks
        if admission.fee_status != "Paid":
            raise HTTPException(status_code=400, detail="Cannot confirm: Fee is not paid.")

        if applicant.document_status != "Verified":
            raise HTTPException(status_code=400, detail="Cannot confirm: Documents are not verified.")

        # Generate Admission Number (Format: INST/2026/UG/CSE/KCET/0001)
        # 1. Fetch related master data
        academic_year = db.query(models.AcademicYear).filter(models.AcademicYear.id == program.academic_year_id).first()
        if not academic_year:
            raise HTTPException(status_code=400, detail="Program has no associated academic year.")
        department = db.query(models.Department).filter(models.Department.id == program.department_id).first()
        if not department:
            raise HTTPException(status_code=400, detail="Program has no associated department.")
        institution = db.query(models.Institution).filter(models.Institution.id == department.institution_id).first()
        if not institution:
            raise HTTPException(status_code=400, detail="Department has no associated institution.")

        # 2. Get sequence number (Count confirmed admissions in this program + 1)
        sequence_count = db.query(models.Admission).filter(
            models.Admission.program_id == program.id,
            models.Admission.is_confirmed == True
        ).count() + 1

        sequence_str = f"{sequence_count:04d}" # Pads with zeros to make it 4 digits (e.g., 0001)

        # 3. Construct the immutable string
        adm_number = f"{institution.code}/{academic_year.year}/{program.course_type}/{program.name}/{admission.quota_type}/{sequence_str}"

        admission.admission_number = adm_number
        admission.is_confirmed = True

        db.commit()
        db.refresh(admission)
        return admission
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during admission confirmation.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error during admission confirmation.")
