"""
ConversationService: thin domain service for conversation history and mapping.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.services.repositories import (
    users_repo,
    conversations_repo,
)


class ConversationService:
    def get_history(self, db: Session, user_id: str) -> Dict[str, Any]:
        user = users_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("user_not_found")

        conversations = conversations_repo.list_all_asc(db, user.id)
        return {
            "user_id": str(user.id),
            "conversations": [
                {
                    "role": c.role,
                    "message": c.message,
                    "timestamp": c.timestamp.isoformat(),
                    "emotion_type": c.emotion_type,
                    "emotion_score": c.emotion_score,
                }
                for c in conversations
            ],
        }


conversation_service = ConversationService()


