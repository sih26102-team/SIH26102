from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models.models import User
from app.core.security import verify_password
from app.core.Oauth2 import create_access_token

router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login')
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        data = await request.json()
        username = data.get("username") or data.get("email")
        password = data.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username/email and password required")

    db_user = db.query(User).filter((User.email == username) | (User.username == username)).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account pending admin approval")
    if not verify_password(password, db_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = create_access_token(data={"user_id": db_user.id, "email": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "name": db_user.full_name or db_user.username,
            "role": db_user.role,
        }
    }

    

    