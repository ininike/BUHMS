from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException, JWTDecodeError, MissingTokenError, CSRFError
from os import environ
from datetime import timedelta
from sqlmodel import SQLModel
from dotenv import load_dotenv
from routes import auth, test, rooms, students, leaderboard, complaints
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
    authjwt_token_expires: timedelta = timedelta(days=1)
    authjwt_cookie_max_age: int = 60 * 60 * 24 * 30


@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(JWTDecodeError)
def jwt_decode_exception_handler(request: Request, exc: JWTDecodeError):
    return JSONResponse(
        status_code=401,
        content={"message": "Invalid token."}
    )

@app.exception_handler(MissingTokenError)
def access_token_required_exception_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(
        status_code=401,
        content={"message": "You have not logged in"}
    )
    
@app.exception_handler(CSRFError)
def access_token_required_exception_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(
        status_code=401,
        content={"message": "You have not logged in"}
    )

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message,
                 "exc": str(exc.__class__.__name__)}
    )

@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred.",}
    )

    
app.include_router(auth.router)
app.include_router(test.router)
app.include_router(rooms.router)
app.include_router(students.router)
app.include_router(leaderboard.router)
app.include_router(complaints.router)