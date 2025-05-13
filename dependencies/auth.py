from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from models import HostelStudent, HallPorter, HallAdmin
from typing import Annotated
from .db import db_dependency
from dotenv import load_dotenv
from os import environ

load_dotenv()

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login")
token_dependency = Annotated[str, Depends(reusable_oauth2)]

def authenticate_user(Authorize: AuthJWT = Depends(), user_type: str = None):
    Authorize.jwt_required()
    if Authorize.get_raw_jwt()['user_type'] != user_type:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied')
    user_id: int = Authorize.get_jwt_subject()
    return user_id

def validate_user(user_id: int, db: db_dependency, user_type: str):
    if user_type == 'student':
        user = db.get(HostelStudent, user_id)
    elif user_type == 'porter':
        user = db.get(HallPorter, user_id)
    elif user_type == 'admin':
        user = db.get(HallAdmin, user_id)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unable to validate credentials')
    
    return user

def get_current_student(db: db_dependency, Authorize: AuthJWT = Depends()):
    user_id = authenticate_user(Authorize, user_type='student')
    student = validate_user(user_id, db, user_type='student')
    return student

current_student_dependency = Annotated[HostelStudent, Depends(get_current_student)]

def get_current_porter(db: db_dependency, Authorize: AuthJWT = Depends()):
    user_id = authenticate_user(Authorize, user_type='porter')
    porter = validate_user(user_id, db, user_type='porter')
    return porter

current_porter_dependency = Annotated[HallPorter, Depends(get_current_porter)]

def get_current_admin(db: db_dependency, Authorize: AuthJWT = Depends()):
    user_id = authenticate_user(Authorize, user_type='admin')
    admin = validate_user(user_id, db, user_type='admin')
    return admin
    
current_admin_dependency = Annotated[HallAdmin, Depends(get_current_admin)]   

login_form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
