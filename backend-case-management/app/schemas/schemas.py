from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="poornesh_s")
    email: EmailStr = Field(..., example="user@example.com")
    full_name: Optional[str] = Field(None, max_length=100, example="Srimanthula Poornesh")
    role: Optional[str] = Field("Investigator", json_schema_extra={"example": "Investigator"})


class UserCreate(UserBase):
    """Used for register / create_user request body."""
    password: str = Field(..., min_length=8, max_length=72, example="SecurePass123!",description="Password must be between 8 and 72 characters long.")

    @field_validator('password')
    @classmethod
    def validate_password(cls,value:str):
        if len(value.encode("utf-8"))>72:
            raise ValueError("Password must not exceed 72 bytes when encoded in UTF-8.")
        return value
    
class UserUpdate(BaseModel):
    """Optional: for updating profile fields."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Used for get_user and successful create_user response."""
    id: int
    is_active: bool = True
    created_at: datetime
    

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr = Field(...,example="Poorna@gmail.com")
    password:str = Field(...,min_length = 8, max_length=72, example="SecurePass123!",description="Password must be between 8 and 72 characters long.")

class TokenResponse(BaseModel):
    access_token:str = Field(...,example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InBvb3JuZXNoQGdtYWlsLmNvbSIsImV4cCI6MTY5MDAwMDAwMH0.abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890")
    token_type:str = "bearer"
class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None

class CaseBase(BaseModel):
    title: str = Field(...,min_length =3,max_length = 200)
    description :Optional[str] = None
    flagged_work_id:str = Field(...,description = "ID of the flagged work from data-ai-engine")
    risk_score: float = Field(default = 0.0,ge = 0.0, le = 1.0)

class CreateCase(CaseBase):
    pass

class UpdateCase(BaseModel):
    status:Optional[str] = Field(None, description = "OPEN, UNDER_INVESTIGATION, RESOLVED,CLOSED")
    description:Optional[str] = None
    assigned_to_id : Optional[int] = None

class CaseResponse(CaseBase):
    id:int
    status:str
    assigned_to_id: Optional[int] = None
    created_at: datetime
    assigned_officer:Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes = True)

class MessageResponse(BaseModel):
    """Standard response for delete_user, archive_case, or general status actions."""
    message: str
    detail: Optional[str] = None

