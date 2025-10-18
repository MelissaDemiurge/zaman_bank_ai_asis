"""
Главное приложение FastAPI для Zaman AI Assistant
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, goals, challenges, profile
from backend.utils.db import init_db

app = FastAPI(
    title="Zaman AI Assistant API",
    description="AI-ассистент нового поколения для Zaman Bank",
    version="1.0.0"
)

# CORS middleware для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(goals.router, prefix="/api", tags=["Goals"])
app.include_router(challenges.router, prefix="/api", tags=["Challenges"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    print("🚀 Запуск Zaman AI Assistant...")
    print("📊 Инициализация базы данных...")
    init_db()
    print("✓ База данных готова!")
    print("✓ API готов к работе!")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Добро пожаловать в Zaman AI Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "goals": "/api/goals",
            "challenges": "/api/challenges",
            "profile": "/api/profile/{user_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "healthy", "service": "Zaman AI Assistant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

