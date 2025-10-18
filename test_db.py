"""
Тест базы данных с новым типом GUID
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
os.environ['DATABASE_URL'] = 'sqlite:///./test_zaman.db'

print("=" * 60)
print("ТЕСТ БАЗЫ ДАННЫХ")
print("=" * 60)

# Импорт моделей
from backend.models.user import User
from backend.models.conversation import Conversation
from backend.models.goal import Goal
from backend.models.emotion_log import EmotionLog
from backend.models.challenge import Challenge
from backend.utils.db import init_db, SessionLocal
import uuid

print("\n[TEST 1] Создание таблиц...")
try:
    init_db()
    print("[OK] Таблицы созданы успешно!")
except Exception as e:
    print(f"[ERROR] Ошибка создания таблиц: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST 2] Создание пользователя...")
try:
    db = SessionLocal()
    
    # Создание пользователя
    user = User(name="Test User", phone="+77001234567")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"[OK] Пользователь создан с ID: {user.id}")
    print(f"     Тип ID: {type(user.id)}")
    
    # Проверка загрузки
    loaded_user = db.query(User).filter(User.id == user.id).first()
    print(f"[OK] Пользователь загружен: {loaded_user.name}")
    
    db.close()
    
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print("\nБаза данных работает корректно!")
print("Можно запускать: python quick_start.py")

