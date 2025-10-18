"""
Модель диалога (истории сообщений)
"""
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.utils.db import Base
from backend.utils.guid import GUID

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' или 'assistant'
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotion_score = Column(Float, nullable=True)  # Уровень стресса 1-10
    emotion_type = Column(String(50), nullable=True)  # тип эмоции
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation {self.role}: {self.message[:50]}...>"

