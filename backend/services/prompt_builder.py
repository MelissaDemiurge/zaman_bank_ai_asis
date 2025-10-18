"""
Конструктор промптов для Zaman AI
"""
from backend.config import SYSTEM_PROMPT
from backend.prompts import get_intent_detection_prompt
from typing import List, Dict, Optional, Any
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
            
            # Дополнительная инструкция в зависимости от стресса
            stress_score = emotion_data.get("stress_score", 0)
            
            if stress_score <= 4:
                full_system_prompt += """

✅ КЛИЕНТ СПОКОЕН (стресс низкий)

НЕ УТЕШАЙ! НЕ "понимаю как это важно/тревожно".
Просто будь дружелюбным помощником.
Деловой тон с лёгкостью.

Пример: "Отличная цель! Давайте подумаем, как её достичь."
"""
            elif stress_score >= 7:
                full_system_prompt += """

🚨 КРИТИЧЕСКИ ВАЖНО: Клиент в сильном стрессе!

Твой ответ ОБЯЗАТЕЛЬНО должен начинаться с:
1. Тёплых слов поддержки (как друг, не как робот)
2. Признания что чувства клиента нормальны
3. Заверения что вы вместе найдёте решение

ТОЛЬКО ПОТОМ мягко предложи обсудить решение.
НЕ ПИШИ про банковские продукты в первых 2-3 предложениях!

Пример начала: "Я понимаю, как тяжело сейчас. Финансовые переживания — это действительно непросто, и ваши чувства совершенно естественны. Знаете, многие проходят через это, и важно, что вы не закрываетесь, а ищете выход. Я рядом, чтобы помочь."
"""
            elif stress_score >= 5:
                full_system_prompt += """

📌 ВНИМАНИЕ: Клиент немного обеспокоен (стресс средний).

Будь чуть мягче, но не "терапевтируй".
Просто покажи понимание и переходи к решениям.

Пример: "Понимаю, что это важный вопрос. Давайте разберёмся."
"""
        
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
    
    def build_intent_detection_prompt(
        self, 
        user_message: str,
        user_goals: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Промпт для определения намерений пользователя (умный анализ вместо ключевых слов)
        
        Args:
            user_message: Сообщение пользователя
            user_goals: Текущие цели пользователя (для контекста)
            
        Returns:
            Промпт для определения намерения
        """
        return get_intent_detection_prompt(user_message, user_goals)
    
    def build_goal_extraction_prompt(self, user_message: str) -> str:
        """
        Промпт для извлечения финансовой цели из текста (LEGACY - используется как fallback)
        
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

