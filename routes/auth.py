from fastapi import APIRouter, status, Depends, Response
from fastapi.responses import JSONResponse
from models.database_models import Student, HallPorter, HallAdmin, HostelStudent, AcademicSemester
from models.auth import LoginResponse
from models.response import ResponseData
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

def has_registered(student: Student) -> HostelStudent | None:
    """Check if a student has paid of a hostel this semester"""
    for semester_hostel in student.semester_hostels:
        if semester_hostel.has_checked_out == True:
            continue
        return semester_hostel
    
def verify_login (username: str, password: str, db, user_type: str):
    if user_type == 'student':
        user = db.exec(select(Student).where(Student.matric_no == username)).first()
    elif user_type == 'porter':
        user = db.exec(select(HallPorter).where(HallPorter.email == username)).first()
    elif user_type == 'admin':
        user = db.exec(select(HallAdmin).where(HallAdmin.email == username)).first()
    
    if user is None:
        return None
    
    valid = password == user.password
    if not valid:
        return None
    return user

def get_current_semester(db):
    """Get the current academic session"""
    return db.exec(select(AcademicSemester).where(AcademicSemester.is_current == True)).first()
    
@router.post("/student-login", status_code=status.HTTP_200_OK, description="authenticate a student and return an access token", response_model=LoginResponse)
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    student = verify_login(input.username, input.password, db, 'student')
    if student is None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Invalid username or password"})
    student_hostel = has_registered(student)
    if student_hostel:
        access_token = Authorize.create_access_token(subject=student_hostel.id, user_claims={
                'user_type': 'student',
                'hostel_id': student_hostel.hostel_id,
                'current_semester': get_current_semester(db).id,
            })
        Authorize.set_access_cookies(access_token)
    return LoginResponse(
        message="Log in successful",
        hasRoom=bool(student_hostel.room_id),
        isPaid=bool(student_hostel)
    )

@router.post("/porter-login", status_code=status.HTTP_200_OK, description="authenticate a porter and return an access token", response_model=ResponseData)
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    porter = verify_login(input.username, input.password, db, 'porter')
    if porter is None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Invalid username or password"})
    access_token = Authorize.create_access_token(subject=porter.id, user_claims={'user_type': 'porter'})
    Authorize.set_access_cookies(access_token)
    return ResponseData(message="Login successful")

@router.post("/admin-login", status_code=status.HTTP_200_OK, description="authenticate an admin and return an access token", response_model=ResponseData)
async def login(input: login_form_dependency, db: db_dependency, Authorize: AuthJWT = Depends()):
    admin = verify_login(input.username, input.password, db, 'admin')
    if admin is None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Invalid username or password"})
    access_token = Authorize.create_access_token(subject=admin.id, user_claims={'user_type': 'admin'})
    Authorize.set_access_cookies(access_token)
    return ResponseData(message="Login successful")

@router.post("/logout", status_code=status.HTTP_200_OK, description="logout a user", response_model=ResponseData)
async def logout( response: Response, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies(response)
    return ResponseData(message="Logout successful")

    


    


