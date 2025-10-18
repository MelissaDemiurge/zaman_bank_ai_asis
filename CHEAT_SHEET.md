# 🎯 Zaman AI Assistant - Шпаргалка

## ⚡ Команды для быстрого запуска

### 1️⃣ Активация окружения
```bash
.\venv\Scripts\activate
```

### 2️⃣ Быстрый старт
```bash
python quick_start.py
```

### 3️⃣ Тестирование
```bash
python test_system.py
```

---

## 🔗 Важные URL

| Ресурс | URL |
|--------|-----|
| API Swagger | http://localhost:8000/docs |
| API Base | http://localhost:8000/api |
| Health Check | http://localhost:8000/health |
| Frontend | file:///C:/bank/frontend/index.html |

---

## 📡 Примеры curl запросов

### Обычный вопрос
```bash
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"user_id\": \"demo\", \"message\": \"Какие у вас депозиты?\", \"mode\": \"text\"}"
```

### Стресс-сценарий
```bash
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"user_id\": \"demo\", \"message\": \"Я потратил все деньги, у меня стресс\", \"mode\": \"text\"}"
```

### Нефинансовый вопрос
```bash
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"user_id\": \"demo\", \"message\": \"Как приготовить плов?\", \"mode\": \"text\"}"
```

### Создать цель
```bash
curl -X POST "http://localhost:8000/api/goals" -H "Content-Type: application/json" -d "{\"user_id\": \"demo\", \"title\": \"Квартира\", \"target_amount\": 15000000, \"deadline_months\": 36}"
```

### Получить профиль
```bash
curl -X GET "http://localhost:8000/api/profile/demo"
```

### Создать челлендж
```bash
curl -X POST "http://localhost:8000/api/challenges" -H "Content-Type: application/json" -d "{\"user_id\": \"demo\", \"challenge_type\": \"no_impulse\"}"
```

---

## 📂 Важные файлы

| Файл | Описание |
|------|----------|
| `backend/config.py` | API keys, системные промпты |
| `backend/main.py` | FastAPI приложение |
| `backend/services/rag_engine.py` | RAG + ChromaDB |
| `frontend/index.html` | UI интерфейс |
| `knowledge/*.txt` | База знаний |
| `test_system.py` | Системные тесты |

---

## 🛠️ Troubleshooting

### Ошибка: "База знаний не найдена"
```bash
python scripts\init_knowledge_base.py
```

### Ошибка: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Ошибка: Numpy version
```bash
pip install "numpy>=1.24.0,<2.0.0" --force-reinstall
```

### Проверка здоровья API
```bash
curl http://localhost:8000/health
```

---

## 🎬 Демо для жюри (5 минут)

### 1. Запуск (30 сек)
```bash
.\venv\Scripts\activate
python quick_start.py
```

### 2. Открыть Swagger (10 сек)
```
http://localhost:8000/docs
```

### 3. Тест в Swagger (2 мин)

**Запрос 1:** POST /api/chat
```json
{
  "user_id": "judge_demo",
  "message": "Какие у вас депозиты?",
  "mode": "text"
}
```

**Запрос 2:** POST /api/chat
```json
{
  "user_id": "judge_demo",
  "message": "Я потратил все деньги на ерунду, стресс",
  "mode": "text"
}
```

**Запрос 3:** GET /api/profile/judge_demo

**Запрос 4:** POST /api/chat
```json
{
  "user_id": "judge_demo",
  "message": "Как приготовить плов?",
  "mode": "text"
}
```

### 4. Показать Frontend (2 мин)
Открыть `frontend/index.html`

---

## 📊 Ключевые метрики для презентации

- ✅ **31 чанк** в базе знаний
- ✅ **7 микросервисов** (RAG, LLM, Emotion, Voice, etc.)
- ✅ **12+ API endpoints**
- ✅ **5 таблиц БД** (Users, Goals, Emotions, etc.)
- ✅ **4 типа триггеров** для проактивности
- ✅ **Emotion scoring** 1-10 scale
- ✅ **Исламская геймификация** без азарта

---

## 💡 Уникальные фичи для акцента

1. **Строгая фокусировка** - отказ от нефинансовых тем
2. **Эмоциональный интеллект** - real-time анализ стресса
3. **Проактивность** - бот сам пишет клиенту
4. **Исламская этика** - только халяльные продукты
5. **RAG на исламских финансах** - deep knowledge base

---

## 🏆 Готово к демонстрации!

Все компоненты работают. Проект готов для HackNU/25!

**Удачи! 🚀**

