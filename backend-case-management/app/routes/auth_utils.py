from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import User
import os

SECRET_KEY = os.getenv('JWT_SECRET', 'super_secret_key_123')
ALGORITHM = 'HS256'
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail='Invalid authentication credentials')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid authentication credentials')

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail='User not found')
    return user
