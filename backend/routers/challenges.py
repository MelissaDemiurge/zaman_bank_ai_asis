"""
Роутер для челленджей (геймификация)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from backend.utils.db import get_db
from backend.models.challenge import Challenge
from backend.models.user import User
from backend.services.gamification import gamification_service

router = APIRouter()

class ChallengeCreate(BaseModel):
    user_id: int
    challenge_type: str  # Тип из шаблонов

class ChallengeUpdate(BaseModel):
    current_value: Optional[float] = None
    status: Optional[str] = None

class ChallengeResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    challenge_type: str
    target_value: Optional[float]
    current_value: float
    progress_percentage: float
    status: str
    reward_title: Optional[str]
    created_at: datetime

@router.post("/challenges", response_model=ChallengeResponse)
async def create_challenge(challenge: ChallengeCreate, db: Session = Depends(get_db)):
    """
    Создание нового челленджа
    """
    # Проверка пользователя
    user = db.query(User).filter(User.id == challenge.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получение шаблона челленджа
    template = None
    for tmpl in gamification_service.CHALLENGE_TEMPLATES.values():
        if tmpl["challenge_type"] == challenge.challenge_type:
            template = tmpl
            break
    
    if not template:
        raise HTTPException(status_code=400, detail="Неизвестный тип челленджа")
    
    # Создание челленджа
    new_challenge = Challenge(
        user_id=challenge.user_id,
        title=template["title"],
        description=template["description"],
        challenge_type=template["challenge_type"],
        target_value=template["target_value"],
        reward_title=template["reward_title"]
    )
    
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    
    return ChallengeResponse(
        id=new_challenge.id,
        title=new_challenge.title,
        description=new_challenge.description,
        challenge_type=new_challenge.challenge_type,
        target_value=new_challenge.target_value,
        current_value=new_challenge.current_value,
        progress_percentage=new_challenge.progress_percentage,
        status=new_challenge.status,
        reward_title=new_challenge.reward_title,
        created_at=new_challenge.created_at
    )

@router.get("/challenges/{user_id}", response_model=List[ChallengeResponse])
async def get_user_challenges(user_id: int, db: Session = Depends(get_db)):
    """
    Получение всех челленджей пользователя
    """
    challenges = db.query(Challenge).filter(Challenge.user_id == user_id).all()
    
    return [
        ChallengeResponse(
            id=c.id,
            title=c.title,
            description=c.description,
            challenge_type=c.challenge_type,
            target_value=c.target_value,
            current_value=c.current_value,
            progress_percentage=c.progress_percentage,
            status=c.status,
            reward_title=c.reward_title,
            created_at=c.created_at
        )
        for c in challenges
    ]

@router.patch("/challenges/{challenge_id}")
async def update_challenge(
    challenge_id: int, 
    update: ChallengeUpdate, 
    db: Session = Depends(get_db)
):
    """
    Обновление прогресса челленджа
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Челлендж не найден")
    
    if update.current_value is not None:
        challenge.current_value = update.current_value
        
        # Автоматическое завершение
        if challenge.current_value >= challenge.target_value:
            challenge.status = "completed"
            challenge.completed_at = datetime.utcnow()
            
            # Генерация поздравления
            completion_message = gamification_service.generate_completion_message({
                "title": challenge.title,
                "reward_title": challenge.reward_title
            })
            
            db.commit()
            return {
                "message": "Челлендж выполнен!",
                "completion_message": completion_message,
                "reward": challenge.reward_title
            }
    
    if update.status is not None:
        challenge.status = update.status
    
    db.commit()
    
    return {"message": "Челлендж обновлён", "challenge_id": challenge_id}

@router.get("/challenges/templates/list")
async def get_challenge_templates():
    """
    Получение доступных шаблонов челленджей
    """
    return {
        "templates": [
            {
                "challenge_type": template["challenge_type"],
                "title": template["title"],
                "description": template["description"],
                "reward_title": template["reward_title"]
            }
            for template in gamification_service.CHALLENGE_TEMPLATES.values()
        ]
    }

