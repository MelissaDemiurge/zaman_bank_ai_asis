# 🚀 Инструкции по развертыванию Zaman AI Assistant

## ✅ Статус: Проект полностью готов к демонстрации!

Все компоненты протестированы и работают:
- ✅ RAG Engine (ChromaDB + Embeddings)
- ✅ LLM Service (gpt-4o-mini)
- ✅ Emotion Analyzer
- ✅ Prompt Builder
- ✅ База знаний векторизована

---

## 🎯 Быстрый старт (5 минут)

### Вариант 1: С SQLite (рекомендуется для демо)

```bash
# 1. Активировать виртуальное окружение
.\venv\Scripts\activate

# 2. Запустить сервер (он автоматически использует SQLite)
python quick_start.py
```

**Готово!** API доступен на `http://localhost:8000`

### Вариант 2: Ручной запуск

```bash
# Активировать venv
.\venv\Scripts\activate

# Запустить backend
cd backend
python main.py
```

---

## 🌐 Доступ к интерфейсам

### 1. Frontend (UI)
Откройте в браузере:
```
file:///C:/bank/frontend/index.html
```

Или запустите локальный сервер:
```bash
cd frontend
python -m http.server 3000
```
Затем откройте: `http://localhost:3000`

### 2. API Documentation (Swagger)
```
http://localhost:8000/docs
```

### 3. API Endpoint
```
http://localhost:8000/api/chat
```

---

## 🧪 Тестирование

### Быстрый тест системы
```bash
python test_system.py
```

### Тест через curl

**Простой вопрос:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"demo_user\", \"message\": \"Какие у вас депозиты?\", \"mode\": \"text\"}"
```

**Стресс-сценарий:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"demo_user\", \"message\": \"Я потратил все деньги, у меня стресс\", \"mode\": \"text\"}"
```

**Нефинансовый вопрос (проверка фокусировки):**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"demo_user\", \"message\": \"Как приготовить плов?\", \"mode\": \"text\"}"
```

Больше примеров в файле `API_EXAMPLES.md`

---

## 📊 Структура проекта

```
C:\bank\
├── backend/                  # Backend API
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация (API keys, промпты)
│   ├── models/              # SQLAlchemy модели
│   ├── services/            # Бизнес-логика
│   ├── routers/             # API endpoints
│   └── utils/               # Утилиты
├── frontend/                # Frontend UI
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── knowledge/               # База знаний
│   ├── faq.txt
│   ├── glossary.txt
│   └── products.txt
├── chroma_db/              # Векторная БД (создается автоматически)
├── scripts/
│   └── init_knowledge_base.py
├── quick_start.py          # Быстрый запуск
├── test_system.py          # Тесты
└── README.md
```

---

## 🔧 Конфигурация

### API Keys и Base URL

В файле `backend/config.py`:

```python
OPENAI_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
OPENAI_BASE_URL = "https://openai-hub.neuraldeep.tech"
```

### База данных

**По умолчанию (SQLite):**
```python
DATABASE_URL = "sqlite:///./zaman.db"
```

**Для продакшена (PostgreSQL):**
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/zaman_db"
```

---

## 🎬 Сценарии для демонстрации на хакатоне

### Сценарий 1: "Новый клиент с финансовой целью"

1. Откройте frontend (`index.html`)
2. Напишите: **"Здравствуйте! Я хочу накопить на квартиру, можете помочь?"**
3. Покажите ответ с рекомендацией депозита
4. Через Swagger создайте цель (POST /api/goals)
5. Напишите: **"Какой депозит лучше всего подойдёт для моей цели?"**
6. Покажите, что AI учитывает цель в ответе

**Что демонстрирует:** RAG + контекст целей + персонализация

### Сценарий 2: "Клиент в финансовом стрессе"

1. Напишите: **"Я опять потратил все деньги на ерунду из-за стресса"**
2. Покажите анализ эмоций (stress_score: 8/10)
3. Покажите эмпатичный ответ с альтернативами стресс-покупкам
4. Через Swagger создайте челлендж (POST /api/challenges с type: "stress_management")
5. Покажите прогресс челленджа

**Что демонстрирует:** Emotion analysis + эмпатия + геймификация

### Сценарий 3: "Вопросы об исламских финансах"

1. **"Чем исламский депозит отличается от обычного?"**
2. **"Что такое Мурабаха?"**
3. **"Почему риба запрещена?"**

**Что демонстрирует:** RAG на базе знаний + глубокое понимание исламских финансов

### Сценарий 4: "Проверка фокусировки"

1. **"Какая погода сегодня?"** → Отказ
2. **"Как приготовить плов?"** → Отказ
3. **"Хочу взять кредит на авто"** → Помощь

**Что демонстрирует:** Строгая фокусировка на банкинге

---

## 🏆 Уникальные фичи для презентации

### 1. Эмоциональный интеллект
- Real-time анализ стресса
- Адаптивные ответы
- Emotional DNA (GET /api/profile/{user_id})

### 2. Строгая фокусировка
- Отказ от нефинансовых тем
- RAG только на банковской базе

### 3. Исламская геймификация
- Челленджи без азарта
- Духовные награды (Сабр, Баракат)

### 4. Проактивность
- Триггеры на стресс, дедлайны, неактивность
- Бот сам пишет клиенту (POST /api/proactive/check/{user_id})

### 5. Голосовой режим
- Whisper-1 для speech-to-text
- Seamless переключение text/voice

---

## 📈 Метрики для презентации

- **База знаний:** 31 чанк (FAQ + Продукты + Глоссарий)
- **RAG:** Top-3 релевантных документа на запрос
- **Emotion Detection:** 10-балльная шкала стресса
- **Модели:** gpt-4o-mini, text-embedding-3-small, whisper-1
- **Архитектура:** Микросервисная (7 сервисов)
- **API:** 12+ endpoints

---

## 🐛 Troubleshooting

### Проблема: "ModuleNotFoundError"
```bash
# Установите зависимости
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Проблема: "База знаний не найдена"
```bash
# Запустите векторизацию
python scripts\init_knowledge_base.py
```

### Проблема: "API не отвечает"
```bash
# Проверьте, что сервер запущен
curl http://localhost:8000/health
```

### Проблема: Ошибка с numpy
```bash
# Установите совместимую версию
pip install "numpy>=1.24.0,<2.0.0" --force-reinstall
```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи сервера
2. Запустите `python test_system.py`
3. Проверьте наличие `chroma_db/` директории
4. Убедитесь, что API key валиден

---

## 🎓 Дополнительные материалы

- `README.md` - Полная документация
- `API_EXAMPLES.md` - Примеры API запросов
- `test_system.py` - Системные тесты

---

## 🚀 Готово к демонстрации!

Проект полностью готов для презентации на HackNU/25. Все компоненты протестированы и работают!

**Удачи на хакатоне! 🏆**

