"""
Сервис для работы с голосом (Whisper-1)
"""
from openai import OpenAI
from backend.config import OPENAI_API_KEY, OPENAI_BASE_URL, WHISPER_MODEL
import base64
import io
from typing import Optional

class VoiceService:
    """Работа с речью: распознавание и синтез"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        self.whisper_model = WHISPER_MODEL
    
    def speech_to_text(self, audio_data: bytes, audio_format: str = "webm") -> Optional[str]:
        """
        Преобразование речи в текст
        
        Args:
            audio_data: Аудио данные в байтах
            audio_format: Формат аудио (webm, mp3, wav, etc.)
            
        Returns:
            Распознанный текст или None при ошибке
        """
        try:
            # Создание file-like объекта
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"
            
            # Запрос к Whisper API
            response = self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file,
                language="ru"  # Русский язык
            )
            
            return response.text.strip()
        except Exception as e:
            print(f"Error in speech_to_text: {e}")
            return None
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Преобразование текста в речь
        
        Args:
            text: Текст для озвучивания
            
        Returns:
            Аудио данные в байтах или None при ошибке
        """
        try:
            # Проверка наличия TTS endpoint
            response = self.client.audio.speech.create(
                model="tts-1",  # Попытка использовать TTS модель
                voice="alloy",
                input=text
            )
            
            return response.content
        except Exception as e:
            print(f"TTS not available or error: {e}")
            # TTS может быть недоступен в данном API
            return None
    
    def decode_base64_audio(self, base64_audio: str) -> bytes:
        """
        Декодирование base64 аудио
        
        Args:
            base64_audio: Аудио в base64
            
        Returns:
            Байты аудио
        """
        return base64.b64decode(base64_audio)
    
    def encode_audio_to_base64(self, audio_data: bytes) -> str:
        """
        Кодирование аудио в base64
        
        Args:
            audio_data: Байты аудио
            
        Returns:
            Base64 строка
        """
        return base64.b64encode(audio_data).decode('utf-8')

# Singleton instance
voice_service = VoiceService()

