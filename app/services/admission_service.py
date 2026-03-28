from sqlalchemy.orm import Session
from app import models
from datetime import datetime


def confirm_admission(db: Session, applicant_id: int):
    # Get admission
    admission = db.query(models.Admission).filter(
        models.Admission.applicant_id == applicant_id
    ).first()

    if not admission:
        raise ValueError("Seat not allocated for this applicant")

    # Check already confirmed
    if admission.is_confirmed: #type: ignore
        raise ValueError("Admission already confirmed")

    # Get applicant
    applicant = db.query(models.Applicant).filter(
        models.Applicant.id == applicant_id
    ).first()

    # Validate fee
    if admission.fee_status != "Paid": #type: ignore
        raise ValueError("Fee not paid")

    # Validate documents
    if applicant.document_status != "Verified": #type: ignore
        raise ValueError("Documents not verified")

    # Generate admission number
    year = datetime.now().year

    program = db.query(models.Program).filter(
        models.Program.id == admission.program_id
    ).first()

    # Count existing confirmed admissions for sequence
    count = db.query(models.Admission).filter(
        models.Admission.program_id == admission.program_id,
        models.Admission.quota_type == admission.quota_type,
        models.Admission.is_confirmed == True
    ).count()

    sequence = str(count + 1).zfill(4)

    admission_number = f"INST/{year}/{program.course_type}/{program.name}/{admission.quota_type}/{sequence}" #type: ignore

    # Update admission
    admission.admission_number = admission_number #type: ignore
    admission.is_confirmed = True #type: ignore

    db.commit()
    db.refresh(admission)

    return admission

def allocate_seat(db: Session, applicant_id: int):
    # Get applicant
    applicant = db.query(models.Applicant).filter(
        models.Applicant.id == applicant_id
    ).first()

    if not applicant:
        raise ValueError("Applicant not found")

    # Check if already allocated
    existing = db.query(models.Admission).filter(
        models.Admission.applicant_id == applicant_id
    ).first()

    if existing:
        raise ValueError("Seat already allocated to this applicant")

    # Get quota
    quota = db.query(models.Quota).filter(
        models.Quota.program_id == applicant.program_id,
        models.Quota.quota_type == applicant.quota_type
    ).first()

    if not quota:
        raise ValueError("Quota not found")

    # Count already allocated seats
    allocated_count = db.query(models.Admission).filter(
        models.Admission.program_id == applicant.program_id,
        models.Admission.quota_type == applicant.quota_type
    ).count()

    # Check seat availability
    if allocated_count >= quota.total_seats: #type: ignore
        raise ValueError("No seats available in this quota")

    # Create admission
    admission = models.Admission(
        applicant_id=applicant.id,
        program_id=applicant.program_id,
        quota_type=applicant.quota_type
    )

    db.add(admission)
    db.commit()
    db.refresh(admission)

    return admission
