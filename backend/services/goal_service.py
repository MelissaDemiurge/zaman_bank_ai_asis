"""
GoalService: domain-level API for creating and deleting goals from HTTP layer.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from backend.services.repositories import (
    users_repo,
    goals_repo,
)
from backend.models.goal import Goal


class GoalService:
    def create_goal(
        self,
        db: Session,
        *,
        user_id: str,
        title: str,
        target_amount: Optional[float],
        deadline_months: Optional[int],
    ) -> Dict[str, Any]:
        user = users_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("user_not_found")

        goal = goals_repo.create(
            db,
            user_id=str(user.id),
            title=title,
            target_amount=float(target_amount or 0),
            deadline_months=deadline_months,
        )

        return {
            "success": True,
            "message": f"Цель '{title}' успешно добавлена!",
            "goal": {
                "id": str(goal.id),
                "title": goal.title,
                "target_amount": goal.target_amount,
                "deadline_months": goal.deadline_months,
            },
        }

    def delete_goal(self, db: Session, *, user_id: str, goal_id: str) -> Dict[str, Any]:
        user = users_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("user_not_found")

        goal = goals_repo.get_by_id_for_user(db, user_id=str(user.id), goal_id=goal_id)
        if not goal:
            raise ValueError("goal_not_found")

        title = goal.title
        goals_repo.delete(db, goal)
        return {"success": True, "message": f"Цель '{title}' успешно удалена!"}

    # Additional helpers for dedicated Goals router
    def create_goal_model(
        self,
        db: Session,
        *,
        user_id: str,
        title: str,
        target_amount: float,
        deadline_months: Optional[int],
    ) -> Goal:
        user = users_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("user_not_found")
        return goals_repo.create(
            db,
            user_id=str(user.id),
            title=title,
            target_amount=float(target_amount),
            deadline_months=deadline_months,
        )

    def list_goals_by_user(self, db: Session, *, user_id: str) -> List[Goal]:
        user = users_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("user_not_found")
        return goals_repo.list_by_user(db, str(user.id))

    def update_goal(
        self,
        db: Session,
        *,
        goal_id: str,
        current_amount: Optional[float] = None,
        status: Optional[str] = None,
    ) -> Goal:
        goal = goals_repo.get_by_id(db, goal_id)
        if not goal:
            raise ValueError("goal_not_found")

        if current_amount is not None:
            goal.current_amount = float(current_amount)
            if goal.target_amount and goal.current_amount >= goal.target_amount:
                goal.status = "completed"
                from datetime import datetime
                goal.completed_at = datetime.utcnow()

        if status is not None:
            goal.status = status
            if status == "completed":
                from datetime import datetime
                goal.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(goal)
        return goal

    def delete_goal_by_id(self, db: Session, *, goal_id: str) -> None:
        goal = goals_repo.get_by_id(db, goal_id)
        if not goal:
            raise ValueError("goal_not_found")
        goals_repo.delete(db, goal)


goal_service = GoalService()


