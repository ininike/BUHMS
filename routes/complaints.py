from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from sqlmodel import select
from dependencies.db import db_dependency
from dependencies.auth import current_student_dependency
from models.database_models import Student, Hostel, HallAdmin, HostelStudent, Room

router = APIRouter(
    tags=["complaints"],
    prefix="/complaints"
)




    
    
    