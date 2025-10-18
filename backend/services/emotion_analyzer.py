"""
Анализатор эмоций для определения финансового стресса
"""
from backend.services.llm_service import llm_service
from backend.config import EMOTION_ANALYSIS_PROMPT
from typing import Dict, Any
import json

class EmotionAnalyzer:
    """Анализ эмоционального состояния клиента"""
    
    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Анализ эмоций в сообщении
        
        Args:
            message: Сообщение пользователя
            
        Returns:
            Словарь с результатами анализа:
            {
                "emotion_type": str,
                "stress_score": float,
                "financial_vulnerability": str,
                "notes": str
            }
        """
        prompt = EMOTION_ANALYSIS_PROMPT + f"\n{message}"
        
        try:
            response = llm_service.simple_query(prompt, system_prompt=None)
            
            # Извлечение JSON из ответа
            result = llm_service.extract_json_from_response(response)
            
            # Валидация и значения по умолчанию
            if not result:
                return self._default_emotion()
            
            return {
                "emotion_type": result.get("emotion_type", "спокойствие"),
                "stress_score": float(result.get("stress_score", 3)),
                "financial_vulnerability": result.get("financial_vulnerability", "низкая"),
                "notes": result.get("notes", "")
            }
        except Exception as e:
            print(f"Error in emotion analysis: {e}")
            return self._default_emotion()
    
    def _default_emotion(self) -> Dict[str, Any]:
        """Эмоции по умолчанию при ошибке"""
        return {
            "emotion_type": "спокойствие",
            "stress_score": 3.0,
            "financial_vulnerability": "низкая",
            "notes": ""
        }
    
    def get_emotional_context(self, emotion_data: Dict[str, Any]) -> str:
        """
        Получение текстового описания эмоционального состояния для промпта
        
        Args:
            emotion_data: Данные анализа эмоций
            
        Returns:
            Текстовое описание для контекста
        """
        emotion_type = emotion_data.get("emotion_type", "спокойствие")
        stress_score = emotion_data.get("stress_score", 3)
        vulnerability = emotion_data.get("financial_vulnerability", "низкая")
        
        context = f"=== ЭМОЦИОНАЛЬНОЕ СОСТОЯНИЕ КЛИЕНТА ===\n"
        context += f"Эмоция: {emotion_type}\n"
        context += f"Уровень стресса: {stress_score}/10\n"
        context += f"Финансовая уязвимость: {vulnerability}\n"
        
        # Рекомендации по тону ответа
        if stress_score >= 7:
            context += "\n⚠️ ВАЖНО: Клиент в стрессе! Начни с эмоциональной поддержки, затем дай совет.\n"
        elif stress_score >= 5:
            context += "\n📌 Клиент немного обеспокоен. Будь особенно эмпатичным.\n"
        
        if vulnerability in ["высокая", "средняя"]:
            context += "⚠️ Высокая склонность к импульсивным тратам. Предложи альтернативы стресс-покупкам.\n"
        
        return context

# Singleton instance
emotion_analyzer = EmotionAnalyzer()

