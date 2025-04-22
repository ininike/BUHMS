from sqlmodel import create_engine
from dotenv import load_dotenv
from os import environ

load_dotenv()

DATABASE_URL = environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
        



