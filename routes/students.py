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
    tags=["students"],
    prefix="/students"
)

@router.post("/select-room", status_code=200, description="handles student room selection/changing")
async def change_room(input: RoomsStudentsInput, db: db_dependency, current_student: current_student_dependency, Authorize: AuthJWT = Depends()):
    if current_student.has_checked_in == True:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Contact the Hall Admin to change your room after you have checked in."})
    current_student.room_id = input.room_id
    db.add(current_student)
    db.commit(current_student)
    return ResponseData(
        message="Room updated successfully",
        status_code=200,
    )

