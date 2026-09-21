from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.role import RoleName


class UserRoleAssignRequest(BaseModel):
    role: RoleName

class UserRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    role_id: UUID
