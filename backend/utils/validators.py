"""
Валидаторы для входных данных
"""
import re
from typing import Optional

def is_valid_phone(phone: str) -> bool:
    """Проверка формата телефона"""
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone))

def is_valid_amount(amount: float) -> bool:
    """Проверка суммы"""
    return amount > 0 and amount <= 100_000_000

def sanitize_input(text: str) -> str:
    """Очистка пользовательского ввода"""
    # Удаление потенциально опасных символов
    text = text.strip()
    # Ограничение длины
    max_length = 2000
    if len(text) > max_length:
        text = text[:max_length]
    return text

def extract_goal_amount(text: str) -> Optional[float]:
    """Извлечение суммы из текста"""
    # Поиск чисел в тексте
    numbers = re.findall(r'[\d\s]+', text.replace(',', ''))
    for num in numbers:
        try:
            amount = float(num.replace(' ', ''))
            if is_valid_amount(amount):
                return amount
        except ValueError:
            continue
    return None

