from redis import Redis
from fastapi_jwt_auth import AuthJWT
from dotenv import load_dotenv
import os
from models import Student

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def has_registered(student: Student) -> int | None:
    """Check if a student has paid of a hostel this semester"""
    for session_hostel in student.session_hostel:
        if session_hostel.has_checked_out == True:
            continue
        return session_hostel.id



    
