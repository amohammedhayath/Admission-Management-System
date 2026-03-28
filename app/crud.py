from sqlalchemy.orm import Session
from app import models, schemas


def create_program_with_quotas(db: Session, data: schemas.ProgramWithQuotas):
    # Create Program
    program = models.Program(
        name=data.program.name,
        course_type=data.program.course_type,
        intake=data.program.intake
    )
    db.add(program)
    db.commit()
    db.refresh(program)

    # Validate quota sum
    total_quota = sum(q.total_seats for q in data.quotas)

    if total_quota != program.intake:
        raise ValueError("Total quota seats must equal program intake")

    # Create quotas
    for q in data.quotas:
        quota = models.Quota(
            program_id=program.id,
            quota_type=q.quota_type,
            total_seats=q.total_seats
        )
        db.add(quota)

    db.commit()
    return program

def create_applicant(db: Session, data: schemas.ApplicantCreate):
    # Check program exists
    program = db.query(models.Program).filter(models.Program.id == data.program_id).first()
    if not program:
        raise ValueError("Program not found")

    # Check quota exists for that program
    quota = db.query(models.Quota).filter(
        models.Quota.program_id == data.program_id,
        models.Quota.quota_type == data.quota_type
    ).first()

    if not quota:
        raise ValueError("Invalid quota for selected program")

    # Create applicant
    applicant = models.Applicant(
        name=data.name,
        email=data.email,
        phone=data.phone,
        category=data.category,
        marks=data.marks,
        program_id=data.program_id,
        quota_type=data.quota_type
    )

    db.add(applicant)
    db.commit()
    db.refresh(applicant)

    return applicant
