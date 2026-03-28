'''Imports'''
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


# -------------------- Program --------------------
class Program(Base):
    '''Program model representing an academic program.'''
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., CSE
    course_type = Column(String, nullable=False)  # UG / PG
    intake = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    quotas = relationship("Quota", back_populates="program")
    applicants = relationship("Applicant", back_populates="program")
    admissions = relationship("Admission", back_populates="program")


# -------------------- Quota --------------------
class Quota(Base):
    '''Quota model representing seat allocation for a program.'''
    __tablename__ = "quotas"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    quota_type = Column(String, nullable=False)  # KCET / COMEDK / Management
    total_seats = Column(Integer, nullable=False)

    program = relationship("Program", back_populates="quotas")


# -------------------- Applicant --------------------
class Applicant(Base):
    '''Applicant model representing a student applying for admission.'''
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    category = Column(String)  # GM / SC / ST
    marks = Column(Integer)

    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    quota_type = Column(String, nullable=False)

    document_status = Column(String, default="Pending")  # Pending / Verified
    created_at = Column(DateTime, default=datetime.utcnow)

    program = relationship("Program", back_populates="applicants")
    admission = relationship("Admission", back_populates="applicant", uselist=False)


# -------------------- Admission --------------------
class Admission(Base):
    '''Admission model representing the admission details of an applicant.'''
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, index=True)

    applicant_id = Column(Integer, ForeignKey("applicants.id"), unique=True, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)

    quota_type = Column(String, nullable=False)

    admission_number = Column(String, unique=True)

    fee_status = Column(String, default="Pending")  # Pending / Paid
    is_confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    applicant = relationship("Applicant", back_populates="admission")
    program = relationship("Program", back_populates="admissions")
