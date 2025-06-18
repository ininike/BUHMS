from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from models.response import ResponseData
from models.input import SelectRoomInput, AddDeviceInput, ReadAnnouncementInput, MakeComplaintInput
from sqlmodel import select
from dependencies.db import db_dependency
from dependencies.auth import current_student_dependency
from models.database_models import Student, Hostel, HallAdmin, HostelStudent, Room, Device, Announcement, Complaint, AnnouncementRead
from datetime import datetime

router = APIRouter(
    tags=["students"],
    prefix="/student"
)

@router.post("/select-room", status_code=200, description="handles student room selection/changing")
async def change_room(input: SelectRoomInput, db: db_dependency, current_student: current_student_dependency):
    if current_student.has_checked_in == True:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Contact the Hall Admin to change your room after you have checked in."})
    current_student.room_id = input.room_id
    db.add(current_student)
    db.commit()
    return ResponseData(
        message="Room updated successfully",
    )
    
@router.get("/devices", status_code=200, description="Get all rooms in a hostel")
async def get_student_devices(db: db_dependency, current_student: current_student_dependency):
    devices = db.exec(select(Device).where(Device.room_student_id == current_student.id)).all()
    return ResponseData(
        message="Successfully retrieved student devices",
        data={"devices": devices}
    )
    
@router.get("/device/{device_id}", status_code=200, description="Get a specific device")
async def get_device(device_id: int, db: db_dependency, current_student: current_student_dependency):
    device = db.get(Device, device_id)
    if not device:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Device not found"})
    if device.room_student_id != current_student.id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have permission to view this device"})
    return ResponseData(
        message="Device retrieved successfully",
        data={"device": device}
    )

@router.post("/register-device", status_code=201, description="Register a new device for a student")
async def register_device(input: AddDeviceInput, db: db_dependency, current_student: current_student_dependency):
    device = Device(type=input.type,name=input.name,photo=input.photo,color=input.color,unique_code=input.unique_code, room_student_id=current_student.id)
    db.add(device)
    db.commit()
    return ResponseData(
        message="Device registered successfully",
    )
    
@router.delete("/remove-device/{device_id}", status_code=200, description="Remove a device (set date_removed to now)")
async def remove_device(device_id: int, db: db_dependency, current_student: current_student_dependency):
    device: Device = db.get(Device, device_id)
    if not device:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Device not found"})
    if device.room_student_id != current_student.id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have permission to remove this device"})
    if not device.receipt_confirmed:
        db.delete(device)
        db.commit()
    else:
        device.date_removed = datetime.now()
        db.add(device)
        db.commit()
    return ResponseData(
        message="Device removed successfully",
    )


    
@router.get("/merit-points", status_code=200, description="Get the current student's merit points")
async def get_merit_points(db: db_dependency, current_student: current_student_dependency):
    merit_points = current_student.merit_points
    return ResponseData(
        message="Successfully retrieved merit points",
        data={"merit_points": merit_points}
    )

@router.get("/announcements", status_code=200, description="Get the announcements for current student's hostels")
async def get_announcements(db: db_dependency, current_student: current_student_dependency):
    current_semester = current_student.academic_semester_id
    announcements = db.exec(select(Announcement).where(Announcement.academic_semester_id == current_semester).order_by(Announcement.time_created)).all()
    read_announcements = db.exec(select(AnnouncementRead).where(
        AnnouncementRead.hostel_student_id == current_student.id
    )).all()
    for announcement in announcements:
        announcement['is_read'] = any(read.announcement_id == announcement.id for read in read_announcements)
    return ResponseData(
        message="Successfully retrieved notice board announcements",
        data={"announcements": announcements}
    )

@router.get("/announcement/{announcement_id}", status_code=200, description="Mark an annoucements as read")
async def read_announcement(announcement_id: int, db:db_dependency, current_student: current_student_dependency):
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Announcement not found"})
    if announcement.hostel_id != current_student.hostel_id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have permission to read this announcement"})
    existing_read = db.exec(select(AnnouncementRead).where(
        AnnouncementRead.announcement_id == announcement_id,
        AnnouncementRead.hostel_student_id == current_student.id
    )).first()
    if not existing_read:
       read = AnnouncementRead(announcement_id=announcement_id,hostel_student_id=current_student.id,)
       db.add(read) 
       db.commit()
    return ResponseData(
        message="Annoucement retrieved successfully",
        data = {"announcement": announcement}
    )
    

    
@router.post("/make-complaint", status_code=200, description="Make a complaint to the hall admin")
async def make_complaint(input: MakeComplaintInput, db: db_dependency, current_student: current_student_dependency):
    complaint = Complaint(hostel_student_id=current_student.id, content=input.content)
    db.add(complaint)
    db.commit()
    return ResponseData(
        message="Complaint made successfully", 
        data={"complaint": complaint}
    )
    
@router.get("/close-complaint/{complaint_id}", status_code=200, description="Close a complaint")
async def close_complaint(complaint_id: int, db: db_dependency, current_student: current_student_dependency):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Complaint not found"})
    if complaint.hostel_student_id != current_student.id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have permission to close this complaint"})
    complaint.status = "resolved"
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return ResponseData(
        message="Complaint closed successfully",
        data={"complaint": complaint}
    )
    
@router.delete("/withdraw-complaint/{complaint_id}", status_code=200, description="Withdraw a complaint")
async def withdraw_complaint(complaint_id: int, db: db_dependency, current_student: current_student_dependency):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Complaint not found"})
    if complaint.hostel_student_id != current_student.id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have permission to withdraw this complaint"})
    if complaint.status != "pending":
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Only pending complaints can be withdrawn"})
    db.delete(complaint)
    db.commit()
    return ResponseData(
        message="Complaint withdrawn successfully",
    )
    
@router.post("/edit-complaint/{complaint_id}", status_code=200, description="Edit a complaint")
async def edit_complaint(complaint_id: int, input: MakeComplaintInput, db: db_dependency, current_student: current_student_dependency):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Complaint not found"})
    if complaint.hostel_student_id != current_student.id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have permission to edit this complaint"})
    if complaint.status != "pending":
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Only pending complaints can be withdrawn"})
    complaint.content = input.content
    db.add(complaint)
    db.commit()
    return ResponseData(
        message="Complaint edited successfully",
        data={"complaint": complaint}
    )

    
@router.get("/complaints", status_code=200, description="View complaints")
async def get_complaints(db: db_dependency, current_student: current_student_dependency):
    complaints = db.exec(select(Complaint).where(Complaint.hostel_student_id == current_student.id)).all()
    return ResponseData(
       message="Student complaints fetched successfully" ,
       data={"complaints": complaints}
    )
    
@router.get("complaint/{complaint_id}", status_code=200, description="View a specific complaint")
async def get_complaint(complaint_id: int, db: db_dependency, current_student: current_student_dependency):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Complaint not found"})
    if complaint.hostel_student_id != current_student.id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You do not have permission to view this complaint"})
    return ResponseData(
        message="Complaint retrieved successfully",
        data={"complaint": complaint}
    )