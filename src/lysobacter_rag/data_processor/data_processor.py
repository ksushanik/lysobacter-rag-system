"""
Модуль для подготовки и чанкинга данных для RAG-системы
Преобразует извлеченные данные в формат, подходящий для индексации
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass
from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

from config import config
from ..pdf_extractor import ExtractedDocument, ExtractedTable


@dataclass
class DocumentChunk:
    """Класс для хранения чанка документа"""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str
    chunk_type: str  # 'text' или 'table'


class DataProcessor:
    """Класс для обработки и чанкинга извлеченных данных"""
    
    def __init__(self):
        """Инициализация процессора данных"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
        )
        
    def process_documents(self, extracted_docs: List[ExtractedDocument]) -> List[DocumentChunk]:
        """
        Обрабатывает список извлеченных документов и создает чанки
        
        Args:
            extracted_docs (List[ExtractedDocument]): Извлеченные документы
            
        Returns:
            List[DocumentChunk]: Список чанков для индексации
        """
        all_chunks = []
        
        logger.info(f"Начинаю обработку {len(extracted_docs)} документов")
        
        for doc in extracted_docs:
            # Обрабатываем таблицы
            table_chunks = self._process_tables(doc.tables)
            all_chunks.extend(table_chunks)
            
            # Обрабатываем текстовый контент
            text_chunks = self._process_text_content(doc)
            all_chunks.extend(text_chunks)
            
            logger.info(f"Обработан документ {doc.source_pdf}: {len(table_chunks)} таблиц, {len(text_chunks)} текстовых чанков")
        
        logger.info(f"Всего создано {len(all_chunks)} чанков")
        return all_chunks
    
    def _process_tables(self, tables: List[ExtractedTable]) -> List[DocumentChunk]:
        """
        Обрабатывает таблицы и создает для них чанки
        
        Args:
            tables (List[ExtractedTable]): Список извлеченных таблиц
            
        Returns:
            List[DocumentChunk]: Чанки таблиц
        """
        table_chunks = []
        
        for table in tables:
            # Формируем текстовое представление таблицы
            table_text = self._format_table_as_text(table)
            
            # Создаем метаданные для таблицы
            metadata = {
                'source_pdf': table.source_pdf,
                'page_number': table.page_number,
                'chunk_type': 'table',
                'original_table_title': table.title,
                'table_description': table.description,
                'table_legend': table.legend,
                'confidence_score': table.confidence_score,
                'table_shape': f"{table.table_data.shape[0]}x{table.table_data.shape[1]}"
            }
            
            # Создаем уникальный ID для чанка
            chunk_id = f"{table.source_pdf}_page_{table.page_number}_table_{hash(table.title) % 10000}"
            
            chunk = DocumentChunk(
                text=table_text,
                metadata=metadata,
                chunk_id=chunk_id,
                chunk_type='table'
            )
            
            table_chunks.append(chunk)
        
        return table_chunks
    
    def _format_table_as_text(self, table: ExtractedTable) -> str:
        """
        Форматирует таблицу как текст для индексации
        
        Args:
            table (ExtractedTable): Таблица для форматирования
            
        Returns:
            str: Текстовое представление таблицы
        """
        # Начинаем с маркера и заголовка
        formatted_text = f"[TABLE_START]\n"
        formatted_text += f"Заголовок таблицы: {table.title}\n\n"
        
        # Добавляем описание, если есть
        if table.description.strip():
            formatted_text += f"Описание: {table.description}\n\n"
        
        # Добавляем саму таблицу в markdown формате
        formatted_text += "Данные таблицы:\n"
        try:
            # Конвертируем DataFrame в markdown
            table_md = table.table_data.to_markdown(index=False)
            formatted_text += table_md + "\n\n"
        except Exception as e:
            # Если не удается конвертировать в markdown, используем простой формат
            logger.warning(f"Не удалось конвертировать таблицу в markdown: {e}")
            formatted_text += str(table.table_data) + "\n\n"
        
        # Добавляем легенду, если есть
        if table.legend.strip():
            formatted_text += f"Примечания и легенда: {table.legend}\n\n"
        
        formatted_text += "[TABLE_END]"
        
        return formatted_text
    
    def _process_text_content(self, doc: ExtractedDocument) -> List[DocumentChunk]:
        """
        Обрабатывает текстовый контент документа и создает чанки
        
        Args:
            doc (ExtractedDocument): Документ для обработки
            
        Returns:
            List[DocumentChunk]: Текстовые чанки
        """
        # Очищаем текст от табличного контента, который уже обработан отдельно
        cleaned_text = self._remove_table_content(doc.text_content)
        
        # Разбиваем текст на чанки
        text_chunks = self.text_splitter.split_text(cleaned_text)
        
        document_chunks = []
        
        for i, chunk_text in enumerate(text_chunks):
            # Пропускаем слишком короткие чанки
            if len(chunk_text.strip()) < 50:
                continue
            
            # Определяем номер страницы для чанка (приблизительно)
            page_number = self._estimate_page_number(chunk_text, doc.text_content, doc.total_pages)
            
            # Создаем метаданные
            metadata = {
                'source_pdf': doc.source_pdf,
                'page_number': page_number,
                'chunk_type': 'text',
                'chunk_index': i,
                'total_chunks': len(text_chunks)
            }
            
            # Создаем уникальный ID
            chunk_id = f"{doc.source_pdf}_text_chunk_{i}"
            
            chunk = DocumentChunk(
                text=chunk_text.strip(),
                metadata=metadata,
                chunk_id=chunk_id,
                chunk_type='text'
            )
            
            document_chunks.append(chunk)
        
        return document_chunks
    
    def _remove_table_content(self, text: str) -> str:
        """
        Удаляет из текста контент, который уже обработан как таблицы
        
        Args:
            text (str): Исходный текст
            
        Returns:
            str: Очищенный текст
        """
        # Удаляем строки, которые выглядят как табличные данные
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_clean = line.strip()
            
            # Пропускаем очень короткие строки
            if len(line_clean) < 3:
                continue
            
            # Пропускаем строки, которые выглядят как табличные заголовки
            if self._is_likely_table_content(line_clean):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _is_likely_table_content(self, line: str) -> bool:
        """
        Определяет, является ли строка частью таблицы
        
        Args:
            line (str): Строка для проверки
            
        Returns:
            bool: True если строка похожа на табличный контент
        """
        # Проверяем на наличие множественных разделителей (табуляция, пробелы)
        if len(re.findall(r'\t+|\s{3,}', line)) > 2:
            return True
        
        # Проверяем на наличие характерных символов таблиц
        table_chars = ['|', '+', '-', '=']
        if sum(line.count(char) for char in table_chars) > len(line) * 0.3:
            return True
        
        return False
    
    def _estimate_page_number(self, chunk_text: str, full_text: str, total_pages: int) -> int:
        """
        Приблизительно определяет номер страницы для чанка
        
        Args:
            chunk_text (str): Текст чанка
            full_text (str): Полный текст документа
            total_pages (int): Общее количество страниц
            
        Returns:
            int: Приблизительный номер страницы
        """
        try:
            # Находим позицию чанка в полном тексте
            chunk_position = full_text.find(chunk_text[:100])  # Ищем по первым 100 символам
            
            if chunk_position == -1:
                return 1  # Если не найден, возвращаем первую страницу
            
            # Вычисляем приблизительную страницу на основе позиции
            text_progress = chunk_position / len(full_text)
            estimated_page = max(1, int(text_progress * total_pages))
            
            return min(estimated_page, total_pages)
        
        except Exception:
            return 1
    
    def get_statistics(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Возвращает статистику по созданным чанкам
        
        Args:
            chunks (List[DocumentChunk]): Список чанков
            
        Returns:
            Dict[str, Any]: Статистика
        """
        stats = {
            'total_chunks': len(chunks),
            'text_chunks': len([c for c in chunks if c.chunk_type == 'text']),
            'table_chunks': len([c for c in chunks if c.chunk_type == 'table']),
            'avg_chunk_length': sum(len(c.text) for c in chunks) / len(chunks) if chunks else 0,
            'sources': list(set(c.metadata['source_pdf'] for c in chunks))
        }
        
        return stats


if __name__ == "__main__":
    # Пример использования
    from ..pdf_extractor import PDFExtractor
    
    extractor = PDFExtractor()
    docs = extractor.extract_all_pdfs(str(config.DATA_DIR))
    
    processor = DataProcessor()
    chunks = processor.process_documents(docs)
    
    stats = processor.get_statistics(chunks)
    print("Статистика обработки:")
    for key, value in stats.items():
        print(f"{key}: {value}") 