from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from models.rooms import RoomsStudentsInput
from sqlmodel import select
from dependencies.db import db_dependency
from dependencies.auth import current_student_dependency
from models.database_models import Student, Hostel, HallPorter, HallAdmin, HostelStudent, Room, AcademicSession

router = APIRouter(
    tags=["devices"],
    prefix="/devices"
)

@router.get("/", status_code=200, description="Get all rooms in a hostel")
async def get_student_devices(db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    devices = db.exec()