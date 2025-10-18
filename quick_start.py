"""
Быстрый старт для демонстрации на хакатоне
Использует SQLite вместо PostgreSQL для упрощения
"""
import os
import sys

# Изменение DATABASE_URL на SQLite
os.environ['DATABASE_URL'] = 'sqlite:///./zaman.db'

print("=" * 60)
print("ZAMAN AI ASSISTANT - БЫСТРЫЙ СТАРТ")
print("=" * 60)
print()
print("📌 Использование SQLite для упрощённого тестирования")
print()

# Проверка существования векторной базы
if not os.path.exists('chroma_db'):
    print("⚠️  База знаний не инициализирована!")
    print("   Запуск векторизации...")
    print()
    
    # Запуск векторизации
    from backend.services.rag_engine import rag_engine
    try:
        rag_engine.load_knowledge_base('knowledge')
    except Exception as e:
        print(f"❌ Ошибка при векторизации: {e}")
        sys.exit(1)
else:
    print("✓ База знаний уже инициализирована")

print()
print("🚀 Запуск API сервера...")
print("   API будет доступен на: http://localhost:8000")
print("   Документация: http://localhost:8000/docs")
print()
print("Для остановки нажмите Ctrl+C")
print("=" * 60)
print()

# Запуск FastAPI
if __name__ == "__main__":
    import uvicorn
    from backend.main import app
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

