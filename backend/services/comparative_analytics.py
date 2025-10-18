"""
Сравнительная аналитика для анонимного сравнения с похожими пользователями
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend.models.transaction import Transaction
from backend.models.goal import Goal
from backend.models.emotion_log import EmotionLog
from backend.services.llm_service import llm_service
import json

class ComparativeAnalytics:
    """Анонимная сравнительная аналитика пользователей"""
    
    def __init__(self):
        # Профили пользователей для сравнения
        self.user_profiles = {
            "young_professional": {
                "age_range": "25-35",
                "income_range": (200000, 500000),
                "description": "молодые профессионалы"
            },
            "family": {
                "age_range": "30-45", 
                "income_range": (300000, 800000),
                "description": "семьи с детьми"
            },
            "senior": {
                "age_range": "45-60",
                "income_range": (400000, 1000000),
                "description": "зрелые специалисты"
            },
            "student": {
                "age_range": "18-25",
                "income_range": (50000, 200000),
                "description": "студенты и молодые специалисты"
            }
        }
    
    def get_comparative_analysis(
        self, 
        user_id: str, 
        db: Session, 
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Получение сравнительной аналитики для пользователя
        
        Args:
            user_id: ID пользователя
            db: Сессия базы данных
            period_days: Период анализа
            
        Returns:
            Словарь с сравнительной аналитикой
        """
        # Определение профиля пользователя
        user_profile = self._determine_user_profile(user_id, db)
        
        # Получение данных пользователя
        user_data = self._get_user_financial_data(user_id, db, period_days)
        
        # Получение анонимных данных похожих пользователей
        similar_users_data = self._get_similar_users_data(user_profile, db, period_days)
        
        # Сравнительный анализ
        comparison = self._compare_with_similar_users(user_data, similar_users_data)
        
        # Генерация мотивирующих инсайтов
        insights = self._generate_motivational_insights(user_data, similar_users_data, user_profile)
        
        return {
            "user_profile": user_profile,
            "user_data": user_data,
            "similar_users_data": similar_users_data,
            "comparison": comparison,
            "insights": insights,
            "period_days": period_days
        }
    
    def _determine_user_profile(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Определение профиля пользователя на основе его данных
        
        Args:
            user_id: ID пользователя
            db: Сессия базы данных
            
        Returns:
            Профиль пользователя
        """
        # Получение среднего дохода за последние 3 месяца
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        income_transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.amount > 0,
                Transaction.date >= three_months_ago
            )
        ).all()
        
        if not income_transactions:
            # Если нет данных о доходах, используем дефолтный профиль
            return self.user_profiles["young_professional"]
        
        avg_monthly_income = sum(t.amount for t in income_transactions) / 3
        
        # Определение профиля на основе дохода
        if avg_monthly_income < 150000:
            return self.user_profiles["student"]
        elif avg_monthly_income < 350000:
            return self.user_profiles["young_professional"]
        elif avg_monthly_income < 600000:
            return self.user_profiles["family"]
        else:
            return self.user_profiles["senior"]
    
    def _get_user_financial_data(self, user_id: str, db: Session, period_days: int) -> Dict[str, Any]:
        """Получение финансовых данных пользователя"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Транзакции
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        # Цели
        goals = db.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.status == "active"
            )
        ).all()
        
        # Эмоции
        emotions = db.query(EmotionLog).filter(
            and_(
                EmotionLog.user_id == user_id,
                EmotionLog.timestamp >= start_date
            )
        ).all()
        
        # Расчет метрик
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        net_income = total_income - total_expenses
        
        # Анализ категорий расходов
        expense_categories = {}
        for t in transactions:
            if t.amount < 0:
                category = t.category or "прочее"
                if category not in expense_categories:
                    expense_categories[category] = 0
                expense_categories[category] += abs(t.amount)
        
        # Стресс-покупки
        stress_purchases = [t for t in transactions if t.is_stress_purchase]
        stress_amount = sum(abs(t.amount) for t in stress_purchases)
        
        # Средний стресс
        avg_stress = sum(e.stress_score for e in emotions) / len(emotions) if emotions else 3.0
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_income": net_income,
            "savings_rate": (net_income / total_income * 100) if total_income > 0 else 0,
            "expense_categories": expense_categories,
            "stress_purchases_count": len(stress_purchases),
            "stress_purchases_amount": stress_amount,
            "stress_purchases_percentage": (stress_amount / total_expenses * 100) if total_expenses > 0 else 0,
            "average_stress": avg_stress,
            "goals_count": len(goals),
            "goals_progress": sum(g.progress_percentage for g in goals) / len(goals) if goals else 0,
            "transaction_count": len(transactions)
        }
    
    def _get_similar_users_data(self, user_profile: Dict, db: Session, period_days: int) -> Dict[str, Any]:
        """
        Получение анонимных данных похожих пользователей
        
        Args:
            user_profile: Профиль пользователя
            db: Сессия базы данных
            period_days: Период анализа
            
        Returns:
            Агрегированные данные похожих пользователей
        """
        # В реальном приложении здесь был бы запрос к базе данных
        # Для демонстрации используем симулированные данные
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Получение всех транзакций за период (анонимно)
        all_transactions = db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        if not all_transactions:
            return self._get_default_similar_data()
        
        # Группировка по пользователям
        user_transactions = {}
        for t in all_transactions:
            if t.user_id not in user_transactions:
                user_transactions[t.user_id] = []
            user_transactions[t.user_id].append(t)
        
        # Фильтрация похожих пользователей (по доходу)
        income_range = user_profile["income_range"]
        similar_users = []
        
        for user_id, transactions in user_transactions.items():
            user_income = sum(t.amount for t in transactions if t.amount > 0)
            avg_monthly_income = user_income / (period_days / 30)
            
            if income_range[0] <= avg_monthly_income <= income_range[1]:
                similar_users.append(transactions)
        
        if not similar_users:
            return self._get_default_similar_data()
        
        # Агрегация данных
        return self._aggregate_similar_users_data(similar_users)
    
    def _aggregate_similar_users_data(self, similar_users_transactions: List[List[Transaction]]) -> Dict[str, Any]:
        """Агрегация данных похожих пользователей"""
        all_transactions = []
        for user_transactions in similar_users_transactions:
            all_transactions.extend(user_transactions)
        
        if not all_transactions:
            return self._get_default_similar_data()
        
        # Расчет метрик
        total_income = sum(t.amount for t in all_transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in all_transactions if t.amount < 0))
        net_income = total_income - total_expenses
        
        # Анализ категорий
        expense_categories = {}
        for t in all_transactions:
            if t.amount < 0:
                category = t.category or "прочее"
                if category not in expense_categories:
                    expense_categories[category] = 0
                expense_categories[category] += abs(t.amount)
        
        # Стресс-покупки
        stress_purchases = [t for t in all_transactions if t.is_stress_purchase]
        stress_amount = sum(abs(t.amount) for t in stress_purchases)
        
        # Нормализация на количество пользователей
        user_count = len(similar_users_transactions)
        
        return {
            "user_count": user_count,
            "avg_income": total_income / user_count,
            "avg_expenses": total_expenses / user_count,
            "avg_net_income": net_income / user_count,
            "avg_savings_rate": (net_income / total_income * 100) if total_income > 0 else 0,
            "avg_expense_categories": {k: v / user_count for k, v in expense_categories.items()},
            "avg_stress_purchases_count": len(stress_purchases) / user_count,
            "avg_stress_purchases_amount": stress_amount / user_count,
            "avg_stress_purchases_percentage": (stress_amount / total_expenses * 100) if total_expenses > 0 else 0,
            "avg_transaction_count": len(all_transactions) / user_count
        }
    
    def _compare_with_similar_users(self, user_data: Dict, similar_data: Dict) -> Dict[str, Any]:
        """Сравнение пользователя с похожими пользователями"""
        comparison = {}
        
        # Сравнение доходов
        if similar_data["avg_income"] > 0:
            income_ratio = user_data["total_income"] / similar_data["avg_income"]
            comparison["income"] = {
                "user": user_data["total_income"],
                "average": similar_data["avg_income"],
                "ratio": income_ratio,
                "status": "выше среднего" if income_ratio > 1.1 else "ниже среднего" if income_ratio < 0.9 else "на уровне"
            }
        
        # Сравнение расходов
        if similar_data["avg_expenses"] > 0:
            expense_ratio = user_data["total_expenses"] / similar_data["avg_expenses"]
            comparison["expenses"] = {
                "user": user_data["total_expenses"],
                "average": similar_data["avg_expenses"],
                "ratio": expense_ratio,
                "status": "выше среднего" if expense_ratio > 1.1 else "ниже среднего" if expense_ratio < 0.9 else "на уровне"
            }
        
        # Сравнение сбережений
        if similar_data["avg_savings_rate"] > 0:
            savings_ratio = user_data["savings_rate"] / similar_data["avg_savings_rate"]
            comparison["savings"] = {
                "user": user_data["savings_rate"],
                "average": similar_data["avg_savings_rate"],
                "ratio": savings_ratio,
                "status": "выше среднего" if savings_ratio > 1.1 else "ниже среднего" if savings_ratio < 0.9 else "на уровне"
            }
        
        # Сравнение стресс-покупок
        if similar_data["avg_stress_purchases_percentage"] > 0:
            stress_ratio = user_data["stress_purchases_percentage"] / similar_data["avg_stress_purchases_percentage"]
            comparison["stress_purchases"] = {
                "user": user_data["stress_purchases_percentage"],
                "average": similar_data["avg_stress_purchases_percentage"],
                "ratio": stress_ratio,
                "status": "выше среднего" if stress_ratio > 1.1 else "ниже среднего" if stress_ratio < 0.9 else "на уровне"
            }
        
        return comparison
    
    def _generate_motivational_insights(
        self, 
        user_data: Dict, 
        similar_data: Dict, 
        user_profile: Dict
    ) -> List[str]:
        """Генерация мотивирующих инсайтов"""
        insights = []
        
        # Анализ сбережений
        if user_data["savings_rate"] > similar_data["avg_savings_rate"]:
            insights.append(f"Отлично! Вы откладываете {user_data['savings_rate']:.1f}% от дохода, что выше среднего для {user_profile['description']} ({similar_data['avg_savings_rate']:.1f}%).")
        elif user_data["savings_rate"] < similar_data["avg_savings_rate"] * 0.8:
            insights.append(f"У вас есть потенциал для роста! Средний уровень сбережений среди {user_profile['description']} составляет {similar_data['avg_savings_rate']:.1f}%, а у вас {user_data['savings_rate']:.1f}%.")
        
        # Анализ стресс-покупок
        if user_data["stress_purchases_percentage"] < similar_data["avg_stress_purchases_percentage"]:
            insights.append(f"Превосходно! У вас меньше стресс-покупок ({user_data['stress_purchases_percentage']:.1f}%) по сравнению со средним показателем {user_profile['description']} ({similar_data['avg_stress_purchases_percentage']:.1f}%).")
        elif user_data["stress_purchases_percentage"] > similar_data["avg_stress_purchases_percentage"] * 1.2:
            insights.append(f"Обратите внимание на стресс-покупки. У вас {user_data['stress_purchases_percentage']:.1f}%, что выше среднего для {user_profile['description']} ({similar_data['avg_stress_purchases_percentage']:.1f}%).")
        
        # Анализ расходов
        if user_data["total_expenses"] < similar_data["avg_expenses"]:
            insights.append(f"Вы тратите меньше среднего! Ваши расходы {user_data['total_expenses']:,.0f} ₸ против средних {similar_data['avg_expenses']:,.0f} ₸ среди {user_profile['description']}.")
        
        # Общие мотивирующие сообщения
        if user_data["goals_count"] > 0:
            insights.append(f"У вас {user_data['goals_count']} активных финансовых целей. Среди {user_profile['description']} в среднем достигают 70% своих целей в течение года.")
        
        return insights
    
    def _get_default_similar_data(self) -> Dict[str, Any]:
        """Дефолтные данные для похожих пользователей"""
        return {
            "user_count": 100,
            "avg_income": 300000,
            "avg_expenses": 250000,
            "avg_net_income": 50000,
            "avg_savings_rate": 16.7,
            "avg_expense_categories": {
                "еда": 80000,
                "транспорт": 40000,
                "развлечения": 30000,
                "шопинг": 50000,
                "прочее": 50000
            },
            "avg_stress_purchases_count": 3,
            "avg_stress_purchases_amount": 15000,
            "avg_stress_purchases_percentage": 6.0,
            "avg_transaction_count": 45
        }
    
    def get_anonymous_insights(self, user_id: str, db: Session) -> str:
        """
        Получение анонимных инсайтов для предложения пользователю
        
        Args:
            user_id: ID пользователя
            db: Сессия базы данных
            
        Returns:
            Текст с анонимными инсайтами
        """
        analysis = self.get_comparative_analysis(user_id, db)
        
        # Формирование сообщения
        message = f"""📊 Анонимная сравнительная аналитика

Ваш профиль: {analysis['user_profile']['description']} (возраст {analysis['user_profile']['age_range']})

💡 Инсайты на основе данных {analysis['similar_users_data']['user_count']} похожих пользователей:

"""
        
        for insight in analysis['insights']:
            message += f"• {insight}\n"
        
        message += f"""
🎯 Мотивация: Среди {analysis['user_profile']['description']} в среднем достигают своих финансовых целей на 70% в течение года. Продолжайте в том же духе!

💭 Хотите узнать больше о своих финансовых привычках? Я могу предложить персональные рекомендации на основе вашего профиля."""
        
        return message

# Singleton instance
comparative_analytics = ComparativeAnalytics()
