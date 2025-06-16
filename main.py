from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from os import environ
from datetime import timedelta
from sqlmodel import SQLModel
from dotenv import load_dotenv
from routes import auth, test, rooms, students, devices, complaints
from redis import Redis

load_dotenv()

app = FastAPI()
origins = [
    'http://localhost:3000'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(SQLModel):
    authjwt_secret_key: str = environ.get("JWT_KEY")
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_secure: bool = True
    authjwt_cookie_csrf_protect: bool = True
    authjwt_cookie_samesite: str = "lax"
    authjwt_cookie_max_age: int = 60 * 60 * 24 * 30


@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )

@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
    )
    
app.include_router(auth.router)
app.include_router(test.router)
app.include_router(rooms.router)
app.include_router(students.router)
app.include_router(devices.router)
app.include_router(complaints.router)