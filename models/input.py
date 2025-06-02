from sqlmodel import SQLModel
from typing import Optional

class SelectRoomInput(SQLModel):
    room_id: int
    
class AddDeviceInput(SQLModel):
    type: str
    name: str
    photo: Optional[str]
    color: str
    unique_code: str
    
class ReadAnnouncementInput(SQLModel):
    announcement_id: int