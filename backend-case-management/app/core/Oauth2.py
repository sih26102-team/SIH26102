from jose import JWTError,jwt
from datetime import datetime,timedelta
from app.schemas.schemas import TokenData

from app.core.config import settings

from app.database.database import get_db
from app.models.models import User
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire_time = datetime.utcnow() + timedelta(minutes = settings.access_token_expire_time)
    to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token:str,credenials_exception):
    try:
        payload = jwt.decode(token,settings.secret_key,algorithms = [settings.algorithm])
        user_id:int = payload.get("user_id")
        email:str = payload.get("email")
        if user_id is None or email is None:
            raise credenials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credenials_exception
    return token_data

def get_current_user(token:str = Depends(oauth2_scheme),db:Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail = "Could not validate credentials", headers = {"WWW-Authenticate":"bearer"})
    token_data = verify_access_token(token,credentials_exception)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise credentials_exception
    return user

