import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.models.refresh_token import RefreshToken


class RefreshTokenService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID) -> str:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_token(raw_token) # Normal SHA256 hash is sufficient since raw_token is already random

        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        self.db.add(refresh_token)
        self.db.commit()

        return raw_token

    def revoke(self, raw_token: str):
        token_hash = hash_token(raw_token)
        statement = delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
        self.db.execute(statement)
        self.db.commit()

    def validate_and_rotate(self, raw_token: str) -> UUID:
        token_hash = hash_token(raw_token)
        statement = select(RefreshToken).filter_by(token_hash=token_hash)
        stored: RefreshToken | None = self.db.execute(statement).scalar_one_or_none()
        if not stored or stored.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        user_id: UUID = stored.user_id
        self.db.delete(stored)
        self.db.commit()
        return user_id
