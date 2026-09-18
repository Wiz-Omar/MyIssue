from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserLogoutRequest, UserResponse
from app.services.auth import UserService
from app.services.refresh_token import RefreshTokenService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse , status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):  #noqa: B008
    user_service = UserService(db)
    user: User = user_service.register_user(user_data)
    return user # FastAPI converts User type to UserResponse since response model is set above

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):  #noqa: B008
    user_service = UserService(db)
    user: User = user_service.authenticate_user(password=user_data.password, email=user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_service.issue_tokens(user.id)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(data: UserLogoutRequest, db: Session = Depends(get_db)): #noqa B008
    refresh_token_service = RefreshTokenService(db)
    refresh_token_service.revoke(data.refresh_token)
    return {"message": "Logged out successfully"}

@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)): #noqa B008
    user_service: UserService = UserService(db)
    refresh_token_service: RefreshTokenService = RefreshTokenService(db)
    user_id: int = refresh_token_service.validate_and_rotate(data.refresh_token)
    return user_service.issue_tokens(user_id)
