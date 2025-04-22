from fastapi import Depends
from sqlmodel import Session
from database import engine
from typing import Annotated

def get_session():
    with Session(engine) as session:
        yield session
        
db_dependency = Annotated[Session, Depends(get_session)]