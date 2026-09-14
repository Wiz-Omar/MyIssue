from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate
from app.services.auth import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):  #noqa: B008
    user_service = UserService(db)
    user_service.register_user(user_data)
    return JSONResponse(
        status_code=201,
        content={"message": "User registered successfully"}
    )
