from sqlmodel import SQLModel

class RoomsStudentsInput(SQLModel):
    """Input model for rooms and students"""
    room_id: int