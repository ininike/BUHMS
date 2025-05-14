from sqlmodel import SQLModel

class ResponseData(SQLModel):
    """Base class for all response data models"""
    message: str
    data: dict | None = None