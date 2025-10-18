# 🚀 Развертывание Zaman AI Assistant

## Требования

- Python 3.10+
- Виртуальное окружение (уже создано)
- API ключ OpenAI

## Быстрый запуск

### 1. Активация окружения
```bash
.\venv\Scripts\activate
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Инициализация базы знаний
```bash
python scripts/init_knowledge_base.py
```

### 4. Запуск сервера
```bash
python quick_start.py
```

### 5. Открыть интерфейс
Откройте `frontend/index.html` в браузере

## Доступ к сервисам

- **Frontend**: `frontend/index.html`
- **API**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Конфигурация

### API ключи
В `backend/config.py`:
```python
OPENAI_API_KEY = "your-api-key"
OPENAI_BASE_URL = "https://api.openai.com/v1"
```

### База данных
По умолчанию используется SQLite (`zaman.db`). Для PostgreSQL измените `DATABASE_URL` в `config.py`.

## Структура проекта

```
backend/          # FastAPI приложение
├── main.py       # Точка входа
├── config.py     # Конфигурация
├── models/       # Модели данных
├── services/     # Бизнес-логика
├── routers/      # API endpoints
└── utils/        # Утилиты

frontend/         # Пользовательский интерфейс
├── index.html    # Главная страница
├── app.js        # Логика приложения
└── styles.css    # Стили

knowledge/        # База знаний для RAG
├── faq.txt       # FAQ
├── products.txt  # Продукты банка
└── glossary.txt  # Глоссарий

chroma_db/        # Векторная база данных
```

## API Endpoints

### Основные
- `POST /api/chat` - Чат с AI
- `GET /api/goals/{user_id}` - Цели пользователя
- `POST /api/goals` - Создание цели
- `GET /api/challenges/{user_id}` - Челленджи
- `GET /api/profile/{user_id}` - Профиль

### Пример запроса
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "Хочу накопить на квартиру", "mode": "text"}'
```

## Устранение неполадок

### Ошибка импорта модулей
```bash
pip install -r requirements.txt
```

### База знаний не инициализирована
```bash
python scripts/init_knowledge_base.py
```

### Сервер не запускается
Проверьте, что порт 8000 свободен и API ключ валиден.

## Готово!

Проект готов к использованию. Все компоненты протестированы и работают.

