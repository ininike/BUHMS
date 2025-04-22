from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
import jwt
from jwt.exceptions import InvalidTokenError
from models import HostelStudent, HallPorter, HallAdmin
from typing import Annotated
from .db import db_dependency
from utils.auth import SECRET_KEY, ALGORITHM

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login")
token_dependency = Annotated[str, Depends(reusable_oauth2)]

def get_current_student(db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    if Authorize.get_raw_jwt()['user_type'] !='student':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Access Denied')
    hostel_student_id: int = Authorize.get_jwt_subject()
    student = db.get(HostelStudent, hostel_student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Unable to validate credentials')
    return student

current_student_dependency = Annotated[HostelStudent, Depends(get_current_student)]

def get_current_porter(token: token_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    if Authorize.get_raw_jwt()['user_type'] !='porter':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Access Denied')
    porter_id: int = Authorize.get_jwt_subject()
    porter = db.get(HallPorter, porter_id)
    if porter is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Unable to validate credentials')
    return porter

current_porter_dependency = Annotated[HallPorter, Depends(get_current_porter)]

def get_current_admin(token: token_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        if Authorize.get_raw_jwt()['user_type'] !='admin':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Access Denied')
        admin_id: int = Authorize.get_jwt_subject()
        admin = db.get(HallAdmin, admin_id)
        if admin is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Unable to validate credentials')
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid token')
    return admin
    
current_admin_dependency = Annotated[HallAdmin, Depends(get_current_admin)]   

def get_current_user(token: token_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    pass
    # j
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #     if payload
    #     else:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Unable to validate credentials')
    # except InvalidTokenError:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid token')
    return None 

login_form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
