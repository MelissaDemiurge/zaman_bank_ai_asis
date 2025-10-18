"""
Роутер для эмоционального профиля и проактивных уведомлений
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.utils.db import get_db
from backend.models.user import User
from backend.models.emotion_log import EmotionLog
from backend.models.conversation import Conversation
from backend.models.goal import Goal
from backend.models.challenge import Challenge
from backend.services.proactive_agent import proactive_agent

router = APIRouter()

class EmotionalProfileResponse(BaseModel):
    user_id: str
    average_stress_score: float
    dominant_emotion: str
    financial_vulnerability_trend: str
    recent_emotions: List[dict]

@router.get("/profile/{user_id}", response_model=EmotionalProfileResponse)
async def get_emotional_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Получение эмоционального профиля пользователя
    """
    # Проверка пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получение эмоций за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    emotions = db.query(EmotionLog).filter(
        EmotionLog.user_id == user_id,
        EmotionLog.timestamp >= thirty_days_ago
    ).all()
    
    if not emotions:
        return EmotionalProfileResponse(
            user_id=user_id,
            average_stress_score=3.0,
            dominant_emotion="спокойствие",
            financial_vulnerability_trend="низкая",
            recent_emotions=[]
        )
    
    # Расчёт статистики
    avg_stress = sum(e.stress_score for e in emotions) / len(emotions)
    
    # Доминирующая эмоция
    emotion_counts = {}
    for e in emotions:
        emotion_counts[e.emotion_type] = emotion_counts.get(e.emotion_type, 0) + 1
    dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
    
    # Тренд уязвимости
    vulnerability_map = {"низкая": 1, "средняя": 2, "высокая": 3}
    recent_vulnerabilities = [
        vulnerability_map.get(e.financial_vulnerability, 1) 
        for e in emotions[-10:] 
        if e.financial_vulnerability
    ]
    avg_vulnerability = sum(recent_vulnerabilities) / len(recent_vulnerabilities) if recent_vulnerabilities else 1
    
    vulnerability_trend = "низкая"
    if avg_vulnerability >= 2.5:
        vulnerability_trend = "высокая"
    elif avg_vulnerability >= 1.5:
        vulnerability_trend = "средняя"
    
    # Последние эмоции
    recent = [
        {
            "emotion_type": e.emotion_type,
            "stress_score": e.stress_score,
            "timestamp": e.timestamp.isoformat()
        }
        for e in emotions[-10:]
    ]
    
    return EmotionalProfileResponse(
        user_id=user_id,
        average_stress_score=round(avg_stress, 1),
        dominant_emotion=dominant_emotion,
        financial_vulnerability_trend=vulnerability_trend,
        recent_emotions=recent
    )

@router.post("/proactive/check/{user_id}")
async def check_proactive_triggers(user_id: str, db: Session = Depends(get_db)):
    """
    Проверка триггеров для проактивных уведомлений
    """
    # Проверка пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Последняя активность
    last_conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.role == "user"
    ).order_by(Conversation.timestamp.desc()).first()
    
    last_conv_date = last_conversation.timestamp if last_conversation else None
    
    # Последние эмоции
    recent_emotions = db.query(EmotionLog).filter(
        EmotionLog.user_id == user_id
    ).order_by(EmotionLog.timestamp.desc()).limit(5).all()
    
    emotions_data = [
        {
            "stress_score": e.stress_score,
            "emotion_type": e.emotion_type,
            "timestamp": e.timestamp
        }
        for e in recent_emotions
    ]
    
    # Цели
    goals = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.status == "active"
    ).all()
    
    goals_data = [
        {
            "title": g.title,
            "progress_percentage": g.progress_percentage,
            "created_at": g.created_at,
            "deadline_months": g.deadline_months
        }
        for g in goals
    ]
    
    # Челленджи
    challenges = db.query(Challenge).filter(
        Challenge.user_id == user_id,
        Challenge.status == "active"
    ).all()
    
    challenges_data = [
        {
            "title": c.title,
            "progress_percentage": c.progress_percentage
        }
        for c in challenges
    ]
    
    # Проверка триггеров
    notification = proactive_agent.check_triggers(
        user_id=user_id,
        last_conversation_date=last_conv_date,
        recent_emotions=emotions_data,
        goals=goals_data,
        challenges=challenges_data
    )
    
    if notification:
        return {
            "has_notification": True,
            "message": notification
        }
    else:
        return {
            "has_notification": False,
            "message": None
        }

