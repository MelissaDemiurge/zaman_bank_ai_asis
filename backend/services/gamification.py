"""
Сервис геймификации (исламский подход)
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from backend.services.llm_service import llm_service

class GamificationService:
    """Управление челленджами и наградами"""
    
    # Шаблоны челленджей (исламский подход)
    CHALLENGE_TEMPLATES = {
        "no_impulse_30": {
            "title": "30 дней без импульсивных трат",
            "description": "Контролируй эмоции и избегай спонтанных покупок в течение месяца",
            "challenge_type": "no_impulse",
            "target_value": 30,
            "reward_title": "Самоконтроль (Сабр)",
            "advice": "При желании купить что-то спонтанно, подожди 24 часа. Часто желание проходит."
        },
        "save_100k": {
            "title": "Накопить 100,000₸ за 3 месяца",
            "description": "Поставь цель и регулярно откладывай средства",
            "challenge_type": "savings",
            "target_value": 100000,
            "reward_title": "Первый барака́т",
            "advice": "Открой депозит 'Вакала' и переводи туда часть дохода автоматически."
        },
        "deposit_open": {
            "title": "Открыть первый депозит Вакала",
            "description": "Начни путь исламских инвестиций",
            "challenge_type": "deposit",
            "target_value": 1,
            "reward_title": "Партнёр банка",
            "advice": "Депозит Вакала — это не риба, а партнёрство в халяльном бизнесе."
        },
        "reduce_spending": {
            "title": "Сократить траты на 20%",
            "description": "Анализируй расходы и оптимизируй бюджет",
            "challenge_type": "reduce_spending",
            "target_value": 20,
            "reward_title": "Мудрый управляющий",
            "advice": "Веди учёт трат и определи, от чего можно отказаться без потери качества жизни."
        },
        "stress_free_week": {
            "title": "Неделя без стресс-покупок",
            "description": "При стрессе ищи альтернативы тратам: прогулка, спорт, хобби",
            "challenge_type": "stress_management",
            "target_value": 7,
            "reward_title": "Эмоциональная независимость",
            "advice": "Составь список бесплатных активностей, которые приносят радость."
        }
    }
    
    def suggest_challenge(
        self, 
        emotion_data: Optional[Dict] = None,
        user_goals: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Предложение челленджа на основе эмоций и целей
        
        Args:
            emotion_data: Данные о эмоциях пользователя
            user_goals: Цели пользователя
            
        Returns:
            Словарь с данными челленджа
        """
        # Логика выбора челленджа
        if emotion_data:
            stress_score = emotion_data.get("stress_score", 3)
            vulnerability = emotion_data.get("financial_vulnerability", "низкая")
            
            # Высокий стресс и уязвимость - челленджи по контролю трат
            if stress_score >= 7 or vulnerability == "высокая":
                return self.CHALLENGE_TEMPLATES["stress_free_week"]
            elif stress_score >= 5:
                return self.CHALLENGE_TEMPLATES["no_impulse_30"]
        
        # Если есть цели на накопление - челлендж по сбережениям
        if user_goals:
            return self.CHALLENGE_TEMPLATES["save_100k"]
        
        # По умолчанию - открытие депозита
        return self.CHALLENGE_TEMPLATES["deposit_open"]
    
    def generate_completion_message(self, challenge: Dict) -> str:
        """
        Генерация персонального поздравления при выполнении челленджа
        
        Args:
            challenge: Данные челленджа
            
        Returns:
            Поздравительное сообщение
        """
        reward_title = challenge.get("reward_title", "Награда")
        challenge_title = challenge.get("title", "Челлендж")
        
        prompt = f"""Создай короткое вдохновляющее поздравление клиенту Zaman Bank, который выполнил челлендж:

Челлендж: {challenge_title}
Награда: {reward_title}

Требования:
- 2-3 предложения
- Тон: тёплый, поддерживающий
- Упомяни духовный рост и финансовую мудрость (без религиозной проповеди)
- На русском языке

Поздравление:"""
        
        try:
            message = llm_service.simple_query(prompt)
            return message
        except:
            return f"🎉 Поздравляем! Вы выполнили челлендж '{challenge_title}' и получили награду '{reward_title}'!"
    
    def calculate_progress(self, challenge: Dict) -> float:
        """
        Расчёт прогресса челленджа
        
        Args:
            challenge: Данные челленджа из БД
            
        Returns:
            Процент выполнения
        """
        current = challenge.get("current_value", 0)
        target = challenge.get("target_value", 1)
        
        if target == 0:
            return 0.0
        
        return min((current / target) * 100, 100.0)
    
    def get_challenge_advice(self, challenge_type: str) -> str:
        """
        Получение совета по челленджу
        
        Args:
            challenge_type: Тип челленджа
            
        Returns:
            Совет
        """
        for template in self.CHALLENGE_TEMPLATES.values():
            if template["challenge_type"] == challenge_type:
                return template["advice"]
        
        return "Следуйте плану и отслеживайте прогресс!"
    
    def format_challenges_summary(self, challenges: List[Dict]) -> str:
        """
        Форматирование списка челленджей для отображения
        
        Args:
            challenges: Список челленджей
            
        Returns:
            Отформатированная строка
        """
        if not challenges:
            return "У вас пока нет активных челленджей."
        
        summary = "🎯 Ваши активные челленджи:\n\n"
        for challenge in challenges:
            progress = self.calculate_progress(challenge)
            title = challenge.get("title", "Челлендж")
            summary += f"• {title}: {progress:.1f}% выполнено\n"
        
        return summary

# Singleton instance
gamification_service = GamificationService()

