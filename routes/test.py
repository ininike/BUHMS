from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from sqlmodel import select
from dependencies.db import db_dependency
from models.database_models import Student, HallPorter, HallAdmin, HostelStudent, Room, AcademicSession, Hostel

router = APIRouter(
    tags =['test'],
    prefix="/test"
)

@router.get("/rooms", status_code=200, description="Get all rooms in a hostel")
async def get_rooms(db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(Room).count.where(Room.id != 1 and Room.hostel_id == 1)
    print(statement)
    rooms = db.exec(statement).mappings().first()
    print(rooms)
    return rooms
    
    