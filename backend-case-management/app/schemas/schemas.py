from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.core.security import is_valid_gov_email

CaseStatusType = Literal[
    "REQUESTED",
    "APPROVED",
    "ASSIGNED",
    "UNDER_INVESTIGATION",
    "EVIDENCE_SUBMITTED",
    "UNDER_REVIEW",
    "RESOLVED",
    "ESCALATED",
    "REJECTED",
    "ARCHIVED",
    "OPEN"
]

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="investigator.demo")
    email: EmailStr = Field(..., example="investigator.demo@civicshield.gov.in")
    full_name: Optional[str] = Field(None, max_length=100, example="Demo Investigator")
    role: Optional[str] = Field("investigator", example="investigator")

    @field_validator("email")
    @classmethod
    def validate_gov_email(cls, v: str) -> str:
        if not is_valid_gov_email(v):
            raise ValueError("Registration is restricted to authorized government/investigation domains (*.gov.in, *.nic.in, *.civicshield.gov.in).")
        return v.lower()


class UserCreate(UserBase):
    """Used by Admin to provision new Investigator accounts."""
    password: str = Field(..., min_length=8, max_length=72, example="CivicShield@Demo2026!")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None


# --- Case & Investigation Workflow Schemas ---

class CaseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    flagged_work_id: str = Field(..., description="ID of the flagged work, e.g., PRJ-2026-001 or MPL-UP-1042")
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    risk_level: Optional[str] = Field("MEDIUM", description="LOW, MEDIUM, or HIGH")
    flagged_reasons: Optional[str] = Field(None, description="Explainability reasons for why this project was flagged")
    recommended_action: Optional[str] = Field(None, description="Recommended review action")


class RequestInvestigation(BaseModel):
    """Investigator requests an investigation for a flagged project."""
    flagged_work_id: str
    title: str
    description: Optional[str] = None
    request_reason: str = Field(..., min_length=5, example="High burn rate and expenditure mismatch observed; field inspection required.")
    risk_score: float = 0.0
    risk_level: str = "HIGH"
    flagged_reasons: Optional[str] = None


class AdminAssignCase(BaseModel):
    """Admin directly assigns a project/case to an investigator."""
    flagged_work_id: str
    title: str
    investigator_id: int
    description: Optional[str] = None
    risk_score: float = 0.0
    risk_level: str = "HIGH"
    flagged_reasons: Optional[str] = None


class ApproveInvestigation(BaseModel):
    """Admin approves a requested investigation and assigns an investigator."""
    investigator_id: Optional[int] = None
    admin_notes: Optional[str] = None


class RejectInvestigation(BaseModel):
    """Admin rejects an investigation request."""
    rejection_reason: str = Field(..., min_length=3, example="Project already verified by TPI.")


class SubmitFieldEvidence(BaseModel):
    """Investigator submits on-site inspection findings, evidence photo, and GPS."""
    evidence_photo_url: Optional[str] = Field(None, description="URL or base64 data of captured site photograph")
    latitude: Optional[float] = Field(None, description="Genuine latitude captured from device/browser")
    longitude: Optional[float] = Field(None, description="Genuine longitude captured from device/browser")
    location_timestamp: Optional[datetime] = None
    site_condition: Optional[str] = Field(None, example="Roofing incomplete, foundation laid.")
    financial_observation: Optional[str] = Field(None, example="Reported 90% expenditure vs 45% physical completion.")
    investigator_recommendation: Optional[str] = Field(None, example="Withhold next tranche pending contractor audit.")
    investigator_notes: Optional[str] = Field(None, example="Site visited in person. Verified with local Panchayat head.")


class ResolveCase(BaseModel):
    """Admin or Investigator resolves/closes or escalates a case."""
    resolution: Literal["RESOLVED", "ESCALATED", "CLOSED_NO_ACTION", "CLOSED_ACTION_TAKEN"]
    resolution_notes: str = Field(..., min_length=5)


class CaseAuditLogResponse(BaseModel):
    id: int
    case_id: int
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    details: Optional[str] = None
    performed_by_id: Optional[int] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseResponse(CaseBase):
    id: int
    status: CaseStatusType
    requested_by_id: Optional[int] = None
    request_reason: Optional[str] = None
    assigned_to_id: Optional[int] = None
    evidence_photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_timestamp: Optional[datetime] = None
    site_condition: Optional[str] = None
    financial_observation: Optional[str] = None
    investigator_recommendation: Optional[str] = None
    investigator_notes: Optional[str] = None
    resolution: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_officer: Optional[UserResponse] = None
    requester: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
