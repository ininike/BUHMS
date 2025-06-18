from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from sqlmodel import select
from dependencies.db import db_dependency
from dependencies.auth import current_student_dependency
from models.database_models import Student, Hostel, HallAdmin, HostelStudent, Room, Device


router = APIRouter(
    tags=["devices"],
    prefix="/devices"
)

@router.get("/{student_id}", status_code=200, description="Get all rooms in a hostel")
async def get_student_devices(student_id: int, db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_type = Authorize.get_raw_jwt()['user_type']
    if user_type == 'student':
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN)
    devices = db.exec(select(Device).where(Device.room_student_id == student_id)).all()
    return ResponseData(
        message="Successfully retrieved student devices",
        data=devices
    )


    
