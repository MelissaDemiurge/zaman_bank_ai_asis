"""
AI-сервис для финансовой аналитики
Нейронка получает данные и сама рассуждает - минимум условий, максимум свободы
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models.transaction import Transaction
from backend.models.goal import Goal
from backend.models.emotion_log import EmotionLog
from backend.services.llm_service import llm_service
from backend.config import MAX_TOKENS_ANALYTICS
import json
import uuid

class AIAnalytics:
    """Умный AI-аналитик финансов"""
    
    def analyze_user_finances(
        self, 
        user_id: str, 
        db: Session,
        user_query: Optional[str] = None,
        period_days: int = 30
    ) -> str:
        """
        Нейронка получает данные и сама решает что анализировать
        
        Args:
            user_id: ID пользователя
            db: Сессия БД
            user_query: Вопрос пользователя (опционально)
            period_days: Период анализа
            
        Returns:
            Анализ от нейронки
        """
        # Собираем сырые данные
        financial_data = self._get_raw_financial_data(user_id, db, period_days)
        
        # Даем нейронке свободу рассуждать
        prompt = self._build_analytics_prompt(financial_data, user_query)
        
        # Используем больше токенов для детальной аналитики
        analysis = llm_service.simple_query(prompt, max_tokens=MAX_TOKENS_ANALYTICS)
        
        return analysis
    
    def get_comparative_insights(
        self, 
        user_id: str, 
        db: Session,
        period_days: int = 30
    ) -> str:
        """
        Сравнительная аналитика - нейронка сама решает что важно
        
        Args:
            user_id: ID пользователя
            db: Сессия БД
            period_days: Период анализа
            
        Returns:
            Сравнительные инсайты
        """
        # Данные пользователя
        user_data = self._get_raw_financial_data(user_id, db, period_days)
        
        # Анонимные данные других пользователей
        market_data = self._get_market_data(db, period_days)
        
        # Нейронка сама делает выводы
        prompt = self._build_comparative_prompt(user_data, market_data)
        
        # Используем больше токенов для сравнительной аналитики
        insights = llm_service.simple_query(prompt, max_tokens=MAX_TOKENS_ANALYTICS)
        
        return insights
    
    def _get_raw_financial_data(
        self, 
        user_id: str, 
        db: Session, 
        period_days: int
    ) -> Dict[str, Any]:
        """Просто собираем данные - без анализа"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Конвертируем user_id в UUID если это строка
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                pass  # Если не UUID, оставляем как есть
        
        # Транзакции
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date
            )
        ).order_by(Transaction.date.desc()).all()
        
        # Цели
        goals = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all()
        
        # Эмоции за последние 7 дней
        emotions = db.query(EmotionLog).filter(
            and_(
                EmotionLog.user_id == user_id,
                EmotionLog.timestamp >= datetime.utcnow() - timedelta(days=7)
            )
        ).order_by(EmotionLog.timestamp.desc()).all()
        
        # Форматируем данные просто и понятно
        return {
            "period": f"{period_days} дней",
            "transactions": [
                {
                    "date": t.date.strftime("%Y-%m-%d"),
                    "amount": t.amount,
                    "description": t.description,
                    "balance": t.balance
                } 
                for t in transactions[:50]  # Последние 50 транзакций
            ],
            "current_balance": transactions[0].balance if transactions else 0,
            "goals": [
                {
                    "title": g.title,
                    "target": g.target_amount,
                    "current": g.current_amount,
                    "progress": g.progress_percentage
                }
                for g in goals
            ],
            "recent_emotions": [
                {
                    "date": e.timestamp.strftime("%Y-%m-%d"),
                    "type": e.emotion_type,
                    "stress": e.stress_score
                }
                for e in emotions[:7]
            ]
        }
    
    def _get_market_data(self, db: Session, period_days: int) -> Dict[str, Any]:
        """Агрегированные данные всех пользователей (анонимно)"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Все транзакции (анонимно)
        all_transactions = db.query(Transaction).filter(
            Transaction.date >= start_date
        ).all()
        
        if not all_transactions:
            return {"message": "Недостаточно данных для сравнения"}
        
        # Группируем по пользователям
        users_data = {}
        for t in all_transactions:
            if str(t.user_id) not in users_data:
                users_data[str(t.user_id)] = []
            users_data[str(t.user_id)].append(t)
        
        # Простая агрегация
        user_summaries = []
        for user_transactions in users_data.values():
            income = sum(t.amount for t in user_transactions if t.amount > 0)
            expenses = abs(sum(t.amount for t in user_transactions if t.amount < 0))
            
            if income > 0:
                user_summaries.append({
                    "income": income,
                    "expenses": expenses,
                    "savings_rate": (income - expenses) / income * 100 if income > 0 else 0
                })
        
        return {
            "users_count": len(user_summaries),
            "summaries": user_summaries[:20]  # Первые 20 для примера
        }
    
    def _build_analytics_prompt(
        self, 
        financial_data: Dict[str, Any], 
        user_query: Optional[str]
    ) -> str:
        """Промпт для анализа - даем нейронке свободу"""
        
        prompt = f"""Ты — финансовый аналитик Zaman Bank с глубоким пониманием исламских финансов.

