from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserCreate):
        try:
            user = User(
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                email=user_data.email,
                password_hash=user_data.password
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            return user
        
        except SQLAlchemyError as e:
            self.db.rollback()
            print("error:")
            print(e._message())
            raise HTTPException(status_code=500, detail="Database error")
