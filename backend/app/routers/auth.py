from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import create_access_token
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserLogin
from app.services.auth import UserService

router = APIRouter(prefix="/auth", tags=["auth"])
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):  #noqa: B008
    user_service = UserService(db)
    user_service.register_user(user_data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User registered successfully"}
    )

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):  #noqa: B008
    user: User = UserService(db).authenticate_user(password=user_data.password, email=user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )
