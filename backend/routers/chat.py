"""
Роутер для чата (главный endpoint)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from backend.utils.db import get_db
from backend.models.user import User
from backend.models.conversation import Conversation
from backend.models.emotion_log import EmotionLog
from backend.models.goal import Goal
from backend.models.challenge import Challenge
from backend.services.llm_service import llm_service
from backend.services.rag_engine import rag_engine
from backend.services.emotion_analyzer import emotion_analyzer
from backend.services.prompt_builder import prompt_builder
from backend.services.voice_service import voice_service
from backend.utils.validators import sanitize_input

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: Optional[str] = None
    mode: str = "text"  # "text" или "voice"
    audio_data: Optional[str] = None  # base64 если voice

class ChatResponse(BaseModel):
    response: str
    emotion: dict
    suggested_products: List[str]
    audio_response: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Главный endpoint для чата
    """
    try:
        # 1. Получение или создание пользователя
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            user = User(id=request.user_id, name=f"User_{request.user_id[:8]}")
            db.add(user)
            db.commit()
        
        # 2. Обработка голосового ввода
        user_message = request.message
        if request.mode == "voice" and request.audio_data:
            audio_bytes = voice_service.decode_base64_audio(request.audio_data)
            transcribed = voice_service.speech_to_text(audio_bytes)
            if transcribed:
                user_message = transcribed
            else:
                raise HTTPException(status_code=400, detail="Не удалось распознать речь")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
        
        # Очистка ввода
        user_message = sanitize_input(user_message)
        
        # 3. Анализ эмоций
        emotion_data = emotion_analyzer.analyze(user_message)
        
        # Сохранение эмоции в БД
        emotion_log = EmotionLog(
            user_id=user.id,
            emotion_type=emotion_data["emotion_type"],
            stress_score=emotion_data["stress_score"],
            financial_vulnerability=emotion_data["financial_vulnerability"],
            notes=emotion_data["notes"]
        )
        db.add(emotion_log)
        
        # 4. Получение контекста пользователя
        # Цели
        user_goals = db.query(Goal).filter(
            Goal.user_id == user.id,
            Goal.status == "active"
        ).all()
        goals_data = [
            {
                "title": g.title,
                "target_amount": g.target_amount,
                "current_amount": g.current_amount,
                "progress_percentage": g.progress_percentage
            }
            for g in user_goals
        ]
        
        # Челленджи
        user_challenges = db.query(Challenge).filter(
            Challenge.user_id == user.id,
            Challenge.status == "active"
        ).all()
        challenges_data = [
            {
                "title": c.title,
                "progress_percentage": c.progress_percentage
            }
            for c in user_challenges
        ]
        
        # История диалога
        recent_conversations = db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).order_by(Conversation.timestamp.desc()).limit(10).all()
        
        conversation_history = [
            {"role": c.role, "message": c.message}
            for c in reversed(recent_conversations)
        ]
        
        # 5. Построение промпта
        messages = prompt_builder.build_chat_prompt(
            user_message=user_message,
            emotion_data=emotion_data,
            user_goals=goals_data if goals_data else None,
            active_challenges=challenges_data if challenges_data else None,
            conversation_history=conversation_history
        )
        
        # 6. Получение ответа от LLM
        assistant_response = llm_service.chat_completion(messages)
        
        # 7. Извлечение рекомендованных продуктов (простой поиск по ключевым словам)
        suggested_products = []
        response_lower = assistant_response.lower()
        products_keywords = {
            "Депозит Вакала": ["вакала", "депозит вакала", "овернайт"],
            "Депозит Выгодный": ["выгодный", "депозит выгодный"],
            "Финансирование Мурабаха": ["мурабаха", "финансирование"],
            "Автофинансирование": ["автомобиль", "авто"],
            "Финансирование недвижимости": ["квартира", "недвижимость", "жилье"]
        }
        
        for product, keywords in products_keywords.items():
            if any(kw in response_lower for kw in keywords):
                suggested_products.append(product)
        
        # 8. Сохранение диалога
        # Сообщение пользователя
        user_conv = Conversation(
            user_id=user.id,
            message=user_message,
            role="user",
            emotion_score=emotion_data["stress_score"],
            emotion_type=emotion_data["emotion_type"]
        )
        db.add(user_conv)
        
        # Ответ ассистента
        assistant_conv = Conversation(
            user_id=user.id,
            message=assistant_response,
            role="assistant"
        )
        db.add(assistant_conv)
        
        db.commit()
        
        # 9. Генерация голосового ответа (если требуется)
        audio_response = None
        if request.mode == "voice":
            audio_bytes = voice_service.text_to_speech(assistant_response)
            if audio_bytes:
                audio_response = voice_service.encode_audio_to_base64(audio_bytes)
        
        # 10. Возврат ответа
        return ChatResponse(
            response=assistant_response,
            emotion=emotion_data,
            suggested_products=suggested_products,
            audio_response=audio_response
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{user_id}")
async def get_conversation_history(user_id: str, db: Session = Depends(get_db)):
    """
    Получение истории диалога
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.timestamp.asc()).all()
    
    return {
        "user_id": user_id,
        "conversations": [
            {
                "role": c.role,
                "message": c.message,
                "timestamp": c.timestamp.isoformat(),
                "emotion_type": c.emotion_type,
                "emotion_score": c.emotion_score
            }
            for c in conversations
        ]
    }

