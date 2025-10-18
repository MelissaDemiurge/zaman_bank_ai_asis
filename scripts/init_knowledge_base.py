"""
Скрипт для инициализации базы знаний (векторизация)
"""
import sys
import os

# Добавление родительской директории в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.rag_engine import rag_engine

def main():
    """Главная функция"""
    # Set UTF-8 encoding for Windows console
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ЗНАНИЙ ZAMAN BANK")
    print("=" * 60)
    
    # Путь к базе знаний
    knowledge_dir = "knowledge"
    
    if not os.path.exists(knowledge_dir):
        print(f"[ERROR] Директория {knowledge_dir} не найдена!")
        return
    
    print(f"\n[INFO] Директория базы знаний: {knowledge_dir}")
    
    # Проверка файлов
    files = [f for f in os.listdir(knowledge_dir) if f.endswith('.txt')]
    print(f"[INFO] Найдено файлов: {len(files)}")
    for f in files:
        print(f"   - {f}")
    
    if not files:
        print("[ERROR] Нет файлов для обработки!")
        return
    
    # Загрузка и векторизация
    print("\n[INFO] Начинается векторизация...")
    try:
        rag_engine.load_knowledge_base(knowledge_dir)
        print("\n" + "=" * 60)
        print("[SUCCESS] БАЗА ЗНАНИЙ УСПЕШНО ИНИЦИАЛИЗИРОВАНА!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Ошибка при векторизации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

