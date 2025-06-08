"""
Улучшенный экстрактор PDF с использованием unstructured для лучшего извлечения таблиц и структурированного контента
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass
import hashlib

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.documents.elements import Table, CompositeElement, Title, NarrativeText
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    logging.warning("unstructured не установлен. Используется базовый экстрактор.")

from pydantic import BaseModel
from config import config

logger = logging.getLogger(__name__)

@dataclass
class ExtractedDocument:
    """Структура для извлеченного документа"""
    text: str
    metadata: Dict[str, Any]
    element_type: str  # 'text', 'table', 'title', 'header'
    confidence: float = 1.0

class EnhancedPDFExtractor:
    """Улучшенный экстрактор PDF с поддержкой структурированного контента"""
    
    def __init__(self):
        """Инициализация экстрактора"""
        if not UNSTRUCTURED_AVAILABLE:
            raise ImportError(
                "Для использования улучшенного экстрактора необходимо установить unstructured:\n"
                "pip install unstructured[pdf]"
            )
        
        logger.info("Инициализирован улучшенный PDF экстрактор")
    
    def extract_from_pdf(self, pdf_path: str) -> List[ExtractedDocument]:
        """
        Извлекает структурированный контент из PDF
        
        Args:
            pdf_path (str): Путь к PDF файлу
            
        Returns:
            List[ExtractedDocument]: Список извлеченных документов
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")
        
        logger.info(f"Извлекаю контент из PDF: {pdf_path.name}")
        
        try:
            # Используем unstructured для партиционирования PDF
            elements = partition_pdf(
                filename=str(pdf_path),
                # Извлекаем изображения для анализа таблиц
                extract_images_in_pdf=False,
                # Используем модель макета для определения таблиц
                infer_table_structure=True,
                # Стратегия чанкинга по заголовкам
                chunking_strategy="by_title",
                # Параметры чанкинга
                max_characters=2000,
                new_after_n_chars=1800,
                combine_text_under_n_chars=500,
            )
            
            documents = []
            
            for i, element in enumerate(elements):
                # Определяем тип элемента
                element_type = self._classify_element(element)
                
                # Извлекаем текст
                text = str(element).strip()
                if not text:
                    continue
                
                # Создаем метаданные
                metadata = {
                    'source_pdf': pdf_path.name,
                    'element_id': i,
                    'element_type': element_type,
                    'page_number': getattr(element, 'metadata', {}).get('page_number'),
                    'coordinates': getattr(element, 'metadata', {}).get('coordinates'),
                }
                
                # Дополнительные метаданные для таблиц
                if element_type == 'table':
                    metadata.update(self._extract_table_metadata(element, text))
                
                # Создаем хеш для уникальности
                text_hash = hashlib.md5(text.encode()).hexdigest()
                metadata['content_hash'] = text_hash
                
                # Оценка уверенности
                confidence = self._calculate_confidence(element, text)
                
                documents.append(ExtractedDocument(
                    text=text,
                    metadata=metadata,
                    element_type=element_type,
                    confidence=confidence
                ))
            
            logger.info(f"Извлечено {len(documents)} элементов из {pdf_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении из PDF {pdf_path}: {str(e)}")
            raise
    
    def _classify_element(self, element) -> str:
        """Классифицирует тип элемента"""
        element_type_str = str(type(element))
        
        if "Table" in element_type_str:
            return "table"
        elif "Title" in element_type_str:
            return "title"
        elif "Header" in element_type_str:
            return "header"
        elif "NarrativeText" in element_type_str:
            return "text"
        elif "CompositeElement" in element_type_str:
            return "text"
        else:
            return "text"
    
    def _extract_table_metadata(self, element, text: str) -> Dict[str, Any]:
        """Извлекает дополнительные метаданные для таблиц"""
        metadata = {}
        
        # Пытаемся найти заголовок таблицы в тексте
        lines = text.split('\n')
        if lines:
            potential_title = lines[0].strip()
            if len(potential_title) < 200:  # Вероятно заголовок
                metadata['table_title'] = potential_title
        
        # Подсчитываем количество строк и столбцов
        if hasattr(element, 'metadata') and element.metadata:
            table_data = element.metadata.get('text_as_html')
            if table_data:
                metadata['html_content'] = table_data
                # Подсчет строк и столбцов из HTML
                row_count = table_data.count('<tr')
                col_count = table_data.count('<td') + table_data.count('<th')
                metadata['estimated_rows'] = row_count
                metadata['estimated_cols'] = col_count // max(row_count, 1) if row_count > 0 else 0
        
        # Проверяем на наличие ключевых слов для дифференциальных характеристик
        differential_keywords = [
            'differential', 'characteristics', 'strain', 'phenotypic',
            'biochemical', 'morphological', 'growth', 'temperature'
        ]
        
        text_lower = text.lower()
        keyword_matches = sum(1 for keyword in differential_keywords if keyword in text_lower)
        
        if keyword_matches >= 2:
            metadata['likely_differential_table'] = True
            metadata['differential_score'] = keyword_matches / len(differential_keywords)
        
        return metadata
    
    def _calculate_confidence(self, element, text: str) -> float:
        """Рассчитывает уверенность в качестве извлечения"""
        confidence = 1.0
        
        # Снижаем уверенность для очень коротких текстов
        if len(text) < 50:
            confidence *= 0.7
        
        # Повышаем уверенность для таблиц
        if "Table" in str(type(element)):
            confidence *= 1.2
        
        # Повышаем уверенность для заголовков
        if "Title" in str(type(element)):
            confidence *= 1.1
        
        return min(confidence, 1.0)
    
    def extract_tables_only(self, pdf_path: str) -> List[ExtractedDocument]:
        """
        Извлекает только таблицы из PDF
        
        Args:
            pdf_path (str): Путь к PDF файлу
            
        Returns:
            List[ExtractedDocument]: Список таблиц
        """
        all_documents = self.extract_from_pdf(pdf_path)
        return [doc for doc in all_documents if doc.element_type == 'table']
    
    def get_extraction_stats(self, documents: List[ExtractedDocument]) -> Dict[str, Any]:
        """
        Возвращает статистику извлечения
        
        Args:
            documents (List[ExtractedDocument]): Список документов
            
        Returns:
            Dict[str, Any]: Статистика
        """
        if not documents:
            return {}
        
        stats = {
            'total_documents': len(documents),
            'by_type': {},
            'avg_confidence': sum(doc.confidence for doc in documents) / len(documents),
            'total_text_length': sum(len(doc.text) for doc in documents),
        }
        
        # Статистика по типам
        for doc in documents:
            doc_type = doc.element_type
            if doc_type not in stats['by_type']:
                stats['by_type'][doc_type] = 0
            stats['by_type'][doc_type] += 1
        
        # Статистика по таблицам
        tables = [doc for doc in documents if doc.element_type == 'table']
        if tables:
            stats['tables'] = {
                'count': len(tables),
                'with_titles': sum(1 for t in tables if t.metadata.get('table_title')),
                'differential_tables': sum(1 for t in tables if t.metadata.get('likely_differential_table')),
                'avg_differential_score': sum(
                    t.metadata.get('differential_score', 0) for t in tables
                ) / len(tables) if tables else 0
            }
        
        return stats 