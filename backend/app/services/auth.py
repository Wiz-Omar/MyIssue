from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
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
                password_hash=get_password_hash(user_data.password)
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            return user
        
        except SQLAlchemyError as e:
            self.db.rollback()
            print("error:", str(e))
            raise HTTPException(status_code=500, detail="Database error")

    def get_user_by_id(self, user_id: int):
        try:
            statement = select(User).filter_by(id=user_id)
            return self.db.execute(statement).scalar_one_or_none()
        except SQLAlchemyError as e:
            print("error:", str(e))
            raise HTTPException(status_code=500, detail="Database error")

    def get_user_by_email(self, email: str):
            try:
                statement = select(User).filter_by(email=email)
                return self.db.execute(statement).scalar_one_or_none()
            except SQLAlchemyError as e:
                print("error:", str(e))
                raise HTTPException(status_code=500, detail="Database error")

    def authenticate_user(
        self, password, user_id: int | None = None, email: str | None = None
    ) -> User | None:
        if not user_id and not email:
            # Calling verify burns the same time when no user is found
            # Makes the response timing indistinguishable for an attacker
            verify_password(password)
            return None
        if user_id:
            user: User = self.get_user_by_id(user_id=user_id)
        else:
            print("trying email login")
            user: User = self.get_user_by_email(email=email)
            print(user)
        if not user:
            # Calling verify burns the same time when no user is found
            # Makes the response timing indistinguishable for an attacker
            verify_password(password)
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
