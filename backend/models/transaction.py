"""
Простая модель транзакций - только самое необходимое
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.utils.db import Base
from backend.utils.guid import GUID

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    
    # Только основные поля
    date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)  # Положительное = доход, отрицательное = расход
    description = Column(Text, nullable=False)
    balance = Column(Float, nullable=True)  # Баланс после транзакции
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50), default="manual")  # manual, csv, api
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.date.strftime('%Y-%m-%d')}: {self.amount:,.0f} ₸ - {self.description[:30]}...>"
