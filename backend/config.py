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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

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

# Emotion analysis
EMOTION_STRESS_THRESHOLD = 7  # Порог стресса для триггера проактивных советов

# Proactive triggers
PROACTIVE_INACTIVITY_DAYS = 5  # Дней неактивности для триггера
PROACTIVE_GOAL_DEADLINE_DAYS = 60  # Дней до дедлайна цели для уведомления


