"""
Роутер для управления финансовыми целями
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from backend.utils.db import get_db
from backend.models.goal import Goal
from backend.models.user import User

router = APIRouter()

class GoalCreate(BaseModel):
    user_id: str
    title: str
    target_amount: float
    deadline_months: Optional[int] = None

class GoalUpdate(BaseModel):
    current_amount: Optional[float] = None
    status: Optional[str] = None

class GoalResponse(BaseModel):
    id: str
    title: str
    target_amount: float
    current_amount: float
    progress_percentage: float
    deadline_months: Optional[int]
    status: str
    created_at: datetime

@router.post("/goals", response_model=GoalResponse)
async def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    """
    Создание новой финансовой цели
    """
    # Проверка пользователя
    user = db.query(User).filter(User.id == goal.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Создание цели
    new_goal = Goal(
        user_id=goal.user_id,
        title=goal.title,
        target_amount=goal.target_amount,
        deadline_months=goal.deadline_months
    )
    
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    return GoalResponse(
        id=str(new_goal.id),
        title=new_goal.title,
        target_amount=new_goal.target_amount,
        current_amount=new_goal.current_amount,
        progress_percentage=new_goal.progress_percentage,
        deadline_months=new_goal.deadline_months,
        status=new_goal.status,
        created_at=new_goal.created_at
    )

@router.get("/goals/{user_id}", response_model=List[GoalResponse])
async def get_user_goals(user_id: str, db: Session = Depends(get_db)):
    """
    Получение всех целей пользователя
    """
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    
    return [
        GoalResponse(
            id=str(g.id),
            title=g.title,
            target_amount=g.target_amount,
            current_amount=g.current_amount,
            progress_percentage=g.progress_percentage,
            deadline_months=g.deadline_months,
            status=g.status,
            created_at=g.created_at
        )
        for g in goals
    ]

@router.patch("/goals/{goal_id}")
async def update_goal(goal_id: str, update: GoalUpdate, db: Session = Depends(get_db)):
    """
    Обновление цели
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    if update.current_amount is not None:
        goal.current_amount = update.current_amount
        
        # Автоматическое завершение при достижении
        if goal.current_amount >= goal.target_amount:
            goal.status = "completed"
            goal.completed_at = datetime.utcnow()
    
    if update.status is not None:
        goal.status = update.status
        if update.status == "completed":
            goal.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Цель обновлена", "goal_id": goal_id}

@router.delete("/goals/{goal_id}")
async def delete_goal(goal_id: str, db: Session = Depends(get_db)):
    """
    Удаление цели
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    db.delete(goal)
    db.commit()
    
    return {"message": "Цель удалена", "goal_id": goal_id}

