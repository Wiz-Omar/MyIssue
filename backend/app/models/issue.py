import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Issue(Base):
    __tablename__ = 'issues'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_issues")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id], back_populates="assigned_issues")
