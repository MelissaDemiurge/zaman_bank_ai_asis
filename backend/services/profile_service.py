"""
ProfileService: domain logic for user creation and emotional profile retrieval.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.services.repositories import users_repo, emotion_logs_repo


class ProfileService:
    def create_user(self, db: Session, *, name: str, phone: Optional[str]) -> Dict[str, Any]:
        if phone:
            existing = users_repo.get_by_phone(db, phone)
            if existing:
                return {
                    "message": "Пользователь уже существует",
                    "user": {
                        "id": str(existing.id),
                        "name": existing.name,
                        "phone": existing.phone,
                        "created_at": existing.created_at.isoformat(),
                    },
                }
        user = users_repo.create(db, name=name, phone=phone)
        return {
            "message": "Пользователь успешно создан",
            "user": {
                "id": str(user.id),
                "name": user.name,
                "phone": user.phone,
                "created_at": user.created_at.isoformat(),
            },
        }

    def get_emotional_profile(self, db: Session, *, user_id: str) -> Dict[str, Any]:
        user = users_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("user_not_found")

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        emotions = emotion_logs_repo.list_since(db, str(user.id), thirty_days_ago)
        if not emotions:
            return {
                "user_id": str(user.id),
                "average_stress_score": 3.0,
                "dominant_emotion": "спокойствие",
                "financial_vulnerability_trend": "низкая",
                "recent_emotions": [],
            }

        avg_stress = sum(e.stress_score for e in emotions) / len(emotions)

        counts: Dict[str, int] = {}
        for e in emotions:
            counts[e.emotion_type] = counts.get(e.emotion_type, 0) + 1
        dominant_emotion = max(counts.items(), key=lambda x: x[1])[0]

        vulnerability_map = {"низкая": 1, "средняя": 2, "высокая": 3}
        last_ten = [
            vulnerability_map.get(e.financial_vulnerability, 1)
            for e in emotions[-10:]
            if e.financial_vulnerability
        ]
        avg_v = sum(last_ten) / len(last_ten) if last_ten else 1
        trend = "низкая"
        if avg_v >= 2.5:
            trend = "высокая"
        elif avg_v >= 1.5:
            trend = "средняя"

        recent = [
            {
                "emotion_type": e.emotion_type,
                "stress_score": e.stress_score,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in emotions[-10:]
        ]

        return {
            "user_id": str(user.id),
            "average_stress_score": round(avg_stress, 1),
            "dominant_emotion": dominant_emotion,
            "financial_vulnerability_trend": trend,
            "recent_emotions": recent,
        }


profile_service = ProfileService()


