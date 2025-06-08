"""
Модуль индексации данных в векторную базу данных
Использует ChromaDB для хранения эмбеддингов и метаданных
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import math
import re

from config import config
from ..data_processor import DocumentChunk


class Indexer:
    """Класс для индексации документов в векторную базу данных"""
    
    def __init__(self):
        """Инициализация индексатора"""
        # Инициализируем модель эмбеддингов
        logger.info(f"Загружаю модель эмбеддингов: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Инициализируем ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(allow_reset=True)
        )
        
        # Получаем или создаем коллекцию
        try:
            self.collection = self.chroma_client.get_collection(
                name=config.CHROMA_COLLECTION_NAME
            )
            logger.info(f"Загружена существующая коллекция: {config.CHROMA_COLLECTION_NAME}")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=config.CHROMA_COLLECTION_NAME,
                metadata={"description": "Lysobacter knowledge base collection"}
            )
            logger.info(f"Создана новая коллекция: {config.CHROMA_COLLECTION_NAME}")
    
    def index_chunks(self, chunks: List[DocumentChunk], batch_size: int = 10) -> bool:
        """
        Индексирует список чанков в векторную базу данных
        
        Args:
            chunks (List[DocumentChunk]): Чанки для индексации
            batch_size (int): Размер батча для обработки
            
        Returns:
            bool: True если индексация прошла успешно
        """
        try:
            logger.info(f"Начинаю индексацию {len(chunks)} чанков")
            
            # Проверяем на дубликаты
            existing_ids = self._get_existing_ids()
            new_chunks = [chunk for chunk in chunks if chunk.chunk_id not in existing_ids]
            
            if not new_chunks:
                logger.info("Все чанки уже проиндексированы")
                return True
            
            logger.info(f"Найдено {len(new_chunks)} новых чанков для индексации")
            
            # Обрабатываем чанки батчами
            for i in tqdm(range(0, len(new_chunks), batch_size), desc="Индексация батчей"):
                batch = new_chunks[i:i + batch_size]
                self._index_batch(batch)
            
            logger.info(f"Успешно проиндексировано {len(new_chunks)} чанков")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при индексации: {str(e)}")
            return False
    
    def _get_existing_ids(self) -> set:
        """
        Получает список уже существующих ID чанков
        
        Returns:
            set: Множество существующих ID
        """
        try:
            result = self.collection.get(include=["metadatas"])
            existing_ids = set()
            
            if result and result['metadatas']:
                for metadata in result['metadatas']:
                    if metadata and 'chunk_id' in metadata:
                        existing_ids.add(metadata['chunk_id'])
            
            return existing_ids
            
        except Exception as e:
            logger.warning(f"Не удалось получить существующие ID: {str(e)}")
            return set()
    
    def _index_batch(self, batch: List[DocumentChunk]):
        """
        Индексирует батч чанков
        
        Args:
            batch (List[DocumentChunk]): Батч чанков для индексации
        """
        # Извлекаем тексты
        texts = [chunk.text for chunk in batch]
        
        # Создаем эмбеддинги
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
        
        # Подготавливаем данные для ChromaDB
        ids = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(batch):
            # Создаем уникальный ID для ChromaDB (используем UUID если chunk_id не уникален)
            chroma_id = str(uuid.uuid4())
            ids.append(chroma_id)
            
            # Подготавливаем метаданные (ChromaDB требует строковые значения)
            metadata = {
                'chunk_id': chunk.chunk_id,
                'source_pdf': chunk.metadata.get('source_pdf', ''),
                'page_number': str(chunk.metadata.get('page_number', '')),
                'chunk_type': chunk.chunk_type,
            }
            
            # Добавляем дополнительные метаданные в зависимости от типа чанка
            if chunk.chunk_type == 'table':
                metadata.update({
                    'original_table_title': chunk.metadata.get('original_table_title', ''),
                    'table_description': chunk.metadata.get('table_description', ''),
                    'confidence_score': str(chunk.metadata.get('confidence_score', '')),
                    'table_shape': chunk.metadata.get('table_shape', '')
                })
            elif chunk.chunk_type == 'text':
                metadata.update({
                    'chunk_index': str(chunk.metadata.get('chunk_index', '')),
                    'total_chunks': str(chunk.metadata.get('total_chunks', ''))
                })
            
            metadatas.append(metadata)
            documents.append(chunk.text)
        
        # Добавляем в коллекцию
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=documents
        )
    
    def search(self, query: str, top_k: int = 5, chunk_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Выполняет семантический поиск по векторной базе данных
        
        Args:
            query (str): Поисковый запрос
            top_k (int): Количество результатов для возврата
            chunk_type (Optional[str]): Фильтр по типу чанка ('text' или 'table')
            
        Returns:
            List[Dict[str, Any]]: Список найденных релевантных чанков
        """
        try:
            # Создаем эмбеддинг для запроса
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
            
            # Подготавливаем фильтр по типу чанка
            where_filter = None
            if chunk_type:
                where_filter = {"chunk_type": chunk_type}
            
            # Выполняем поиск
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Формируем результаты
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i]
                    
                    # Улучшенный расчет релевантности
                    # Используем логарифмическую нормализацию для больших дистанций
                    if distance < 0.1:
                        # Очень близкие результаты
                        normalized_relevance = 1.0
                    elif distance < 5:
                        # Хорошие результаты
                        normalized_relevance = max(0.0, 1.0 - (distance / 10.0))
                    else:
                        # Используем логарифмическую шкалу для больших дистанций
                        normalized_relevance = max(0.0, 1.0 / (1 + math.log10(distance)))
                    
                    result = {
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': distance,
                        'relevance_score': normalized_relevance,  # Новый расчет релевантности
                        'raw_relevance': 1 - distance  # Старый расчет для совместимости
                    }
                    search_results.append(result)
            
            logger.info(f"Найдено {len(search_results)} релевантных чанков для запроса: '{query[:50]}...'")
            return search_results
            
        except Exception as e:
            logger.error(f"Ошибка при поиске: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику коллекции
        
        Returns:
            Dict[str, Any]: Статистика коллекции
        """
        try:
            result = self.collection.get(include=["metadatas"])
            
            total_chunks = len(result['metadatas']) if result['metadatas'] else 0
            
            # Подсчитываем статистику по типам чанков
            chunk_types = {}
            sources = set()
            
            if result['metadatas']:
                for metadata in result['metadatas']:
                    if metadata:
                        chunk_type = metadata.get('chunk_type', 'unknown')
                        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
                        
                        source = metadata.get('source_pdf', '')
                        if source:
                            sources.add(source)
            
            stats = {
                'total_chunks': total_chunks,
                'chunk_types': chunk_types,
                'unique_sources': len(sources),
                'sources': list(sources)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {str(e)}")
            return {}
    
    def delete_collection(self):
        """Удаляет коллекцию (для очистки данных)"""
        try:
            self.chroma_client.delete_collection(config.CHROMA_COLLECTION_NAME)
            logger.info(f"Коллекция {config.CHROMA_COLLECTION_NAME} удалена")
        except Exception as e:
            logger.error(f"Ошибка при удалении коллекции: {str(e)}")
    
    def rebuild_index(self, chunks: List[DocumentChunk]) -> bool:
        """
        Полностью пересоздает индекс
        
        Args:
            chunks (List[DocumentChunk]): Чанки для индексации
            
        Returns:
            bool: True если пересоздание прошло успешно
        """
        logger.info("Начинаю полное пересоздание индекса")
        
        # Удаляем старую коллекцию
        self.delete_collection()
        
        # Создаем новую коллекцию
        self.collection = self.chroma_client.create_collection(
            name=config.CHROMA_COLLECTION_NAME,
            metadata={"description": "Lysobacter knowledge base collection"}
        )
        
        # Индексируем все чанки
        return self.index_chunks(chunks)
    
    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Гибридный поиск: семантический + ключевые слова
        Решает проблему с поиском идентификаторов штаммов
        """
        logger.info(f"Выполняю гибридный поиск для: '{query[:50]}...'")
        
        # 1. Точный поиск по ключевым словам (особенно для штаммов)
        exact_matches = self._exact_keyword_search(query, top_k=50)
        
        # 2. Семантический поиск
        semantic_results = self.search(query, top_k=top_k)
        
        # 3. Объединяем и ранжируем результаты
        combined_results = self._combine_and_rank_results(
            exact_matches, semantic_results, query
        )
        
        logger.info(f"Найдено {len(combined_results)} результатов гибридного поиска")
        return combined_results[:top_k]
    
    def _exact_keyword_search(self, query: str, top_k: int = 50) -> List[Dict[str, Any]]:
        """
        Точный поиск по ключевым словам в документах
        """
        # Паттерны для распознавания идентификаторов штаммов
        strain_patterns = [
            r'\b[A-Z]{1,3}\d{3,5}[A-Z]*\b',  # YC5194, GW1-59T и т.д.
            r'\b[A-Z]+-?\d+[A-Z]*\b',        # различные варианты
        ]
        
        keywords = [query.strip()]
        
        # Извлекаем паттерны штаммов из запроса
        for pattern in strain_patterns:
            matches = re.findall(pattern, query.upper())
            keywords.extend(matches)
        
        # Получаем все документы
        all_data = self.collection.get()
        exact_results = []
        
        if all_data['documents']:
            for i, doc in enumerate(all_data['documents']):
                doc_upper = doc.upper()
                score = 0
                
                # Подсчитываем точные совпадения
                for keyword in keywords:
                    keyword_upper = keyword.upper()
                    count = doc_upper.count(keyword_upper)
                    if count > 0:
                        score += count * 10  # Высокий вес для точных совпадений
                
                if score > 0:
                    metadata = all_data['metadatas'][i]
                    exact_results.append({
                        'text': doc,
                        'metadata': metadata,
                        'relevance_score': min(score / 100.0, 1.0),
                        'search_type': 'exact'
                    })
        
        # Сортируем по релевантности
        exact_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return exact_results[:top_k]
    
    def _combine_and_rank_results(self, exact_results, semantic_results, query):
        """
        Объединяем точные и семантические результаты
        """
        combined = {}
        
        # Добавляем точные результаты с высоким приоритетом
        for result in exact_results:
            doc_text = result['text']
            if doc_text not in combined:
                combined[doc_text] = result
                combined[doc_text]['final_score'] = result['relevance_score'] + 0.5  # Бонус за точность
            
        # Добавляем семантические результаты
        for result in semantic_results:
            doc_text = result['text']
            if doc_text not in combined:
                combined[doc_text] = result
                combined[doc_text]['final_score'] = result['relevance_score']
                combined[doc_text]['search_type'] = 'semantic'
            else:
                # Если документ уже есть, комбинируем скоры
                combined[doc_text]['final_score'] += result['relevance_score'] * 0.3
        
        # Сортируем по финальному скору
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return final_results


if __name__ == "__main__":
    # Пример использования
    from ..pdf_extractor import PDFExtractor
    from ..data_processor import DataProcessor
    
    # Извлекаем данные из PDF
    extractor = PDFExtractor()
    docs = extractor.extract_all_pdfs(str(config.DATA_DIR))
    
    # Обрабатываем в чанки
    processor = DataProcessor()
    chunks = processor.process_documents(docs)
    
    # Индексируем
    indexer = Indexer()
    success = indexer.index_chunks(chunks)
    
    if success:
        # Показываем статистику
        stats = indexer.get_collection_stats()
        print("Статистика индексации:")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Тестовый поиск
        results = indexer.search("phenotypic characteristics", top_k=3)
        print(f"\nНайдено {len(results)} результатов для тестового запроса")
        for i, result in enumerate(results):
            print(f"{i+1}. Релевантность: {result['relevance_score']:.3f}")
            print(f"   Источник: {result['metadata']['source_pdf']}")
            print(f"   Текст: {result['text'][:100]}...")
            print() 