from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Issue(Base):
    __tablename__ = 'issues'

    id = Column(Integer(), primary_key=True)
    title = Column(String(), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    assigned_user_id = Column(Integer(), ForeignKey('users.id'))
    assigned_user = relationship("User", back_populates="assigned_issues")
