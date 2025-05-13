from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class Student (SQLModel, table=True):
    __tablename__ = "students"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    student_name: str
    student_email: str
    matric_no: str
    password: str
    
    session_hostel: List["HostelStudent"] = Relationship(back_populates="student")
    
class Hostel (SQLModel, table=True):
    __tablename__ = "hostels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    
    admin: "HallAdmin" = Relationship(back_populates="hostel")
    porters: List["HallPorter"] = Relationship(back_populates="hostel")
    rooms: List["Room"] = Relationship(back_populates="hostel")
    session_students: List["HostelStudent"] = Relationship(back_populates="hostel")
    
class HallPorter (SQLModel, table=True):
    __tablename__ = "admins"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tel: str
    hostel_id: int = Field(foreign_key="hostels.id")
    email: str
    password: str
    
    hostel: Hostel = Relationship(back_populates="porters")
    
class HallAdmin (SQLModel, table=True):
    __tablename__ = "super_admins"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tel: str
    hostel_id: int = Field(foreign_key="hostels.id")
    email: str
    password: str
    
    hostel: Hostel = Relationship(back_populates="admin")
    
class Room (SQLModel, table=True):
    __tablename__ = "rooms"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    room_number: str
    hostel_id: int = Field(foreign_key="hostels.id")
    max_space: int
    
    hostel: Hostel = Relationship(back_populates="rooms")
    session_students: List["HostelStudent"] = Relationship(back_populates="room")
    
class AcademicSession (SQLModel, table=True):
    __tablename__ = "academic_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_name: str
    registration_start_date: datetime
    semester_end_date: Optional[datetime]
    is_current: bool = Field(default=False)   
    
    hostel_students: List["HostelStudent"] = Relationship(back_populates="current_session")
    
class HostelStudent (SQLModel, table=True):
    __tablename__ = "hostels_students"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: Optional[int] = Field(default=None, foreign_key="rooms.id")
    student_id: int = Field(foreign_key="students.id")
    academic_session_id: int = Field(foreign_key="academic_sessions.id")
    has_checked_in: bool = Field(default=False)
    has_checked_out: bool = Field(default=False)
    hostel_id: int = Field(foreign_key="hostels.id")
    merit_points: int 
    time_checked_in: Optional[datetime]
    time_checked_out: Optional[datetime]
    
    hostel: Hostel = Relationship(back_populates="session_students")
    student: Student = Relationship(back_populates="session_hostel")
    room: Optional[Room] = Relationship(back_populates="session_students")
    current_session: AcademicSession = Relationship(back_populates="hostel_students")