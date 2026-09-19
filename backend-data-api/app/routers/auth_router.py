from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from app.database.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "SIH2026_SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class LoginReq(BaseModel):
    username: str
    password: str

class VerifyOTPReq(BaseModel):
    username: str
    otp: str

class ChangePasswordReq(BaseModel):
    new_password: str

# 1. Login step 1: Check password, trigger OTP
@router.post("/login")
def login(req: LoginReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    # If valid: create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "is_first_login": user.is_first_login},
        expires_delta=access_token_expires
    )
    
    # Audit log login
    from app.models import AuditLog
    audit = AuditLog(actor_user_id=user.id, action="USER_LOGIN", entity_type="User", entity_id=str(user.id), metadata_json="User logged in via OTP")
    db.add(audit)
    db.commit()

    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "is_first_login": user.is_first_login}

# 2. Login step 2: Verify OTP and get JWT
@router.post("/verify-otp")
def verify_otp(req: VerifyOTPReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Prototype OTP simulation (hardcoded to 123456)
    if req.otp != "123456":
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "is_first_login": user.is_first_login}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": {
            "id": user.id, 
            "username": user.username, 
            "role": user.role, 
            "is_first_login": user.is_first_login,
            "state_id": user.state_id,
            "district_id": user.district_id
        }
    }

# RBAC Dependencies
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def require_role(allowed_roles: list):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough privileges")
        return current_user
    return role_checker

@router.post("/first-login")
def first_login(req: ChangePasswordReq, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_first_login:
        raise HTTPException(status_code=400, detail="Not a first login flow")
        
    current_user.password = get_password_hash(req.new_password)
    current_user.is_first_login = False
    db.commit()
    return {"message": "Password changed successfully. Proceed to dashboard."}
