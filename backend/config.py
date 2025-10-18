"""
Конфигурация для Zaman AI Assistant
"""
import os
from typing import Optional

# Импорт промптов из отдельного файла
from backend.prompts import (
    SYSTEM_PROMPT,
    EMOTION_ANALYSIS_PROMPT
)

# API конфигурация для OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Модели
GPT_MODEL = "gpt-5-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
WHISPER_MODEL = "whisper-1"

# База данных
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./zaman.db"
)

# ChromaDB
CHROMA_PERSIST_DIR = "./chroma_db"
CHROMA_COLLECTION_NAME = "zaman_knowledge"

# RAG параметры
TOP_K_RESULTS = 3  # Количество релевантных чанков для контекста
CHUNK_SIZE = 500  # Размер чанков при векторизации

# LLM Token limits (увеличены для более развернутых ответов)
MAX_TOKENS_CHAT = 4000  # Для обычного чата - увеличен для развернутых ответов
MAX_TOKENS_ANALYTICS = 4500  # Для аналитики и детальных отчетов
MAX_TOKENS_SHORT = 500  # Для коротких ответов (эмоции, интенты)

# Emotion analysis
EMOTION_STRESS_THRESHOLD = 7  # Порог стресса для триггера проактивных советов

# Proactive triggers
PROACTIVE_INACTIVITY_DAYS = 5  # Дней неактивности для триггера
PROACTIVE_GOAL_DEADLINE_DAYS = 60  # Дней до дедлайна цели для уведомления


