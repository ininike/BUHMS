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
    
    semester_hostels: List["HostelStudent"] = Relationship(back_populates="student")
    
class Hostel (SQLModel, table=True):
    __tablename__ = "hostels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    
    admin: "HallAdmin" = Relationship(back_populates="hostel")
    rooms: List["Room"] = Relationship(back_populates="hostel")
    semester_students: List["HostelStudent"] = Relationship(back_populates="hostel")
    announcements: List["Announcement"] = Relationship(back_populates="hostel")
    
class HallAdmin (SQLModel, table=True):
    __tablename__ = "admins"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tel: str
    hostel_id: int = Field(foreign_key="hostels.id")
    email: str
    password: str
    type: str
    
    hostel: Hostel = Relationship(back_populates="admin")
    announcements: List["Announcement"] = Relationship(back_populates="admin")
    complaints_commented: List["Complaint"] = Relationship(back_populates="admin")
    
class Room (SQLModel, table=True):
    __tablename__ = "rooms"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    room_number: str
    hostel_id: int = Field(foreign_key="hostels.id")
    max_space: int
    
    hostel: Hostel = Relationship(back_populates="rooms")
    semester_students: List["HostelStudent"] = Relationship(back_populates="room")
    
class AcademicSemester (SQLModel, table=True):
    __tablename__ = "academic_semesters"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    semester_name: str
    registration_start_date: datetime
    semester_end_date: Optional[datetime]
    is_current: bool = Field(default=False)   
    
    hostel_students: List["HostelStudent"] = Relationship(back_populates="semester")
    announcements: List["Announcement"] = Relationship(back_populates="semester")
    
class HostelStudent (SQLModel, table=True):
    __tablename__ = "hostels_students"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: Optional[int] = Field(default=None, foreign_key="rooms.id")
    student_id: int = Field(foreign_key="students.id")
    academic_semester_id: int = Field(foreign_key="academic_semesters.id")
    has_checked_in: bool = Field(default=False)
    has_checked_out: bool = Field(default=False)
    hostel_id: int = Field(foreign_key="hostels.id")
    merit_points: int 
    time_checked_in: Optional[datetime]
    time_checked_out: Optional[datetime]
    
    hostel: Hostel = Relationship(back_populates="semester_students")
    student: Student = Relationship(back_populates="semester_hostels")
    room: Optional[Room] = Relationship(back_populates="semester_students")
    semester: AcademicSemester = Relationship(back_populates="hostel_students")
    semester_devices: List["Device"] = Relationship(back_populates="hostel_student")
    complaints: List["Complaint"] = Relationship(back_populates="hostel_student")
    reads: List["AnnouncementRead"] = Relationship(back_populates="hostel_student")
    
class Device(SQLModel, table=True):
    __tablename__ = "devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    name: str
    photo: Optional[str]
    color: str
    unique_code: str
    receipt_confirmed: bool = Field(default=False)
    time_received: Optional[datetime]
    time_removed: Optional[datetime]
    room_student_id: int = Field(foreign_key="hostels_students.id")
    
    hostel_student: HostelStudent = Relationship(back_populates="semester_devices")
    
class Announcement(SQLModel, table=True):
    __tablename__ = "announcements"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str]
    content: str
    time_created: datetime
    admin_id: int = Field(foreign_key="admins.id")
    hostel_id: int = Field(foreign_key="hostels.id")
    semester_id: int = Field(foreign_key="academic_semesters.id")
    
    hostel: Hostel = Relationship(back_populates="announcements")
    semester: AcademicSemester = Relationship(back_populates="announcements")
    reads: List["AnnouncementRead"] = Relationship(back_populates="announcement")
    admin: HallAdmin = Relationship(back_populates="announcements")
    
class Complaint(SQLModel, table=True):
    __tablename__ = "complaints"

    id: Optional[int] = Field(default=None, primary_key=True)
    hostel_student_id: int = Field(foreign_key="hostels_students.id")
    content: str
    time_created: datetime = Field(default=datetime.now())
    status: str = Field(default="pending")  # pending, resolved, rejected
    comment: Optional[str] = None  # Admin's comment on the complaint
    comment_by : Optional[int] = Field(default=None, foreign_key="admins.id")  # Admin who commented on the complaint
    
    hostel_student: HostelStudent = Relationship(back_populates="complaints")
    admin: Optional[HallAdmin] = Relationship(back_populates="complaints_commented")
    
class AnnouncementRead(SQLModel, table=True):
    __tablename__ = "announcements_reads"

    id: Optional[int] = Field(default=None, primary_key=True)
    announcement_id: int = Field(foreign_key="announcements.id")
    hostel_student_id: int = Field(foreign_key="hostels_students.id")
    
    announcement: Announcement = Relationship(back_populates="reads")
    hostel_student: HostelStudent = Relationship(back_populates="reads")