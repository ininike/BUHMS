from fastapi import APIRouter, HTTPException, status, Depends
from models import Student, HallPorter, HallAdmin
from fastapi_jwt_auth import AuthJWT
from sqlmodel import select 
from dependencies.db import db_dependency
from dependencies.auth import login_form_dependency
from passlib.context import CryptContext

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def has_registered(student: Student) -> int | None:
    """Check if a student has paid of a hostel this semester"""
    for session_hostel in student.session_hostel:
        if session_hostel.has_checked_out == True:
            continue
        
        return session_hostel.id

def verify_login (username: str, password: str, db, user_type: str):
    if user_type == 'student':
        user = db.exec(select(Student).where(Student.matric_no == username)).first()
    elif user_type == 'porter':
        user = db.exec(select(HallPorter).where(HallPorter.email == username)).first()
    elif user_type == 'admin':
        user = db.exec(select(HallAdmin).where(HallAdmin.email == username)).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
    
    # valid = pwd_context.verify(password, user.password)
    valid = True
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username/password')
    
    return user
    
@router.post("/student-login", status_code=status.HTTP_200_OK, description="authenticate a student and return an access token")
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    student = verify_login(input.username, input.password, db, 'student')
    hostel_student_id = has_registered(student)
    if not hostel_student_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail={'message': 'You have not registered for a hostel this semester', 'isPaid':bool(hostel_student_id)})
    access_token = Authorize.create_access_token(subject=hostel_student_id, user_claims={'user_type': 'student'})
    Authorize.set_access_cookies(access_token)
    return {"message": "Log in successful"}

@router.post("/porter-login", status_code=status.HTTP_200_OK, description="authenticate a porter and return an access token")
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    porter = verify_login(input.username, input.password, db, 'porter')
    access_token = Authorize.create_access_token(subject=porter.id, user_claims={'user_type': 'porter'})
    Authorize.set_access_cookies(access_token)
    return {"message": "Log in successful"}

@router.post("/admin-login", status_code=status.HTTP_200_OK, description="authenticate an admin and return an access token")
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    admin = verify_login(input.username, input.password, db, 'admin')
    access_token = Authorize.create_access_token(subject=admin.id, user_claims={'user_type': 'admin'})
    Authorize.set_access_cookies(access_token)
    return {"message": "Log in successful"}

@router.post("/logout", status_code=status.HTTP_200_OK, description="logout a user")
async def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return {"message": "Logged out successfully"}

    


    


