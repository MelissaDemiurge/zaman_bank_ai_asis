"""
Роутер для чата (главный endpoint)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

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
from backend.services.ai_analytics import ai_analytics
from backend.utils.validators import sanitize_input
from backend.prompts import (
    get_no_goals_deletion_prompt,
    get_goal_not_found_prompt,
    get_unspecified_goal_deletion_prompt,
    get_past_deadline_goal_prompt,
    get_create_goal_suggestion_prompt,
    get_delete_goal_confirmation_prompt
)

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    message: Optional[str] = None
    mode: str = "text"  # "text" или "voice"
    audio_data: Optional[str] = None  # base64 если voice

class ChatResponse(BaseModel):
    response: str
    emotion: dict
    suggested_products: List[str]
    audio_response: Optional[str] = None
    suggested_goal: Optional[dict] = None  # Предлагаемая цель
    goal_action: Optional[str] = None  # "create", "delete", None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Главный endpoint для чата
    """
    try:
        # 1. Получение или создание пользователя
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            # Создаем пользователя с переданным ID
            user = User(id=request.user_id, name=f"User_{request.user_id}")
            db.add(user)
            db.commit()
            db.refresh(user)
        
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
        
        # 5. Получение финансового контекста из транзакций
        financial_context = None
        try:
            financial_context = ai_analytics.get_financial_context_for_chat(user.id, db)
        except Exception as e:
            print(f"Could not load financial context: {e}")
        
        # 6. Построение промпта
        messages = prompt_builder.build_chat_prompt(
            user_message=user_message,
            emotion_data=emotion_data,
            user_goals=goals_data if goals_data else None,
            active_challenges=challenges_data if challenges_data else None,
            conversation_history=conversation_history,
            financial_context=financial_context
        )
        
        # 7. Определение намерений пользователя через LLM (умный анализ вместо ключевых слов)
        suggested_goal_data = None
        goal_action = None
        intent_data = {}  # Инициализация для доступности вне try блока
        
        try:
            # LLM анализирует намерение пользователя
            # Передаем ВСЕ цели пользователя (не только active) для контекста
            all_user_goals = db.query(Goal).filter(Goal.user_id == user.id).all()
            all_goals_data = [
                {
                    "title": g.title,
                    "target_amount": g.target_amount,
                    "current_amount": g.current_amount,
                    "progress_percentage": g.progress_percentage,
                    "status": g.status
                }
                for g in all_user_goals
            ]
            print(f"[DEBUG] Passing {len(all_goals_data)} goals to intent detection")
            for goal in all_goals_data:
                print(f"[DEBUG] Goal: {goal['title']} (status: {goal['status']})")
            intent_data = llm_service.detect_intent(user_message, all_goals_data)
            
            # Проверяем уверенность (confidence) - фильтруем неуверенные определения
            confidence_threshold = 0.7  # Порог уверенности
            
            if intent_data.get('confidence', 0) >= confidence_threshold:
                
                # Намерение: создать финансовую цель
                if intent_data['intent'] == 'create_goal':
                    goal_data = intent_data.get('goal_data')
                    reasoning = intent_data.get('reasoning', '')
                    
                    if goal_data and goal_data.get('title'):
                        # Проверка: если дедлайн в прошлом (deadline_months = null + reasoning содержит "прошел"/"невозможно")
                        # то НЕ предлагаем создать цель, а только предупреждаем
                        deadline_months = goal_data.get('deadline_months')
                        is_past_deadline = (
                            deadline_months is None and 
                            ('прошел' in reasoning.lower() or 'невозможно' in reasoning.lower())
                        )
                        
                        if not is_past_deadline:
                            # Нормальная цель - предлагаем создать
                            suggested_goal_data = {
                                "title": goal_data['title'],
                                "target_amount": goal_data.get('target_amount'),
                                "deadline_months": goal_data.get('deadline_months'),
                                "action": "create",
                                "reasoning": reasoning
                            }
                            goal_action = "create"
                            print(f"[Goal Detection] CREATE: {goal_data['title']} "
                                  f"(amount: {goal_data.get('target_amount')}, "
                                  f"months: {goal_data.get('deadline_months')})")
                        else:
                            # Дедлайн в прошлом - только предупреждаем, но НЕ создаем suggested_goal_data
                            suggested_goal_data = {
                                "title": goal_data['title'],
                                "target_amount": goal_data.get('target_amount'),
                                "deadline_months": None,
                                "action": "create",
                                "reasoning": reasoning
                            }
                            goal_action = "create"
                            print(f"[Goal Detection] INVALID DEADLINE: {goal_data['title']} - {reasoning}")
                
                # Намерение: удалить финансовую цель
                elif intent_data['intent'] == 'delete_goal':
                    goal_to_delete = intent_data.get('goal_to_delete')
                    
                    # КРИТИЧЕСКИ ВАЖНО: проверяем что у пользователя ЕСТЬ цели
                    if not user_goals:
                        # НЕТ целей вообще - добавим специальную инструкцию
                        messages.append({"role": "system", "content": get_no_goals_deletion_prompt()})
                        print(f"[Goal Detection] DELETE intent but user has NO goals at all")
                    
                    elif goal_to_delete:
                        # Есть цели - ищем нужную
                        goal_found = False
                        for goal_obj in user_goals:
                            # Проверяем совпадение в обе стороны
                            if (goal_to_delete.lower() in goal_obj.title.lower() or 
                                goal_obj.title.lower() in goal_to_delete.lower()):
                                suggested_goal_data = {
                                    "id": str(goal_obj.id),
                                    "title": goal_obj.title,
                                    "action": "delete",
                                    "reasoning": intent_data.get('reasoning', '')
                                }
                                goal_action = "delete"
                                goal_found = True
                                print(f"[Goal Detection] DELETE: {goal_obj.title}")
                                break
                        
                        # Если цель не найдена среди существующих
                        if not goal_found and intent_data.get('confidence', 0) >= 0.85:
                            print(f"[Goal Detection] DELETE intent for '{goal_to_delete}' but NOT found in goals")
                            # Добавляем инструкцию что такой цели нет
                            messages.append({
                                "role": "system", 
                                "content": get_goal_not_found_prompt(goal_to_delete, goals_data)
                            })
                    
                    else:
                        # Есть цели, но пользователь НЕ указал конкретное название
                        print(f"[Goal Detection] DELETE intent but NO specific goal name provided")
                        messages.append({
                            "role": "system", 
                            "content": get_unspecified_goal_deletion_prompt(goals_data)
                        })
            
            else:
                # Низкая уверенность - логируем для анализа
                print(f"[Intent Detection] Low confidence ({intent_data.get('confidence', 0):.2f}) - "
                      f"Intent '{intent_data.get('intent')}' ignored")
        
        except Exception as e:
            print(f"Error in intent detection: {e}")
            # При ошибке система продолжит работу без определения намерения
        
        # 7. Добавляем инструкцию для LLM о предложении цели (если обнаружена)
        if suggested_goal_data and goal_action == "create":
            # Проверка на невозможный дедлайн (если deadline_months = null и reasoning содержит информацию о прошлой дате)
            reasoning = intent_data.get('reasoning', '')
            deadline_months = suggested_goal_data.get('deadline_months')
            
            if deadline_months is None and ('прошел' in reasoning.lower() or 'невозможно' in reasoning.lower()):
                # Дедлайн в прошлом - AI должен предупредить
                goal_instruction = get_past_deadline_goal_prompt(suggested_goal_data['title'], reasoning)
            else:
                # Нормальная цель - предлагаем добавить
                goal_instruction = get_create_goal_suggestion_prompt(suggested_goal_data['title'])
            messages.append({"role": "system", "content": goal_instruction})
        
        if suggested_goal_data and goal_action == "delete":
            # Для удаления - ВАЖНО: НЕ говорим что удалили, а только ПРЕДЛАГАЕМ
            messages.append({
                "role": "system", 
                "content": get_delete_goal_confirmation_prompt(suggested_goal_data['title'])
            })
        
        # 8. Получение ответа от LLM
        assistant_response = llm_service.chat_completion(messages)
        
        # 9. Извлечение рекомендованных продуктов (простой поиск по ключевым словам)
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
        
        # 10. Сохранение диалога
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
        
        # 11. Генерация голосового ответа (если требуется)
        audio_response = None
        if request.mode == "voice":
            audio_bytes = voice_service.text_to_speech(assistant_response)
            if audio_bytes:
                audio_response = voice_service.encode_audio_to_base64(audio_bytes)
        
        # 12. Возврат ответа
        return ChatResponse(
            response=assistant_response,
            emotion=emotion_data,
            suggested_products=suggested_products,
            audio_response=audio_response,
            suggested_goal=suggested_goal_data,
            goal_action=goal_action
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{user_id}")
async def get_conversation_history(user_id: int, db: Session = Depends(get_db)):
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

class GoalActionRequest(BaseModel):
    user_id: int
    title: str
    target_amount: Optional[float] = None
    deadline_months: Optional[int] = None

@router.post("/goal/create")
async def create_goal(request: GoalActionRequest, db: Session = Depends(get_db)):
    """
    Создание финансовой цели (после подтверждения пользователем)
    """
    try:
        # Проверка пользователя
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Создание цели
        new_goal = Goal(
            user_id=user.id,
            title=request.title,
            target_amount=request.target_amount or 0,
            deadline_months=request.deadline_months
        )
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        
        return {
            "success": True,
            "message": f"✅ Цель '{request.title}' успешно добавлена!",
            "goal": {
                "id": str(new_goal.id),
                "title": new_goal.title,
                "target_amount": new_goal.target_amount,
                "deadline_months": new_goal.deadline_months
            }
        }
    
    except Exception as e:
        print(f"Error creating goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/goal/delete/{user_id}/{goal_id}")
async def delete_goal(user_id: int, goal_id: int, db: Session = Depends(get_db)):
    """
    Удаление финансовой цели
    """
    try:
        # Проверка пользователя
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Поиск цели
        goal = db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user.id
        ).first()
        
        if not goal:
            raise HTTPException(status_code=404, detail="Цель не найдена")
        
        goal_title = goal.title
        db.delete(goal)
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ Цель '{goal_title}' успешно удалена!"
        }
    
    except Exception as e:
        print(f"Error deleting goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

