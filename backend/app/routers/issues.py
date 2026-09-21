from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.issue import Issue
from app.models.user import User
from app.schemas.issue import (
    IssueAssignRequest,
    IssueCreate,
    IssueResponse,
    IssueUpdate,
)
from app.services.issues import IssueService

router = APIRouter(prefix="/issues", tags=["issues"])

@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(issue_data: IssueCreate, 
                       current_user: Annotated[User, Depends(get_current_user)], 
                       db: Session = Depends(get_db) #noqa: B008
):
    issueService = IssueService(db)
    issue: Issue = issueService.create(issue_data, current_user)
    return issue

@router.get("/{issue_id}", response_model=IssueResponse, status_code=status.HTTP_200_OK)
async def get_issue(issue_id: UUID, 
                    _: Annotated[User, Depends(get_current_user)], #dependency added to require authentication
                    db: Session = Depends(get_db)): #noqa: B008
    issueService = IssueService(db)
    issue: Issue = issueService.fetch(issue_id)
    return issue

@router.patch("/{issue_id}", response_model=IssueResponse, status_code=status.HTTP_200_OK)
async def update_issue(issue_id: UUID, issue_data: IssueUpdate, 
                        current_user: Annotated[User, Depends(get_current_user)], 
                        db: Session = Depends(get_db) #noqa: B008
):
    issueService = IssueService(db)
    updated_issue: Issue = issueService.update_issue_data(issue_id, issue_data, current_user)
    return updated_issue

@router.patch("/{issue_id}/assign", response_model=IssueResponse, status_code=status.HTTP_200_OK)
async def assign_user(issue_id: UUID, issue_data: IssueAssignRequest, 
                      current_user: Annotated[User, Depends(get_current_user)], 
                      db: Session = Depends(get_db) #noqa: B008
):
    issueService = IssueService(db)
    updated_issue: Issue = issueService.assign_user(issue_id, issue_data.user_id, current_user)
    return updated_issue
