"""
Сервис для работы с LLM (gpt-4o-mini)
"""
from openai import OpenAI
from backend.config import (
    OPENAI_API_KEY, 
    OPENAI_BASE_URL, 
    GPT_MODEL,
    EMBEDDING_MODEL
)
from typing import List, Dict, Any
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
        max_tokens: int = 1000
    ) -> str:
        """
        Отправка запроса к gpt-4o-mini
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            temperature: Температура генерации
            max_tokens: Максимальное количество токенов
            
        Returns:
            Ответ от модели
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
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
    
    def simple_query(self, prompt: str, system_prompt: str = None) -> str:
        """
        Простой запрос к модели
        
        Args:
            prompt: Пользовательский промпт
            system_prompt: Системный промпт (опционально)
            
        Returns:
            Ответ модели
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(messages)

# Singleton instance
llm_service = LLMService()

