"""
Модель челленджей (геймификация)
"""
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.utils.db import Base
from backend.utils.guid import GUID

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)  # Название челленджа
    challenge_type = Column(String(50), nullable=False)  # savings, no_impulse, deposit
    target_value = Column(Float, nullable=True)  # Целевое значение (сумма, дни)
    current_value = Column(Float, default=0.0)  # Текущий прогресс
    status = Column(String(20), default="active")  # active, completed, failed
    reward_title = Column(String(200), nullable=True)  # Название награды (ачивка)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="challenges")
    
    @property
    def progress_percentage(self) -> float:
        """Прогресс в процентах"""
        if not self.target_value or self.target_value == 0:
            return 0.0
        return min((self.current_value / self.target_value) * 100, 100.0)
    
    def __repr__(self):
        return f"<Challenge {self.title}: {self.progress_percentage:.1f}%>"

