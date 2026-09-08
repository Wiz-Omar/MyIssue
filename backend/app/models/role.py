from app.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer(), primary_key=True)
    role_name = Column(String(), nullable=False, unique=True)

    used_role = relationship("UserRole", back_populates="role")