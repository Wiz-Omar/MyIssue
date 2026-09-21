from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class IssueCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_user_id: UUID | None = None

class IssueUpdate(BaseModel):
    title: str
    description: str

class IssueResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    title: str
    description: str | None = None
    assigned_user_id: UUID | None = None

class IssueAssignRequest(BaseModel):
    user_id: UUID
