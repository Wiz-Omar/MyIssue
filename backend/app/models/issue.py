from datetime import datetime

from app.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class Issue(Base):
    __tablename__ = 'issues'

    id = Column(Integer(), primary_key=True)
    title = Column(String(), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    assigned_user_id = Column(Integer(), ForeignKey('users.id'))
    assigned_user = relationship("User", back_populates="assigned_issues")
