"""
RAG Engine для работы с базой знаний Zaman Bank
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple
from backend.config import (
    CHROMA_PERSIST_DIR, 
    CHROMA_COLLECTION_NAME,
    TOP_K_RESULTS,
    CHUNK_SIZE
)
from backend.services.llm_service import llm_service
import os
import re

class RAGEngine:
    """Система поиска релевантной информации из базы знаний"""
    
    def __init__(self):
        # Инициализация ChromaDB
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # Получение или создание коллекции
        try:
            self.collection = self.client.get_collection(name=CHROMA_COLLECTION_NAME)
            print(f"Загружена существующая коллекция: {CHROMA_COLLECTION_NAME}")
        except:
            self.collection = self.client.create_collection(name=CHROMA_COLLECTION_NAME)
            print(f"Создана новая коллекция: {CHROMA_COLLECTION_NAME}")
    
    def chunk_text(self, text: str, source: str) -> List[Tuple[str, Dict]]:
        """
        Разбивка текста на чанки
        
        Args:
            text: Исходный текст
            source: Источник текста (имя файла)
            
        Returns:
            Список кортежей (текст_чанка, метаданные)
        """
        chunks = []
        
        # Разбивка по разделителям (двойной перенос или знаки равенства)
        sections = re.split(r'\n\n+|═{3,}', text)
        
        current_chunk = ""
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Если добавление секции превысит размер чанка
            if len(current_chunk) + len(section) > CHUNK_SIZE and current_chunk:
                chunks.append((
                    current_chunk.strip(),
                    {"source": source, "type": self._detect_content_type(current_chunk)}
                ))
                current_chunk = section
            else:
                current_chunk += "\n\n" + section if current_chunk else section
        
        # Добавление последнего чанка
        if current_chunk:
            chunks.append((
                current_chunk.strip(),
                {"source": source, "type": self._detect_content_type(current_chunk)}
            ))
        
        return chunks
    
    def _detect_content_type(self, text: str) -> str:
        """Определение типа контента"""
        text_lower = text.lower()
        
        if "вопрос:" in text_lower or "ответ:" in text_lower:
            return "faq"
        elif "продукт" in text_lower or "депозит" in text_lower or "финансирование" in text_lower:
            return "product"
        elif "определение:" in text_lower or "как работает:" in text_lower:
            return "glossary"
        else:
            return "general"
    
    def load_knowledge_base(self, knowledge_dir: str = "knowledge"):
        """
        Загрузка и векторизация базы знаний
        
        Args:
            knowledge_dir: Директория с файлами базы знаний
        """
        print(f"Загрузка базы знаний из {knowledge_dir}...")
        
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        # Обработка всех .txt файлов
        for filename in os.listdir(knowledge_dir):
            if not filename.endswith('.txt'):
                continue
            
            filepath = os.path.join(knowledge_dir, filename)
            print(f"Обработка файла: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разбивка на чанки
            chunks = self.chunk_text(content, filename)
            
            for idx, (chunk_text, metadata) in enumerate(chunks):
                chunk_id = f"{filename}_{idx}"
                all_chunks.append(chunk_text)
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)
        
        print(f"Всего чанков: {len(all_chunks)}")
        
        # Векторизация через LLM service
        print("Векторизация чанков...")
        embeddings = []
        for i, chunk in enumerate(all_chunks):
            if i % 10 == 0:
                print(f"  Обработано {i}/{len(all_chunks)}")
            embedding = llm_service.get_embedding(chunk)
            embeddings.append(embedding)
        
        # Добавление в ChromaDB
        print("Сохранение в ChromaDB...")
        self.collection.add(
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadatas,
            ids=all_ids
        )
        
        print(f"✓ База знаний загружена! Всего документов: {len(all_chunks)}")
    
    def search(self, query: str, top_k: int = TOP_K_RESULTS) -> List[str]:
        """
        Семантический поиск по базе знаний
        
        Args:
            query: Запрос пользователя
            top_k: Количество результатов
            
        Returns:
            Список релевантных текстов
        """
        # Векторизация запроса
        query_embedding = llm_service.get_embedding(query)
        
        if not query_embedding:
            return []
        
        # Поиск в ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        if not results or not results['documents']:
            return []
        
        # Возврат документов
        return results['documents'][0]
    
    def get_context(self, query: str) -> str:
        """
        Получение контекста для промпта
        
        Args:
            query: Запрос пользователя
            
        Returns:
            Форматированный контекст из базы знаний
        """
        documents = self.search(query)
        
        if not documents:
            return "Контекст из базы знаний не найден."
        
        # Форматирование контекста
        context = "=== КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ ZAMAN BANK ===\n\n"
        for i, doc in enumerate(documents, 1):
            context += f"[Источник {i}]\n{doc}\n\n"
        
        return context
    
    def is_banking_related(self, query: str) -> bool:
        """
        Проверка, относится ли вопрос к банковской тематике
        
        Args:
            query: Запрос пользователя
            
        Returns:
            True если вопрос о финансах/банке
        """
        banking_keywords = [
            'депозит', 'кредит', 'финансирование', 'банк', 'деньги', 'накопить',
            'купить', 'цель', 'сумма', 'тенге', 'мурабаха', 'вакала', 'иджара',
            'счет', 'карта', 'процент', 'риба', 'халяль', 'харам', 'шариат',
            'инвестиция', 'бизнес', 'займ', 'ипотека', 'автокредит', 'недвижимость',
            'квартира', 'автомобиль', 'обучение', 'стресс', 'трата', 'накопление'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in banking_keywords)

# Singleton instance
rag_engine = RAGEngine()

