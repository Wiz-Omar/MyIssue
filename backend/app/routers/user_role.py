from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.role import RoleName
from app.schemas.user_role import UserRoleAssignRequest, UserRoleResponse
from app.services.user_role import UserRoleService

router = APIRouter(prefix="/users", tags=["user-roles"])

@router.post(
    "/{user_id}/roles",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_user_role(
    user_id: UUID,
    role_data: UserRoleAssignRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),  #noqa: B008
):
    user_role_service: UserRoleService = UserRoleService(db)
    if not user_role_service.has_role(RoleName.ADMIN, current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed to assign roles")

    return user_role_service.add_user_role(role_data.role, user_id)
