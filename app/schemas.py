from pydantic import BaseModel
from typing import List


# -------- Program --------
class ProgramCreate(BaseModel):
    name: str
    course_type: str
    intake: int


class ProgramResponse(BaseModel):
    id: int
    name: str
    course_type: str
    intake: int

    class Config:
        from_attributes = True


# -------- Quota --------
class QuotaCreate(BaseModel):
    quota_type: str
    total_seats: int


class ProgramWithQuotas(BaseModel):
    program: ProgramCreate
    quotas: List[QuotaCreate]

# -------- Applicant --------
class ApplicantCreate(BaseModel):
    name: str
    email: str
    phone: str
    category: str
    marks: int
    program_id: int
    quota_type: str


class ApplicantResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    category: str
    marks: int
    program_id: int
    quota_type: str
    document_status: str

    class Config:
        from_attributes = True
