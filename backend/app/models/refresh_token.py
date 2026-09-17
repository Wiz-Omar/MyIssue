from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'), nullable=False)
    token_hash = Column(String(), unique= True, nullable=False)
    created_at = Column(DateTime(), default=datetime.now, nullable=False)
    expires_at = Column(DateTime(), nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
    