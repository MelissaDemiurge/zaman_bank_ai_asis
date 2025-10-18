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

# API конфигурация для OpenAI Hub
OPENAI_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
OPENAI_BASE_URL = "https://openai-hub.neuraldeep.tech"

# Модели
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
WHISPER_MODEL = "whisper-1"

# База данных
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/zaman_db"
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


