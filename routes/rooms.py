from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from sqlmodel import select
from dependencies.db import db_dependency
from dependencies.auth import current_student_dependency
from models.database_models import Student, Hostel, HallAdmin, HostelStudent, Room

router = APIRouter(
    tags=["rooms"],
    prefix="/rooms"
)

def fetch_rooms(db, hostel_id: int, user_type: str, student_id: int) -> list:
    """Get all rooms in a hostel"""
    rooms = db.exec(select(Room).where(Room.hostel_id == hostel_id)).all()
    if user_type == 'student':
        student: HostelStudent = db.exec(select(HostelStudent).where(HostelStudent.id == student_id)).first()
        hostels_students = db.exec(select(HostelStudent).where(HostelStudent.hostel_id == hostel_id and HostelStudent.has_checked_out == False)).all()
        rooms = [ room.__dict__ for room in rooms ]
        for room in rooms:
            students = [ student for student in hostels_students if student.room_id == room['id'] ]
            room['count'] = len(students) 
        free_rooms = [ room for room in rooms if room['max_space'] != room['count'] and room['id'] != student.room_id ]
        return free_rooms
    return rooms
    
@router.get("/", status_code=200, description="Get all rooms in a hostel")
async def get_rooms(db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    user_id =  Authorize.get_jwt_subject()
    rooms = fetch_rooms(db, user_claims['hostel_id'], user_claims['user_type'], user_id)
    return ResponseData(
        message="Rooms fetched successfully",
        status_code=200,
        data={'rooms': rooms},
    )
    
@router.get("/{room_id}", status_code=200, description="Get all students in a room")
async def get_room_students(room_id: int, db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    room = db.get(Room, room_id)
    if room is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Room not found"})
    if room.hostel_id != Authorize.get_raw_jwt()['hostel_id']:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have access to this room"})
    rooms_students = db.exec(select(HostelStudent).where(HostelStudent.room_id == room_id and HostelStudent.has_checked_out == False)).all()
    return ResponseData(
        message="Rooms fetched successfully",
        status_code=200,
        data={'students': rooms_students},
    )

    
    