from fastapi import APIRouter, HTTPException, status, Depends
from models import Student, HallPorter, HallAdmin, Token
from fastapi_jwt_auth import AuthJWT
from sqlmodel import select 
from dependencies.db import db_dependency
from dependencies.auth import login_form_dependency, current_student_dependency
from passlib.context import CryptContext
from utils.auth import create_access_token, has_registered
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
@router.post("/student-login", status_code=status.HTTP_200_OK, description="authenticate a student and return an access token", response_model=Token)
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    student = db.exec(select(Student).where(Student.matric_no == input.username)).first()
    if student is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username/password')
    valid = pwd_context.verify(input.password, student.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username/password')
    hostel_student_id = has_registered(student)
    if not hostel_student_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You have not paid for a hostel')
    access_token = Authorize.create_access_token(subject=hostel_student_id, user_claims={'user_type': 'student'})
    refresh_token = Authorize.create_refresh_token(subject=hostel_student_id, user_claims={'user_type': 'student'})
    return {'access_token': access_token, 'refresh_token': refresh_token}

@router.post("/porter-login", status_code=status.HTTP_200_OK, description="authenticate a porte and return an access token", response_model=Token)
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    porter = db.exec(select(HallPorter).where(HallPorter.email == input.username)).first()
    if porter is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username/password')
    valid = pwd_context.verify(input.password, porter.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username/password')
    access_token = Authorize.create_access_token(subject=porter.id, user_claims={'user_type': 'porter'})
    refresh_token = Authorize.create_refresh_token(subject=porter.id, user_claims={'user_type': 'porter'})
    return {'access_token': access_token, 'refresh_token': refresh_token}

@router.post("/admin-login", status_code=status.HTTP_200_OK, description="authenticate an admin and return an access token", response_model=Token)
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    admin = db.exec(select(HallAdmin).where(HallAdmin.email == input.username)).first()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username/password')
    valid = pwd_context.verify(input.password, admin.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username/password')
    access_token = Authorize.create_access_token(subject=admin.id, user_claims={'user_type': 'porter'})
    refresh_token = Authorize.create_refresh_token(subject=admin.id, user_claims={'user_type': 'porter'})
    return {'access_token': access_token, 'refresh_token': refresh_token}

@router.post("/logout", status_code=status.HTTP_200_OK, description="logout a user")
async def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.jwt_refresh_token_required()
    
    return {"message": "Logged out successfully"}








    


