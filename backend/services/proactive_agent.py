"""
Проактивный агент для отправки уведомлений
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from backend.config import (
    PROACTIVE_INACTIVITY_DAYS,
    PROACTIVE_GOAL_DEADLINE_DAYS,
    EMOTION_STRESS_THRESHOLD
)
from backend.services.llm_service import llm_service

class ProactiveAgent:
    """Проактивные уведомления клиентам"""
    
    def check_triggers(
        self,
        user_id: str,
        last_conversation_date: Optional[datetime] = None,
        recent_emotions: Optional[List[Dict]] = None,
        goals: Optional[List[Dict]] = None,
        challenges: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        Проверка триггеров для проактивного сообщения
        
        Args:
            user_id: ID пользователя
            last_conversation_date: Дата последнего сообщения
            recent_emotions: Последние записи эмоций
            goals: Цели пользователя
            challenges: Челленджи пользователя
            
        Returns:
            Текст уведомления или None
        """
        # Триггер 1: Высокий стресс 2+ дня подряд
        if recent_emotions and len(recent_emotions) >= 2:
            stress_trigger = self._check_stress_trigger(recent_emotions)
            if stress_trigger:
                return stress_trigger
        
        # Триггер 2: Цель близка к дедлайну
        if goals:
            goal_trigger = self._check_goal_deadline_trigger(goals)
            if goal_trigger:
                return goal_trigger
        
        # Триггер 3: Неактивность > N дней
        if last_conversation_date:
            inactivity_trigger = self._check_inactivity_trigger(
                last_conversation_date, 
                challenges
            )
            if inactivity_trigger:
                return inactivity_trigger
        
        # Триггер 4: Челлендж близок к завершению
        if challenges:
            challenge_trigger = self._check_challenge_completion_trigger(challenges)
            if challenge_trigger:
                return challenge_trigger
        
        return None
    
    def _check_stress_trigger(self, recent_emotions: List[Dict]) -> Optional[str]:
        """Проверка триггера стресса"""
        # Берём последние 2 записи
        if len(recent_emotions) < 2:
            return None
        
        recent_two = recent_emotions[-2:]
        high_stress_count = sum(
            1 for e in recent_two 
            if e.get("stress_score", 0) >= EMOTION_STRESS_THRESHOLD
        )
        
        if high_stress_count >= 2:
            return """Я заметил, что вы переживаете сложный период. 

Финансовый стресс — это естественно, но я здесь, чтобы помочь. Хотите обсудить вашу финансовую ситуацию? Вместе мы найдём решение.

Также могу предложить альтернативные способы борьбы со стрессом без трат."""
        
        return None
    
    def _check_goal_deadline_trigger(self, goals: List[Dict]) -> Optional[str]:
        """Проверка триггера дедлайна цели"""
        now = datetime.utcnow()
        
        for goal in goals:
            if goal.get("status") != "active":
                continue
            
            # Расчёт дедлайна
            created_at = goal.get("created_at")
            deadline_months = goal.get("deadline_months")
            
            if not created_at or not deadline_months:
                continue
            
            deadline = created_at + timedelta(days=deadline_months * 30)
            days_until_deadline = (deadline - now).days
            
            # Если осталось 2 месяца
            if 0 < days_until_deadline <= PROACTIVE_GOAL_DEADLINE_DAYS:
                title = goal.get("title", "Ваша цель")
                progress = goal.get("progress_percentage", 0)
                
                return f"""Напоминание о цели: '{title}'

До дедлайна осталось {days_until_deadline} дней, а прогресс — {progress:.1f}%.

Хотите, я помогу оптимизировать стратегию накоплений? Например, депозит 'Выгодный' с доходностью 17% годовых может ускорить достижение цели."""
        
        return None
    
    def _check_inactivity_trigger(
        self, 
        last_conversation_date: datetime,
        challenges: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """Проверка триггера неактивности"""
        now = datetime.utcnow()
        days_inactive = (now - last_conversation_date).days
        
        if days_inactive >= PROACTIVE_INACTIVITY_DAYS:
            if challenges:
                return f"""Давно не виделись! Как продвигаются ваши челленджи?

Я здесь, если нужна помощь или совет по финансам."""
            else:
                return """Привет! Давно не общались.

Если у вас появились финансовые вопросы или новые цели — я всегда на связи!"""
        
        return None
    
    def _check_challenge_completion_trigger(
        self, 
        challenges: List[Dict]
    ) -> Optional[str]:
        """Проверка близости завершения челленджа"""
        for challenge in challenges:
            if challenge.get("status") != "active":
                continue
            
            progress = challenge.get("progress_percentage", 0)
            
            # Если прогресс > 80%
            if 80 <= progress < 100:
                title = challenge.get("title", "Челлендж")
                return f"""Отличная работа! 🎉

Ваш челлендж '{title}' почти выполнен ({progress:.1f}%). 

Ещё немного — и вы получите награду! Продолжайте в том же духе."""
        
        return None
    
    def generate_personalized_advice(
        self, 
        user_context: str,
        advice_type: str = "general"
    ) -> str:
        """
        Генерация персонализированного совета
        
        Args:
            user_context: Контекст о пользователе
            advice_type: Тип совета (general, stress, goal, etc.)
            
        Returns:
            Персонализированный совет
        """
        prompts = {
            "stress": f"""Создай короткий (2-3 предложения) совет клиенту Zaman Bank по борьбе с финансовым стрессом.

Контекст: {user_context}

Требования:
- Предложи альтернативы стресс-покупкам
- Упомяни полезные привычки
- Тон: эмпатичный, поддерживающий""",
            
            "goal": f"""Создай короткий совет по достижению финансовой цели.

Контекст: {user_context}

Требования:
- Конкретные шаги
- Можно упомянуть продукты Zaman Bank
- Тон: мотивирующий""",
            
            "general": f"""Создай короткое мотивирующее сообщение клиенту о финансовом планировании.

Контекст: {user_context}

Тон: дружелюбный, профессиональный"""
        }
        
        prompt = prompts.get(advice_type, prompts["general"])
        
        try:
            advice = llm_service.simple_query(prompt)
            return advice
        except:
            return "Продолжайте следовать своему финансовому плану. Я всегда готов помочь!"

# Singleton instance
proactive_agent = ProactiveAgent()

