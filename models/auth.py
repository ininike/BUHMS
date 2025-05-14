from sqlmodel import SQLModel
from .response import ResponseData

class LoginResponse(ResponseData):
    """Response model for login"""
    hasRoom: bool | None = None
    isPaid: bool | None = None