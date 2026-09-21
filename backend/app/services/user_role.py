from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.role import RoleName


class UserRoleService:
    def __init__(self, db: Session):
        self.db = db

    def has_role(self, role: RoleName, user_id: UUID) -> bool:
        try:
            statement = (select(UserRole)
                            .join(Role, UserRole.role_id == Role.id)
                            .where(UserRole.user_id == user_id, Role.role_name == role)
            )
            result = self.db.execute(statement).scalar_one_or_none()
            return result is not None
        except SQLAlchemyError as e:
            print('error:', str(e))
            raise HTTPException(status_code=500, detail="Database error")

    def add_user_role(self, role: RoleName, user_id: UUID) -> UserRole:
        try:
            role_fetch_statement = select(Role).where(Role.role_name==role)
            role: Role | None = self.db.execute(role_fetch_statement).scalar_one_or_none()

            if role is None:
                raise HTTPException(status_code=404, detail="Role not found")
            if self.has_role(RoleName(role.role_name), user_id):
                raise HTTPException(status_code=409, detail="User already has this role")

            user_role = UserRole(
                user_id=user_id,
                role_id=role.id
            )
            self.db.add(user_role)
            self.db.commit()
            self.db.refresh(user_role)

            return user_role
        except SQLAlchemyError as e:
            self.db.rollback()
            print("error:", str(e))
            raise HTTPException(status_code=500, detail="Database error")
