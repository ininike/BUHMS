from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from sqlmodel import select 
from dependencies.db import db_dependency
from models.database_models import Student, HallPorter, HallAdmin, HostelStudent, Room, AcademicSession

router = APIRouter(
    tags=["rooms"]
)

@router.get("/rooms", status_code=200, description="Get all rooms in a hostel", response_model=list[Room])
async def get_rooms(db: db_dependency, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user_type = Authorize.get_jwt_claims().get('user_type')
    rooms = db.exec(select(Room).where(Room.hostel_id == current_user)).all()
    current_semester = db.exec(select(AcademicSession).where(AcademicSession.is_current == True)).first()
    
    if user_type == 'admin' or 'porter':
        rooms = db.exec(select(Room).where(Room.hostel_id == current_user)).all()
        return rooms
    else:
        return JSONResponse(status_code=403, content={"message": "Forbidden"})
    
    return rooms


response = [{
    'room_number': str,
    'max_space': int,
    'students': {
        'name': str,
        'matric_no': str,
    },
}]

response_2 = {
    
}