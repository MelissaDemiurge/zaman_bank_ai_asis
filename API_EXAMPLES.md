# API Examples для тестирования Zaman AI Assistant

## 1. Chat Endpoint (Главный)

### Текстовый режим - Обычный вопрос
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "Какие у вас есть депозиты?",
    "mode": "text"
  }'
```

### Вопрос про финансовую цель
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "Хочу накопить 500,000 тенге на обучение за год",
    "mode": "text"
  }'
```

### Стресс-сценарий
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "Я опять потратил все деньги на ерунду, у меня стресс, что делать?",
    "mode": "text"
  }'
```

### Нефинансовый вопрос (проверка фокусировки)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "Как приготовить плов?",
    "mode": "text"
  }'
```

### Вопрос про исламские финансы
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "Что такое Мурабаха и чем она отличается от обычного кредита?",
    "mode": "text"
  }'
```

### Вопрос про покупку квартиры
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "Я хочу купить квартиру, какие у вас есть варианты?",
    "mode": "text"
  }'
```

---

## 2. Goals (Цели)

### Создание цели
```bash
curl -X POST "http://localhost:8000/api/goals" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "title": "Квартира",
    "target_amount": 15000000,
    "deadline_months": 36
  }'
```

### Получение целей пользователя
```bash
curl -X GET "http://localhost:8000/api/goals/test_user_1"
```

### Обновление прогресса цели
```bash
curl -X PATCH "http://localhost:8000/api/goals/{goal_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "current_amount": 2000000
  }'
```

### Пример: Создать несколько целей
```bash
# Цель 1: Обучение
curl -X POST "http://localhost:8000/api/goals" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "title": "Обучение",
    "target_amount": 500000,
    "deadline_months": 12
  }'

# Цель 2: Автомобиль
curl -X POST "http://localhost:8000/api/goals" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "title": "Автомобиль",
    "target_amount": 5000000,
    "deadline_months": 24
  }'
```

---

## 3. Challenges (Челленджи)

### Получить список доступных шаблонов
```bash
curl -X GET "http://localhost:8000/api/challenges/templates/list"
```

### Создать челлендж "30 дней без импульсивных трат"
```bash
curl -X POST "http://localhost:8000/api/challenges" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "challenge_type": "no_impulse"
  }'
```

### Создать челлендж "Накопить 100К"
```bash
curl -X POST "http://localhost:8000/api/challenges" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "challenge_type": "savings"
  }'
```

### Получить челленджи пользователя
```bash
curl -X GET "http://localhost:8000/api/challenges/test_user_1"
```

### Обновить прогресс челленджа
```bash
curl -X PATCH "http://localhost:8000/api/challenges/{challenge_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "current_value": 25
  }'
```

---

## 4. Profile (Эмоциональный профиль)

### Получить эмоциональный профиль
```bash
curl -X GET "http://localhost:8000/api/profile/test_user_1"
```

### Проверить проактивные триггеры
```bash
curl -X POST "http://localhost:8000/api/proactive/check/test_user_1"
```

---

## 5. Conversation History

### Получить историю диалога
```bash
curl -X GET "http://localhost:8000/api/conversation/test_user_1"
```

---

## Сценарии для демонстрации на хакатоне

### Сценарий 1: "Новый клиент с целью"
```bash
# Шаг 1: Первый вопрос
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "message": "Здравствуйте! Я хочу накопить на квартиру, можете помочь?",
    "mode": "text"
  }'

# Шаг 2: Создание цели
curl -X POST "http://localhost:8000/api/goals" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "title": "Квартира",
    "target_amount": 15000000,
    "deadline_months": 36
  }'

# Шаг 3: Запрос совета с учётом цели
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "message": "Какой депозит лучше всего подойдёт для моей цели?",
    "mode": "text"
  }'
```

### Сценарий 2: "Клиент в стрессе"
```bash
# Шаг 1: Стресс-сообщение
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_2",
    "message": "У меня плохой день, я потратил много денег на ерунду из-за стресса",
    "mode": "text"
  }'

# Шаг 2: Проверка эмоционального профиля
curl -X GET "http://localhost:8000/api/profile/demo_user_2"

# Шаг 3: Создание челленджа
curl -X POST "http://localhost:8000/api/challenges" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_2",
    "challenge_type": "stress_management"
  }'
```

### Сценарий 3: "Вопросы об исламских финансах"
```bash
# Вопрос 1
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_3",
    "message": "Чем исламский депозит отличается от обычного?",
    "mode": "text"
  }'

# Вопрос 2
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_3",
    "message": "Что такое риба и почему это харам?",
    "mode": "text"
  }'

# Вопрос 3
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_3",
    "message": "Можно ли взять кредит в исламском банке?",
    "mode": "text"
  }'
```

---

## Тестирование через Swagger UI

Откройте браузер и перейдите на:
```
http://localhost:8000/docs
```

Там вы найдёте интерактивную документацию API с возможностью тестирования всех endpoints.

---

## Проверка здоровья API

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "healthy",
  "service": "Zaman AI Assistant"
}
```

