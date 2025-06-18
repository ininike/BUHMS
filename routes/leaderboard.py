from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from sqlmodel import select
from dependencies.db import db_dependency
from dependencies.auth import current_student_dependency
from models.database_models import Student, Hostel, HallAdmin, HostelStudent, Room

router = APIRouter(
    tags=["leaderboard"],
    prefix="/leaderboard"
)   

@router.get("/", status_code=200, description="Get leaderboard of students in a hostel")
async def get_leaderboard(db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    hostel_id = user_claims['hostel_id']
    students = db.exec(select(HostelStudent).where(HostelStudent.has_checked_out == False and HostelStudent.hostel_id == hostel_id).order_by(HostelStudent.room_id)).all()
    rooms = db.exec(select(Room).where(Room.hostel_id == hostel_id)).all()
    leaderboard = []
    rooms = [ room.__dict__ for room in rooms ]  # Convert Room objects to dicts for easier acces
    students = [student.__dict__ for student in students]  # Convert HostelStudent objects to dicts for easier access
    for room in rooms:
        room_students = [student for student in students if student['room_id'] == room['id']]
        if room_students:
            leaderboard.append({
                'room': room.name,
                'students': [{
                    'name': student['student'].name,
                    'matric_no': student['student'].matric_no,
                    'merit_points': student['merit_points'],
                    } for student in room_students],
            })
    return ResponseData(
        message="Leaderboard fetched successfully",
        status_code=200,
        data={'leaderboard': leaderboard},
    )