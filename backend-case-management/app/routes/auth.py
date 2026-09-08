from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models.models import User
from app.core.security import verify_password
from app.core.Oauth2 import create_access_token

router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login',response_model=schemas.TokenResponse)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.username).first()
    if not db_user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Invalid Credentials")
    if not verify_password(user.password,db_user.password):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Invalid Credentials")

    access_token = create_access_token(data={"user_id": db_user.id,"email":db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}
    

    