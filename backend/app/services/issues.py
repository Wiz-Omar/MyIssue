from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueUpdate
from app.schemas.role import RoleName
from app.services.auth import UserService
from app.services.user_role import UserRoleService


class IssueService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, issue_data: IssueCreate, current_user: User):
        try:
            issue = Issue(
                title=issue_data.title,
                description=issue_data.description,
                created_by=current_user.id,
                assigned_user_id=None
            )

            self.db.add(issue)
            self.db.commit()
            self.db.refresh(issue)

            if issue_data.assigned_user_id:
                updated_issue: Issue = self.assign_user(issue.id, issue_data.assigned_user_id, current_user)
                return updated_issue
            return issue
        except SQLAlchemyError as e:
            self.db.rollback()
            print('error:', str(e))
            raise HTTPException(status_code=500, detail="Database error")

    def fetch(self, issue_id: UUID) -> Issue:
        try:
            statement = select(Issue).where(Issue.id == issue_id)
            issue: Issue = self.db.execute(statement).scalar_one_or_none()
            if issue is None:
                raise HTTPException(status_code=404, detail="Issue not found")
            return issue
        except SQLAlchemyError as e:
            self.db.rollback()
            print('error:', str(e))
            raise HTTPException(status_code=500, detail="Database error")

    def assign_user(self, issue_id: UUID, user_id: UUID, current_user: User) -> Issue:
        try:
            target_user = UserService(self.db).get_user_by_id(user_id)

            if not target_user:
                raise HTTPException(status_code=404, detail="User not found")
            can_assign = self._can_assign(user_id, current_user)
            if not can_assign:
                raise HTTPException(status_code=403, detail="Not allowed to assign user to issue")
            statement = (update(Issue)
                        .where(Issue.id == issue_id)
                        .values(assigned_user_id=user_id)
                        .returning(Issue)
            )
            updated_issue: Issue = self.db.execute(statement).scalar_one()
            self.db.commit()
            return updated_issue
        except SQLAlchemyError as e:
            self.db.rollback()
            print('error:', str(e))
            raise HTTPException(status_code=500, detail="Database error")

    def update_issue_data(self, issue_id: UUID, issue_data: IssueUpdate, current_user: User) -> Issue:
        try:
            statement = select(Issue).where(Issue.id == issue_id)
            issue: Issue = self.db.execute(statement).scalar_one_or_none()
            if issue is None:
                raise HTTPException(status_code=404, detail="Issue not found")
            if self._can_update(issue, current_user.id): 
                statement = (update(Issue)
                            .where(Issue.id == issue_id)
                            .values(title=issue_data.title, description=issue_data.description)
                            .returning(Issue)
                )
                updated_issue: Issue = self.db.execute(statement).scalar_one()
                self.db.commit()
                return updated_issue
            else:
                raise HTTPException(status_code=403, detail="Not allowed to edit Issue")
        except SQLAlchemyError as e:
            self.db.rollback()
            print('error:', str(e))
            raise HTTPException(status_code=500, detail="Database error")

    def _can_update(self, issue: Issue, current_user_id: UUID) -> bool:
        return (current_user_id == issue.created_by
                or current_user_id == issue.assigned_user_id
                or UserRoleService(self.db).has_role(RoleName.ADMIN, current_user_id)
        )
    def _can_assign(self, target_user_id: UUID, current_user: User) -> bool:
        if UserRoleService(self.db).has_role(RoleName.ADMIN, current_user.id):
            return True
        return target_user_id == current_user.id
