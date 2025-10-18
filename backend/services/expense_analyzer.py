"""
Анализатор расходов и доходов для финансовой аналитики
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend.models.transaction import Transaction, TransactionCategory
from backend.services.llm_service import llm_service
import json

class ExpenseAnalyzer:
    """Анализ финансовых транзакций и выписок"""
    
    def __init__(self):
        self.default_categories = {
            # Доходы
            "income": ["зарплата", "премия", "бонус", "доход", "прибыль", "дивиденды"],
            "business": ["бизнес", "продажа", "услуги", "консультация"],
            
            # Расходы
            "food": ["еда", "продукты", "ресторан", "кафе", "магазин", "супермаркет", "пицца", "бургер"],
            "transport": ["транспорт", "такси", "автобус", "метро", "бензин", "парковка", "uber", "яндекс"],
            "shopping": ["покупка", "одежда", "обувь", "магазин", "интернет", "онлайн", "заказ"],
            "entertainment": ["развлечения", "кино", "театр", "игры", "спорт", "фитнес", "клуб"],
            "health": ["здоровье", "врач", "лекарства", "аптека", "больница", "стоматолог"],
            "education": ["образование", "курсы", "университет", "школа", "книги", "обучение"],
            "utilities": ["коммунальные", "электричество", "газ", "вода", "интернет", "телефон"],
            "housing": ["жилье", "аренда", "ипотека", "ремонт", "мебель", "бытовая техника"],
            "savings": ["накопления", "депозит", "инвестиции", "вклад", "сбережения"],
            "other": ["прочее", "перевод", "комиссия", "штраф", "налог"]
        }
    
    def analyze_user_finances(
        self, 
        user_id: str, 
        db: Session, 
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Комплексный анализ финансов пользователя
        
        Args:
            user_id: ID пользователя
            db: Сессия базы данных
            period_days: Период анализа в днях
            
        Returns:
            Словарь с результатами анализа
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Получение транзакций за период
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        if not transactions:
            return self._empty_analysis_result(period_days)
        
        # Анализ доходов и расходов
        income_analysis = self._analyze_income(transactions)
        expense_analysis = self._analyze_expenses(transactions)
        
        # Анализ категорий
        category_analysis = self._analyze_categories(transactions)
        
        # Анализ трендов
        trend_analysis = self._analyze_trends(transactions, period_days)
        
        # Анализ стресс-покупок
        stress_analysis = self._analyze_stress_purchases(transactions)
        
        # Общие метрики
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        net_income = total_income - total_expenses
        
        # Текущий баланс
        latest_transaction = max(transactions, key=lambda t: t.date)
        current_balance = latest_transaction.account_balance or 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": period_days
            },
            "summary": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_income": net_income,
                "current_balance": current_balance,
                "transaction_count": len(transactions)
            },
            "income_analysis": income_analysis,
            "expense_analysis": expense_analysis,
            "category_analysis": category_analysis,
            "trend_analysis": trend_analysis,
            "stress_analysis": stress_analysis,
            "insights": self._generate_insights(
                total_income, total_expenses, net_income, 
                category_analysis, stress_analysis
            )
        }
    
    def _analyze_income(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Анализ доходов"""
        income_transactions = [t for t in transactions if t.amount > 0]
        
        if not income_transactions:
            return {"total": 0, "count": 0, "sources": [], "average": 0}
        
        total_income = sum(t.amount for t in income_transactions)
        sources = {}
        
        for t in income_transactions:
            category = t.category or "неизвестно"
            if category not in sources:
                sources[category] = {"amount": 0, "count": 0}
            sources[category]["amount"] += t.amount
            sources[category]["count"] += 1
        
        return {
            "total": total_income,
            "count": len(income_transactions),
            "sources": sources,
            "average": total_income / len(income_transactions)
        }
    
    def _analyze_expenses(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Анализ расходов"""
        expense_transactions = [t for t in transactions if t.amount < 0]
        
        if not expense_transactions:
            return {"total": 0, "count": 0, "categories": [], "average": 0}
        
        total_expenses = abs(sum(t.amount for t in expense_transactions))
        categories = {}
        
        for t in expense_transactions:
            category = t.category or "прочее"
            if category not in categories:
                categories[category] = {"amount": 0, "count": 0, "transactions": []}
            categories[category]["amount"] += abs(t.amount)
            categories[category]["count"] += 1
            categories[category]["transactions"].append({
                "date": t.date.isoformat(),
                "amount": abs(t.amount),
                "description": t.description,
                "is_stress": t.is_stress_purchase
            })
        
        # Сортировка по сумме
        sorted_categories = sorted(
            categories.items(), 
            key=lambda x: x[1]["amount"], 
            reverse=True
        )
        
        return {
            "total": total_expenses,
            "count": len(expense_transactions),
            "categories": dict(sorted_categories),
            "average": total_expenses / len(expense_transactions)
        }
    
    def _analyze_categories(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Анализ по категориям"""
        category_stats = {}
        
        for t in transactions:
            category = t.category or "неизвестно"
            if category not in category_stats:
                category_stats[category] = {
                    "income": 0,
                    "expenses": 0,
                    "count": 0,
                    "stress_purchases": 0
                }
            
            if t.amount > 0:
                category_stats[category]["income"] += t.amount
            else:
                category_stats[category]["expenses"] += abs(t.amount)
            
            category_stats[category]["count"] += 1
            
            if t.is_stress_purchase:
                category_stats[category]["stress_purchases"] += 1
        
        return category_stats
    
    def _analyze_trends(self, transactions: List[Transaction], period_days: int) -> Dict[str, Any]:
        """Анализ трендов"""
        if len(transactions) < 2:
            return {"trend": "недостаточно данных", "change_percent": 0}
        
        # Группировка по неделям
        weekly_data = {}
        for t in transactions:
            week_start = t.date - timedelta(days=t.date.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {"income": 0, "expenses": 0}
            
            if t.amount > 0:
                weekly_data[week_key]["income"] += t.amount
            else:
                weekly_data[week_key]["expenses"] += abs(t.amount)
        
        # Анализ тренда
        weeks = sorted(weekly_data.keys())
        if len(weeks) >= 2:
            first_week = weekly_data[weeks[0]]
            last_week = weekly_data[weeks[-1]]
            
            first_net = first_week["income"] - first_week["expenses"]
            last_net = last_week["income"] - last_week["expenses"]
            
            if first_net != 0:
                change_percent = ((last_net - first_net) / abs(first_net)) * 100
            else:
                change_percent = 0
            
            if change_percent > 5:
                trend = "положительный"
            elif change_percent < -5:
                trend = "отрицательный"
            else:
                trend = "стабильный"
        else:
            trend = "недостаточно данных"
            change_percent = 0
        
        return {
            "trend": trend,
            "change_percent": change_percent,
            "weekly_data": weekly_data
        }
    
    def _analyze_stress_purchases(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Анализ стресс-покупок"""
        stress_transactions = [t for t in transactions if t.is_stress_purchase]
        
        if not stress_transactions:
            return {
                "count": 0,
                "total_amount": 0,
                "percentage": 0,
                "categories": {}
            }
        
        total_stress_amount = sum(abs(t.amount) for t in stress_transactions)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        
        stress_categories = {}
        for t in stress_transactions:
            category = t.category or "прочее"
            if category not in stress_categories:
                stress_categories[category] = {"count": 0, "amount": 0}
            stress_categories[category]["count"] += 1
            stress_categories[category]["amount"] += abs(t.amount)
        
        return {
            "count": len(stress_transactions),
            "total_amount": total_stress_amount,
            "percentage": (total_stress_amount / total_expenses * 100) if total_expenses > 0 else 0,
            "categories": stress_categories
        }
    
    def _generate_insights(
        self, 
        total_income: float, 
        total_expenses: float, 
        net_income: float,
        category_analysis: Dict,
        stress_analysis: Dict
    ) -> List[str]:
        """Генерация инсайтов на основе анализа"""
        insights = []
        
        # Анализ сбережений
        if net_income > 0:
            savings_rate = (net_income / total_income) * 100 if total_income > 0 else 0
            if savings_rate > 20:
                insights.append(f"Отличная работа! Вы откладываете {savings_rate:.1f}% от дохода.")
            elif savings_rate > 10:
                insights.append(f"Хорошо! Вы откладываете {savings_rate:.1f}% от дохода.")
            else:
                insights.append(f"Рекомендуем увеличить сбережения. Сейчас вы откладываете {savings_rate:.1f}% от дохода.")
        else:
            insights.append("Внимание: расходы превышают доходы. Рекомендуем пересмотреть бюджет.")
        
        # Анализ стресс-покупок
        if stress_analysis["percentage"] > 30:
            insights.append(f"Высокий процент стресс-покупок ({stress_analysis['percentage']:.1f}%). Рекомендуем найти альтернативные способы борьбы со стрессом.")
        elif stress_analysis["percentage"] > 15:
            insights.append(f"Умеренный процент стресс-покупок ({stress_analysis['percentage']:.1f}%). Можно улучшить.")
        
        # Анализ категорий
        if category_analysis:
            top_category = max(category_analysis.items(), key=lambda x: x[1]["expenses"])
            if top_category[1]["expenses"] > total_expenses * 0.4:
                insights.append(f"Основные расходы на '{top_category[0]}' ({top_category[1]['expenses']/total_expenses*100:.1f}%). Возможно, стоит оптимизировать.")
        
        return insights
    
    def _empty_analysis_result(self, period_days: int) -> Dict[str, Any]:
        """Результат анализа при отсутствии транзакций"""
        return {
            "period": {
                "start_date": (datetime.utcnow() - timedelta(days=period_days)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days": period_days
            },
            "summary": {
                "total_income": 0,
                "total_expenses": 0,
                "net_income": 0,
                "current_balance": 0,
                "transaction_count": 0
            },
            "income_analysis": {"total": 0, "count": 0, "sources": [], "average": 0},
            "expense_analysis": {"total": 0, "count": 0, "categories": [], "average": 0},
            "category_analysis": {},
            "trend_analysis": {"trend": "нет данных", "change_percent": 0},
            "stress_analysis": {"count": 0, "total_amount": 0, "percentage": 0, "categories": {}},
            "insights": ["Нет данных о транзакциях за выбранный период."]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Автоматическая категоризация транзакции на основе описания
        
        Args:
            description: Описание транзакции
            amount: Сумма транзакции
            
        Returns:
            Название категории
        """
        description_lower = description.lower()
        
        # Определение типа транзакции
        if amount > 0:
            # Доходы
            for category, keywords in self.default_categories.items():
                if category in ["income", "business"]:
                    if any(keyword in description_lower for keyword in keywords):
                        return category
            return "income"
        else:
            # Расходы
            for category, keywords in self.default_categories.items():
                if category not in ["income", "business"]:
                    if any(keyword in description_lower for keyword in keywords):
                        return category
            return "other"
    
    def detect_stress_purchase(self, description: str, amount: float, time_of_day: str = None) -> bool:
        """
        Определение стресс-покупки на основе описания и контекста
        
        Args:
            description: Описание транзакции
            amount: Сумма транзакции
            time_of_day: Время дня (опционально)
            
        Returns:
            True если это стресс-покупка
        """
        description_lower = description.lower()
        
        # Ключевые слова стресс-покупок
        stress_keywords = [
            "импульсивно", "срочно", "нужно сейчас", "не могу удержаться",
            "шопинг", "покупка для настроения", "розничная терапия"
        ]
        
        # Категории, часто связанные со стрессом
        stress_categories = [
            "еда", "развлечения", "шопинг", "онлайн покупки"
        ]
        
        # Проверка ключевых слов
        if any(keyword in description_lower for keyword in stress_keywords):
            return True
        
        # Проверка категории
        category = self.categorize_transaction(description, amount)
        if category in stress_categories and abs(amount) > 10000:  # Крупные покупки в стресс-категориях
            return True
        
        return False

# Singleton instance
expense_analyzer = ExpenseAnalyzer()
