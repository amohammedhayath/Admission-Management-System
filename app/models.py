from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base

# -------------------- Master Setup --------------------

class Institution(Base):
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True) # e.g., 'INST' for admission number

    departments = relationship("Department", back_populates="institution")

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)

    institution = relationship("Institution", back_populates="departments")
    programs = relationship("Program", back_populates="department")

    __table_args__ = (
        UniqueConstraint('name', 'institution_id', name='uq_department_name_institution'),
    )

class AcademicYear(Base):
    __tablename__ = "academic_years"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(String, nullable=False, unique=True) # e.g., '2026'
    is_active = Column(Boolean, default=True)

    programs = relationship("Program", back_populates="academic_year")

# -------------------- Core Admission Entities --------------------

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., CSE
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)

    course_type = Column(String, nullable=False)  # UG / PG
    intake = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="programs")
    academic_year = relationship("AcademicYear", back_populates="programs")
    quotas = relationship("Quota", back_populates="program", cascade="all, delete-orphan")
    applicants = relationship("Applicant", back_populates="program")
    admissions = relationship("Admission", back_populates="program")

class Quota(Base):
    __tablename__ = "quotas"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    quota_type = Column(String, nullable=False)  # KCET / COMEDK / Management
    total_seats = Column(Integer, nullable=False)

    program = relationship("Program", back_populates="quotas")

class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    category = Column(String, nullable=False)  # GM / SC / ST
    entry_type = Column(String, nullable=False) # Regular / Lateral
    marks = Column(Integer, nullable=False)

    # Required for Government Flow (KCET/COMEDK)
    allotment_number = Column(String, nullable=True, unique=True)

    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    quota_type = Column(String, nullable=False)

    document_status = Column(String, default="Pending")  # Pending / Submitted / Verified
    created_at = Column(DateTime, default=datetime.utcnow)

    program = relationship("Program", back_populates="applicants")
    admission = relationship("Admission", back_populates="applicant", uselist=False)

class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), unique=True, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    quota_type = Column(String, nullable=False)

    admission_number = Column(String, unique=True, nullable=True) # Generated on confirmation

    fee_status = Column(String, default="Pending")  # Pending / Paid
    is_confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    applicant = relationship("Applicant", back_populates="admission")
    program = relationship("Program", back_populates="admissions")
