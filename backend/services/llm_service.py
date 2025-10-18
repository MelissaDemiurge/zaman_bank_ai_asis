"""
Сервис для работы с LLM (gpt-5-mini)
"""
from openai import OpenAI
from backend.config import (
    OPENAI_API_KEY, 
    OPENAI_BASE_URL, 
    GPT_MODEL,
    EMBEDDING_MODEL,
    MAX_TOKENS_CHAT,
    MAX_TOKENS_ANALYTICS,
    MAX_TOKENS_SHORT
)
from typing import List, Dict, Any, Optional
import json

class LLMService:
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        self.model = GPT_MODEL
        self.embedding_model = EMBEDDING_MODEL
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = None
    ) -> str:
        """
        Отправка запроса к gpt-5-mini
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            temperature: Температура генерации (игнорируется для gpt-5-mini)
            max_tokens: Максимальное количество токенов (по умолчанию MAX_TOKENS_CHAT)
            
        Returns:
            Ответ от модели
        """
        # Используем дефолтное значение из конфига если не указано
        if max_tokens is None:
            max_tokens = MAX_TOKENS_CHAT
            
        try:
            # GPT-5-mini не поддерживает temperature, используем только основные параметры
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in chat_completion: {e}")
            return "Извините, произошла ошибка. Попробуйте ещё раз."
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Получение embedding вектора для текста
        
        Args:
            text: Текст для векторизации
            
        Returns:
            Вектор embedding
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error in get_embedding: {e}")
            return []
    
    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Извлечение JSON из ответа модели
        
        Args:
            response: Текстовый ответ от модели
            
        Returns:
            Словарь с данными или пустой словарь при ошибке
        """
        try:
            # Попытка парсинга всего ответа как JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Поиск JSON в тексте между ``` или {}
            import re
            json_pattern = r'\{[^}]+\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0])
                except:
                    pass
        return {}
    
    def simple_query(
        self, 
        prompt: str, 
        system_prompt: str = None,
        max_tokens: int = None
    ) -> str:
        """
        Простой запрос к модели
        
        Args:
            prompt: Пользовательский промпт
            system_prompt: Системный промпт (опционально)
            max_tokens: Максимальное количество токенов (опционально)
            
        Returns:
            Ответ модели
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(messages, max_tokens=max_tokens)
    
    def detect_intent(self, user_message: str, user_goals: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Определение намерения пользователя через LLM (умный анализ вместо ключевых слов)
        
        Args:
            user_message: Сообщение пользователя
            user_goals: Текущие цели пользователя (для контекста)
            
        Returns:
            Словарь с данными о намерении:
            {
                "intent": "create_goal" | "delete_goal" | "update_goal" | "none",
                "confidence": 0.0-1.0,
                "goal_data": {...},
                "goal_to_delete": "...",
                "reasoning": "..."
            }
        """
        from backend.services.prompt_builder import prompt_builder
        
        try:
            # Создаём промпт для определения намерения
            prompt = prompt_builder.build_intent_detection_prompt(user_message, user_goals)
            
            # Запрос к LLM
            response = self.simple_query(prompt)
            
            # Извлекаем JSON
            intent_data = self.extract_json_from_response(response)
            
            # Валидация обязательных полей
            if not intent_data.get('intent'):
                intent_data['intent'] = 'none'
            if not intent_data.get('confidence'):
                intent_data['confidence'] = 0.0
            
            # Логирование для отладки
            print(f"[Intent Detection] Intent: {intent_data.get('intent')} "
                  f"(confidence: {intent_data.get('confidence'):.2f}) - "
                  f"{intent_data.get('reasoning', 'No reasoning')}")
            
            return intent_data
            
        except Exception as e:
            print(f"Error in detect_intent: {e}")
            # Возвращаем дефолтное значение при ошибке
            return {
                "intent": "none",
                "confidence": 0.0,
                "goal_data": None,
                "goal_to_delete": None,
                "reasoning": f"Error: {str(e)}"
            }

# Singleton instance
llm_service = LLMService()

