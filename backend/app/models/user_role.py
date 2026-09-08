from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class UserRole(Base):
    __tablename__ = 'user_roles'

    user_id = Column(Integer(), ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer(), ForeignKey('roles.id'), primary_key=True)

    user = relationship("User", back_populates="assigned_roles")
    role = relationship("Role", back_populates="used_role")