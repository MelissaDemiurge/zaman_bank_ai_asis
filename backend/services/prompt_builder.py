"""
Конструктор промптов для Zaman AI
"""
from backend.config import SYSTEM_PROMPT
from typing import List, Dict, Optional
from backend.services.rag_engine import rag_engine
from backend.services.emotion_analyzer import emotion_analyzer

class PromptBuilder:
    """Построение контекстуализированных промптов"""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
    
    def build_chat_prompt(
        self,
        user_message: str,
        emotion_data: Optional[Dict] = None,
        user_goals: Optional[List[Dict]] = None,
        active_challenges: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """
        Построение полного промпта для чата
        
        Args:
            user_message: Сообщение пользователя
            emotion_data: Данные о эмоциях
            user_goals: Список целей пользователя
            active_challenges: Активные челленджи
            conversation_history: История диалога
            
        Returns:
            Список сообщений для API
        """
        # Проверка релевантности вопроса
        is_banking = rag_engine.is_banking_related(user_message)
        
        # Базовый системный промпт
        full_system_prompt = self.system_prompt
        
        # Добавление контекста из RAG
        if is_banking:
            rag_context = rag_engine.get_context(user_message)
            full_system_prompt += f"\n\n{rag_context}"
        else:
            full_system_prompt += "\n\n⚠️ ВНИМАНИЕ: Вопрос не связан с банковской тематикой. Вежливо перенаправь клиента."
        
        # Добавление эмоционального контекста
        if emotion_data:
            emotion_context = emotion_analyzer.get_emotional_context(emotion_data)
            full_system_prompt += f"\n\n{emotion_context}"
        
        # Добавление информации о целях
        if user_goals:
            goals_context = self._build_goals_context(user_goals)
            full_system_prompt += f"\n\n{goals_context}"
        
        # Добавление информации о челленджах
        if active_challenges:
            challenges_context = self._build_challenges_context(active_challenges)
            full_system_prompt += f"\n\n{challenges_context}"
        
        # Формирование списка сообщений
        messages = [{"role": "system", "content": full_system_prompt}]
        
        # Добавление истории диалога (последние 5 сообщений)
        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["message"]
                })
        
        # Добавление текущего сообщения
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _build_goals_context(self, goals: List[Dict]) -> str:
        """Построение контекста целей"""
        if not goals:
            return ""
        
        context = "=== ФИНАНСОВЫЕ ЦЕЛИ КЛИЕНТА ===\n"
        for goal in goals:
            progress = goal.get("progress_percentage", 0)
            context += f"- {goal['title']}: {goal['current_amount']:,.0f} / {goal['target_amount']:,.0f} ₸ ({progress:.1f}%)\n"
        
        context += "\n💡 Учитывай цели клиента при советах!\n"
        return context
    
    def _build_challenges_context(self, challenges: List[Dict]) -> str:
        """Построение контекста челленджей"""
        if not challenges:
            return ""
        
        context = "=== АКТИВНЫЕ ЧЕЛЛЕНДЖИ ===\n"
        for challenge in challenges:
            progress = challenge.get("progress_percentage", 0)
            context += f"- {challenge['title']}: {progress:.1f}% выполнено\n"
        
        context += "\n🎯 Поощряй прогресс в челленджах!\n"
        return context
    
    def build_goal_extraction_prompt(self, user_message: str) -> str:
        """
        Промпт для извлечения финансовой цели из текста
        
        Args:
            user_message: Сообщение пользователя
            
        Returns:
            Промпт для извлечения цели
        """
        return f"""Извлеки финансовую цель из сообщения клиента.

Верни ТОЛЬКО JSON:
{{
    "has_goal": true | false,
    "title": "название цели",
    "target_amount": числовая сумма,
    "deadline_months": количество месяцев (если указано, иначе null)
}}

Сообщение: {user_message}"""
    
    def build_product_recommendation_prompt(
        self, 
        user_message: str, 
        context: str
    ) -> str:
        """
        Промпт для рекомендации продуктов
        
        Args:
            user_message: Сообщение пользователя
            context: Контекст из RAG
            
        Returns:
            Промпт для рекомендации
        """
        return f"""На основе базы знаний Zaman Bank, порекомендуй продукты для клиента.

{context}

Запрос клиента: {user_message}

Верни список подходящих продуктов в формате JSON:
{{
    "products": [
        {{"name": "название продукта", "reason": "почему подходит"}}
    ]
}}"""

# Singleton instance
prompt_builder = PromptBuilder()

