from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import datetime

# -------- Enums --------

CourseType = Literal["UG", "PG"]
EntryType = Literal["Regular", "Lateral"]
CategoryType = Literal["GM", "SC", "ST", "OBC", "OTHER"]
QuotaType = Literal["KCET", "COMEDK", "Management"]
DocumentStatus = Literal["Pending", "Submitted", "Verified"]
FeeStatus = Literal["Pending", "Paid"]

# -------- Master Setup Schemas --------

class InstitutionBase(BaseModel):
    name: str
    code: str

class InstitutionCreate(InstitutionBase): pass

class InstitutionResponse(InstitutionBase):
    id: int
    class Config: from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    institution_id: int

class DepartmentCreate(DepartmentBase): pass

class DepartmentResponse(DepartmentBase):
    id: int
    class Config: from_attributes = True

class DepartmentWithInstitution(DepartmentBase):
    id: int
    institution: InstitutionResponse
    class Config: from_attributes = True

class AcademicYearBase(BaseModel):
    year: str
    is_active: bool = True

class AcademicYearCreate(AcademicYearBase): pass

class AcademicYearResponse(AcademicYearBase):
    id: int
    class Config: from_attributes = True

# -------- Program & Quota --------

class QuotaBase(BaseModel):
    quota_type: QuotaType
    total_seats: int

class QuotaCreate(QuotaBase): pass

class QuotaResponse(QuotaBase):
    id: int
    program_id: int
    class Config: from_attributes = True

class ProgramBase(BaseModel):
    name: str
    department_id: int
    academic_year_id: int
    course_type: CourseType = Field(..., description="UG or PG")
    intake: int

class ProgramCreate(ProgramBase):
    quotas: List[QuotaCreate]

class ProgramResponse(ProgramBase):
    id: int
    quotas: List[QuotaResponse] = []
    department: DepartmentWithInstitution
    class Config: from_attributes = True

# -------- Applicant --------

class ApplicantBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15, pattern=r"^\+?[\d\s\-]+$")
    category: CategoryType
    entry_type: EntryType
    marks: int = Field(..., ge=0, le=100)
    program_id: int
    quota_type: QuotaType
    allotment_number: Optional[str] = None

class ApplicantCreate(ApplicantBase): pass

class ApplicantResponse(ApplicantBase):
    id: int
    document_status: DocumentStatus
    created_at: datetime
    class Config: from_attributes = True

class ApplicantUpdateDocs(BaseModel):
    document_status: DocumentStatus

# -------- Admission --------

class AdmissionResponse(BaseModel):
    id: int
    applicant_id: int
    program_id: int
    quota_type: str
    admission_number: Optional[str]
    fee_status: str
    is_confirmed: bool
    created_at: datetime
    class Config: from_attributes = True

class AdmissionUpdateFee(BaseModel):
    fee_status: FeeStatus
