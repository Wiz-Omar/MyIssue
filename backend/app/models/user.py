import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(), nullable=False)
    last_name = Column(String(),  nullable=False)
    email = Column(String(), nullable=False, unique=True)
    password_hash = Column(String(), nullable=False)
    signup_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    assigned_issues = relationship("Issue", back_populates="assigned_user")
    assigned_roles = relationship("UserRole", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    