ДАННЫЕ КЛИЕНТА:
{json.dumps(financial_data, ensure_ascii=False, indent=2)}

ТВОЯ ЗАДАЧА:
Проанализируй финансовую ситуацию клиента и дай практические рекомендации.

СВОБОДНО РАССУЖДАЙ О:
- Структуре доходов и расходов
- Трендах и паттернах
- Возможных проблемах (стресс-траты, импульсивные покупки)
- Прогрессе к целям
- Эмоциональном состоянии и его влиянии на финансы

РЕКОМЕНДАЦИИ:
- Предложи конкретные шаги для улучшения
- Можешь упомянуть продукты Zaman Bank если уместно
- Будь эмпатичным если видишь финансовые трудности

{"ВОПРОС КЛИЕНТА: " + user_query if user_query else ""}

Дай развернутый и содержательный анализ (5-7 абзацев). 
Не спеши - распиши детально свои наблюдения, выводы и рекомендации.
Говори по-человечески, с примерами и конкретикой."""
        
        return prompt
    
    def _build_comparative_prompt(
        self, 
        user_data: Dict[str, Any], 
        market_data: Dict[str, Any]
    ) -> str:
        """Промпт для сравнительной аналитики"""
        
        prompt = f"""Ты — финансовый аналитик Zaman Bank. Проведи сравнительный анализ.

ДАННЫЕ КЛИЕНТА:
{json.dumps(user_data, ensure_ascii=False, indent=2)}

АНОНИМНЫЕ ДАННЫЕ ДРУГИХ ПОЛЬЗОВАТЕЛЕЙ:
{json.dumps(market_data, ensure_ascii=False, indent=2)}

ТВОЯ ЗАДАЧА:
Сравни клиента с другими пользователями и дай мотивирующие инсайты.

СВОБОДНО АНАЛИЗИРУЙ:
- Как клиент выглядит на фоне других?
- В чем он успешен? Что можно улучшить?
- Какие паттерны видны у успешных пользователей?
- Реалистичные мечты и цели других

ВАЖНО:
- Будь мотивирующим, но честным
- Не сравнивай напрямую цифры - говори о тенденциях
- Покажи что клиент не один в своих проблемах
- Дай надежду и конкретные шаги

Формат: развернутый анализ (4-6 абзацев) с конкретными инсайтами и примерами.
Не торопись - дай подробные рекомендации."""
        
        return prompt
    
    def should_offer_analytics(
        self, 
        user_id: str, 
        db: Session
    ) -> bool:
        """
        Проверка - стоит ли предлагать аналитику
        Простая логика: есть транзакции = можно анализировать
        """
        # Конвертируем user_id в UUID если это строка
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                pass
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).limit(1).all()
        
        return len(transactions) > 0
    
    def get_financial_context_for_chat(
        self, 
        user_id: str, 
        db: Session
    ) -> str:
        """
        Финансовый контекст для обычного чата
        Нейронка учитывает это при ответах
        """
        # Конвертируем user_id в UUID если это строка
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                pass
        
        # Последние 10 транзакций
        recent_transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.date.desc()).limit(10).all()
        
        if not recent_transactions:
            return ""
        
        # Текущий баланс
        current_balance = recent_transactions[0].balance or 0
        
        # Быстрая сводка
        income_last_week = sum(
            t.amount for t in recent_transactions 
            if t.amount > 0 and t.date >= datetime.utcnow() - timedelta(days=7)
        )
        expenses_last_week = abs(sum(
            t.amount for t in recent_transactions 
            if t.amount < 0 and t.date >= datetime.utcnow() - timedelta(days=7)
        ))
        
        context = f"""
=== ФИНАНСОВЫЙ КОНТЕКСТ КЛИЕНТА ===

Текущий баланс: {current_balance:,.0f} ₸

За последнюю неделю:
- Доходы: {income_last_week:,.0f} ₸
- Расходы: {expenses_last_week:,.0f} ₸

Последние транзакции:
"""
        for t in recent_transactions[:5]:
            context += f"- {t.date.strftime('%d.%m')}: {t.amount:,.0f} ₸ ({t.description})\n"
        
        context += """
💡 УЧИТЫВАЙ ЭТО при ответах:
- Если клиент спрашивает о продуктах - предлагай с учетом баланса
- Если видишь много трат - можешь мягко предложить оптимизацию
- Если баланс низкий - будь осторожен с предложениями
"""
        
        return context

# Singleton instance
ai_analytics = AIAnalytics()

