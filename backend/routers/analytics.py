"""
Простые роутеры для финансовой аналитики
Нейронка сама решает что анализировать
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import csv
import io

from backend.utils.db import get_db
from backend.models.transaction import Transaction
from backend.models.user import User
from backend.services.ai_analytics import ai_analytics

router = APIRouter()

class AnalyticsRequest(BaseModel):
    user_id: int
    query: Optional[str] = None
    period_days: int = 30

class AnalyticsResponse(BaseModel):
    analysis: str

@router.post("/analytics/analyze", response_model=AnalyticsResponse)
async def analyze_finances(request: AnalyticsRequest, db: Session = Depends(get_db)):
    """
    Умный AI-анализ финансов
    Нейронка сама решает что важно
    """
    try:
        analysis = ai_analytics.analyze_user_finances(
            user_id=request.user_id,
            db=db,
            user_query=request.query,
            period_days=request.period_days
        )
        
        return AnalyticsResponse(analysis=analysis)
    
    except Exception as e:
        print(f"Error in analyze_finances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/compare", response_model=AnalyticsResponse)
async def compare_with_market(request: AnalyticsRequest, db: Session = Depends(get_db)):
    """
    Сравнительная аналитика с анонимными данными
    Нейронка сама делает выводы
    """
    try:
        insights = ai_analytics.get_comparative_insights(
            user_id=request.user_id,
            db=db,
            period_days=request.period_days
        )
        
        return AnalyticsResponse(analysis=insights)
    
    except Exception as e:
        print(f"Error in compare_with_market: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/upload-statement/{user_id}")
async def upload_bank_statement(
    user_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Загрузка выписки CSV
    Формат: дата, сумма, описание, баланс
    """
    try:
        # Проверка пользователя
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Чтение CSV
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        transactions_added = 0
        
        for row in csv_reader:
            try:
                # Парсинг даты (формат: YYYY-MM-DD или DD.MM.YYYY)
                date_str = row.get('date') or row.get('дата') or row.get('Date')
                if '.' in date_str:
                    date = datetime.strptime(date_str, "%d.%m.%Y")
                else:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Парсинг суммы
                amount_str = row.get('amount') or row.get('сумма') or row.get('Amount')
                amount = float(amount_str.replace(',', '.').replace(' ', ''))
                
                # Описание
                description = (
                    row.get('description') or 
                    row.get('описание') or 
                    row.get('Description') or 
                    'Транзакция'
                )
                
                # Баланс (опционально)
                balance_str = row.get('balance') or row.get('баланс') or row.get('Balance')
                balance = float(balance_str.replace(',', '.').replace(' ', '')) if balance_str else None
                
                # Создание транзакции
                transaction = Transaction(
                    user_id=user.id,
                    date=date,
                    amount=amount,
                    description=description,
                    balance=balance,
                    source="csv"
                )
                
                db.add(transaction)
                transactions_added += 1
                
            except Exception as e:
                print(f"Error parsing row: {row}, error: {e}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Загружено {transactions_added} транзакций",
            "transactions_added": transactions_added
        }
    
    except Exception as e:
        print(f"Error uploading statement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/transactions/{user_id}")
async def get_user_transactions(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Получение транзакций пользователя"""
    try:
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.date.desc()).limit(limit).all()
        
        return {
            "transactions": [
                {
                    "id": t.id,
                    "date": t.date.isoformat(),
                    "amount": t.amount,
                    "description": t.description,
                    "balance": t.balance
                }
                for t in transactions
            ]
        }
    
    except Exception as e:
        print(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/should-offer/{user_id}")
async def should_offer_analytics(user_id: int, db: Session = Depends(get_db)):
    """Проверка - стоит ли предлагать аналитику"""
    try:
        should_offer = ai_analytics.should_offer_analytics(user_id, db)
        
        return {
            "should_offer": should_offer,
            "message": "У клиента есть транзакции - можно предложить аналитику" if should_offer else "Нет данных для аналитики"
        }
    
    except Exception as e:
        print(f"Error in should_offer_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

