"""
Модель логов эмоций (Emotional DNA)
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.utils.db import Base
from backend.utils.guid import GUID

class EmotionLog(Base):
    __tablename__ = "emotion_logs"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    emotion_type = Column(String(50), nullable=False)  # стресс, тревога, спокойствие, радость
    stress_score = Column(Float, nullable=False)  # 1-10
    financial_vulnerability = Column(String(20), nullable=True)  # низкая, средняя, высокая
    notes = Column(Text, nullable=True)  # Заметки от AI
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emotion_logs")
    
    def __repr__(self):
        return f"<EmotionLog {self.emotion_type} ({self.stress_score}/10)>"

