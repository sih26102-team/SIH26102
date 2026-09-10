from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas import schemas
from app.models.models import User
from app.database.database import get_db
from app.core.security import get_hash_password
from app.core.Oauth2 import get_current_user, get_current_user_admin

router = APIRouter(
    prefix="/users",
    tags=["Users & Investigator Management"]
)


@router.get("/", response_model=List[schemas.UserResponse])
def get_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user_admin)
):
    """Admin-only endpoint: List all users, optionally filtered by role."""
    query = db.query(User)
    if role:
        query = query.filter(User.role.ilike(role))
    return query.order_by(User.created_at.desc()).all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_investigator(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user_admin)
):
    """
    Admin-only endpoint: Provision a new investigator or analyst account.
    Public registration is strictly disabled.
    """
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists."
        )

    existing_name = db.query(User).filter(User.username == user.username).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists."
        )

    user_data = user.model_dump()
    raw_password = user_data.pop("password")
    user_data["password"] = get_hash_password(raw_password)
    user_data["role"] = user_data.get("role") or "investigator"
    user_data["is_active"] = True

    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/{id}/toggle-status", response_model=schemas.UserResponse)
def toggle_user_status(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user_admin)
):
    """Admin-only endpoint: Activate or disable an investigator account."""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate own admin account")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user profile. Allowed for the account owner or an admin."""
    if current_user.id != id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to account owner or administrator"
        )
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return user


@router.delete("/{id}", response_model=schemas.MessageResponse)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user_admin)
):
    """Admin-only endpoint: Delete a user account."""
    if id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own admin account")

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted successfully"}
