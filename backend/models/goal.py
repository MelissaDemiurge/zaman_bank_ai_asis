"""
Модель финансовых целей
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.utils.db import Base

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)  # "Квартира", "Обучение"
    target_amount = Column(Float, nullable=False)  # Целевая сумма
    current_amount = Column(Float, default=0.0)  # Текущий прогресс
    deadline_months = Column(Integer, nullable=True)  # Срок в месяцах
    status = Column(String(20), default="active")  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    
    @property
    def progress_percentage(self) -> float:
        """Прогресс в процентах"""
        if self.target_amount == 0:
            return 0.0
        return min((self.current_amount / self.target_amount) * 100, 100.0)
    
    def __repr__(self):
        return f"<Goal {self.title}: {self.progress_percentage:.1f}%>"

