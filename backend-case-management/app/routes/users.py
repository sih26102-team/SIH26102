from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models.models import User
from app.database.database import get_db
from typing import List
from app.core.security import get_hash_password
from app.core.Oauth2 import get_current_user,get_current_user_admin

router = APIRouter(
     prefix = "/users",
     tags = ["Users"]
)




@router.get("/",response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db),admin:User = Depends(get_current_user_admin)):
    users = db.query(User).all()
    return users



@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.UserResponse)
def register(user: schemas.UserCreate,db:Session = Depends(get_db)):
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
         raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail = "A user with this email already exists")
    existing_name = db.query(User).filter(User.username == user.username).first()
    if existing_name:
         raise HTTPException(status_code = status.HTTP_409_CONFLICT,detail = "A user with this username already exists")

    user_data = user.model_dump()
    user_data.pop("role",None)
    user_data["password"] = get_hash_password(user.password)
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return  new_user


@router.get("/{id}",response_model=schemas.UserResponse)
def get_user(id: int,db: Session = Depends(get_db),current_user:User = Depends(get_current_user)):
    if current_user.id != id and current_user.role != "admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You dont have access to view this data")
    req_user = db.query(User).filter(User.id==id).first()
    if not req_user:
         raise HTTPException(status_code=404, detail=f"User with id{id} not found")
    return req_user



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int,db: Session = Depends(get_db),admin:User = Depends(get_current_user_admin)):
    deleted_user = db.query(User).filter(User.id == id)
    if not deleted_user.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
    deleted_user.delete(synchronize_session=False)
    db.commit()



@router.put("/{id}",response_model=schemas.UserResponse)
def update_user(id: int, user: schemas.UserUpdate,db: Session = Depends(get_db),current_user:User = Depends(get_current_user)):
    if current_user.id != id and current_user.role != "admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not allowed update others data")
    updated_user = db.query(User).filter(User.id == id)
    if updated_user.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
    updated_user.update(user.model_dump(exclude_unset=True), synchronize_session=False)
    return updated_user
