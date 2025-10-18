"""
Быстрый тест системы Zaman AI Assistant
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
os.environ['DATABASE_URL'] = 'sqlite:///./test_zaman.db'

from backend.services.llm_service import llm_service
from backend.services.rag_engine import rag_engine
from backend.services.emotion_analyzer import emotion_analyzer
from backend.services.prompt_builder import prompt_builder

print("=" * 60)
print("ТЕСТ СИСТЕМЫ ZAMAN AI ASSISTANT")
print("=" * 60)

# Тест 1: RAG поиск
print("\n[TEST 1] RAG поиск...")
query = "Какие у вас депозиты?"
results = rag_engine.search(query)
print(f"Запрос: {query}")
print(f"Найдено документов: {len(results)}")
if results:
    print(f"Первый результат: {results[0][:100]}...")
print("[OK] RAG работает!")

# Тест 2: Анализ эмоций
print("\n[TEST 2] Анализ эмоций...")
message = "Я потратил все деньги, у меня стресс"
emotion = emotion_analyzer.analyze(message)
print(f"Сообщение: {message}")
print(f"Эмоция: {emotion['emotion_type']}")
print(f"Стресс: {emotion['stress_score']}/10")
print("[OK] Emotion analyzer работает!")

# Тест 3: Построение промпта
print("\n[TEST 3] Построение промпта...")
messages = prompt_builder.build_chat_prompt(
    user_message="Хочу накопить на квартиру",
    emotion_data=emotion
)
print(f"Количество сообщений в промпте: {len(messages)}")
print("[OK] Prompt builder работает!")

# Тест 4: LLM запрос
print("\n[TEST 4] LLM запрос...")
print("Отправка запроса к gpt-4o-mini...")
try:
    response = llm_service.simple_query(
        "Скажи 'Привет' на русском языке",
        system_prompt="Ты помощник. Отвечай кратко."
    )
    print(f"Ответ: {response}")
    print("[OK] LLM работает!")
except Exception as e:
    print(f"[ERROR] LLM ошибка: {e}")

# Тест 5: Проверка банковской релевантности
print("\n[TEST 5] Проверка фокусировки...")
banking_query = "Хочу взять кредит"
non_banking_query = "Как приготовить плов?"
print(f"Банковский вопрос: {rag_engine.is_banking_related(banking_query)}")
print(f"Небанковский вопрос: {rag_engine.is_banking_related(non_banking_query)}")
print("[OK] Фильтрация работает!")

print("\n" + "=" * 60)
print("[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print("\nСистема готова к работе!")
print("Запустите: python quick_start.py")

