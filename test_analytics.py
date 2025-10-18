"""
Тестовый скрипт для проверки увеличенных токенов в аналитике
"""
import requests
import json
import sys
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000/api"

def test_analytics_with_csv():
    """Полный тест аналитики с загрузкой CSV"""
    
    print("🚀 Тест улучшенной аналитики с увеличенными токенами\n")
    
    # 1. Создать пользователя
    print("1️⃣ Создание тестового пользователя...")
    response = requests.post(f"{API_BASE}/profile/create", json={
        "name": "Тестовый Пользователь (Аналитика)",
        "phone": f"+7700{__import__('random').randint(1000000, 9999999)}"
    })
    
    if response.status_code != 200:
        print(f"❌ Ошибка создания пользователя: {response.text}")
        return
    
    user_data = response.json()
    user_id = user_data["user"]["id"]
    print(f"✅ Пользователь создан: {user_id}\n")
    
    # 2. Загрузить CSV
    print("2️⃣ Загрузка банковской выписки...")
    with open("test_data/sample_statement.csv", "rb") as f:
        files = {"file": ("statement.csv", f, "text/csv")}
        response = requests.post(
            f"{API_BASE}/analytics/upload-statement/{user_id}",
            files=files
        )
    
    if response.status_code != 200:
        print(f"❌ Ошибка загрузки CSV: {response.text}")
        return
    
    result = response.json()
    print(f"✅ Загружено транзакций: {result['transactions_added']}\n")
    
    # 3. Проверить транзакции
    print("3️⃣ Проверка загруженных транзакций...")
    response = requests.get(f"{API_BASE}/analytics/transactions/{user_id}?limit=5")
    transactions = response.json()["transactions"]
    print(f"✅ Последние 5 транзакций:")
    for t in transactions[:5]:
        print(f"   - {t['date']}: {t['amount']:,.0f} ₸ | {t['description']}")
    print()
    
    # 4. Запросить детальный анализ
    print("4️⃣ Запрос развернутого анализа (с увеличенными токенами)...")
    response = requests.post(f"{API_BASE}/analytics/analyze", json={
        "user_id": user_id,
        "query": "Проанализируй подробно мои финансы. Где я трачу больше всего? Какие есть проблемы и как их решить?",
        "period_days": 60
    })
    
    if response.status_code != 200:
        print(f"❌ Ошибка анализа: {response.text}")
        return
    
    analysis = response.json()["analysis"]
    print("📊 АНАЛИЗ ФИНАНСОВ:")
    print("-" * 80)
    print(analysis)
    print("-" * 80)
    print(f"📏 Длина ответа: {len(analysis)} символов ({len(analysis.split())} слов)\n")
    
    # 5. Сравнительная аналитика
    print("5️⃣ Запрос сравнительной аналитики...")
    response = requests.post(f"{API_BASE}/analytics/compare", json={
        "user_id": user_id,
        "period_days": 60
    })
    
    if response.status_code != 200:
        print(f"❌ Ошибка сравнения: {response.text}")
        return
    
    insights = response.json()["analysis"]
    print("📈 СРАВНИТЕЛЬНАЯ АНАЛИТИКА:")
    print("-" * 80)
    print(insights)
    print("-" * 80)
    print(f"📏 Длина ответа: {len(insights)} символов ({len(insights.split())} слов)\n")
    
    print("✅ Тест завершен успешно!")
    print("\n💡 Настройки токенов:")
    print("   - Обычный чат: 2000 токенов (~1500 слов)")
    print("   - Аналитика: 3000 токенов (~2250 слов)")
    print("   - Короткие ответы: 500 токенов (~375 слов)")

if __name__ == "__main__":
    try:
        test_analytics_with_csv()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Не удается подключиться к API")
        print("   Убедитесь что бэкенд запущен: python backend/main.py")
    except FileNotFoundError:
        print("❌ Ошибка: Файл test_data/sample_statement.csv не найден")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()

