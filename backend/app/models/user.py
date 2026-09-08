from datetime import datetime

from app.database import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    first_name = Column(String(), nullable=False)
    last_name = Column(String(),  nullable=False)
    email = Column(String(), nullable=False, unique=True)
    signup_date = Column(DateTime(), default=datetime.now)

    assigned_issues = relationship("Issue", back_populates="assigned_user")
    assigned_roles = relationship("UserRole", back_populates="user")