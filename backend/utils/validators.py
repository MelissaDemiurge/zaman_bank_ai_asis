"""
Валидаторы для входных данных
"""
import re
from typing import Optional


def sanitize_input(text: str) -> str:
    """Очистка пользовательского ввода"""
    # Удаление потенциально опасных символов
    text = text.strip()
    # Ограничение длины
    max_length = 2000
    if len(text) > max_length:
        text = text[:max_length]
    return text


