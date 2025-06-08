"""
Продвинутый процессор документов с интеграцией нового PDF экстрактора
"""

from pathlib import Path
from typing import List, Dict, Any
from loguru import logger
from tqdm import tqdm

from .document_processor import DocumentChunk
from ..pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor, ExtractedElement
from ..pdf_extractor.text_quality_improver import text_quality_improver


class AdvancedDocumentProcessor:
    """Продвинутый процессор с высококачественным извлечением PDF"""
    
    def __init__(self):
        """Инициализация процессора"""
        self.pdf_extractor = AdvancedPDFExtractor()
        self.chunk_size = 1000  # Размер чанка
        self.chunk_overlap = 200  # Перекрытие чанков
        
        logger.info("Инициализирован продвинутый процессор документов")
    
    def process_pdf_directory(self, pdf_directory: Path) -> List[DocumentChunk]:
        """
        Обрабатывает директорию с PDF файлами
        
        Args:
            pdf_directory (Path): Путь к директории с PDF
            
        Returns:
            List[DocumentChunk]: Список обработанных чанков
        """
        pdf_files = list(pdf_directory.glob("*.pdf"))
        logger.info(f"Найдено {len(pdf_files)} PDF файлов для обработки")
        
        all_chunks = []
        
        for pdf_file in tqdm(pdf_files, desc="Обработка PDF файлов"):
            try:
                # Извлекаем документ с помощью продвинутого экстрактора
                document = self.pdf_extractor.extract_document(pdf_file)
                
                # Конвертируем в чанки
                chunks = self._convert_document_to_chunks(document)
                all_chunks.extend(chunks)
                
                logger.info(f"✅ {pdf_file.name}: {len(chunks)} чанков")
                
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке {pdf_file.name}: {e}")
                continue
        
        logger.info(f"🎉 Всего обработано: {len(all_chunks)} чанков")
        return all_chunks
    
    def _convert_document_to_chunks(self, document) -> List[DocumentChunk]:
        """Конвертирует извлечённый документ в чанки"""
        
        chunks = []
        
        # Обрабатываем текстовые элементы
        text_elements = [e for e in document.elements if e.element_type == 'text']
        text_chunks = self._create_text_chunks(text_elements, document.file_path)
        chunks.extend(text_chunks)
        
        # Обрабатываем табличные элементы
        table_elements = [e for e in document.elements if e.element_type == 'table']
        table_chunks = self._create_table_chunks(table_elements, document.file_path)
        chunks.extend(table_chunks)
        
        return chunks
    
    def _create_text_chunks(self, text_elements: List[ExtractedElement], source_file: str) -> List[DocumentChunk]:
        """Создаёт текстовые чанки"""
        
        chunks = []
        
        # Объединяем весь текст
        full_text = "\n\n".join([element.content for element in text_elements])
        
        # Разбиваем на чанки с перекрытием
        text_chunks = self._split_text_with_overlap(full_text)
        
        for i, chunk_text in enumerate(text_chunks):
            # Дополнительно улучшаем качество
            improved_text = text_quality_improver.improve_text_quality(chunk_text)
            
            chunk = DocumentChunk(
                chunk_id=f"{Path(source_file).stem}_text_{i}",
                text=improved_text,
                chunk_type="text",
                metadata={
                    "source_pdf": Path(source_file).name,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "extraction_method": "advanced_pymupdf4llm",
                    "quality_improved": True
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_table_chunks(self, table_elements: List[ExtractedElement], source_file: str) -> List[DocumentChunk]:
        """Создаёт табличные чанки"""
        
        chunks = []
        
        for i, table_element in enumerate(table_elements):
            # Улучшаем качество табличного текста
            improved_table_text = text_quality_improver.improve_text_quality(table_element.content)
            
            # Добавляем контекст для лучшего поиска
            enhanced_text = self._enhance_table_context(improved_table_text, table_element)
            
            chunk = DocumentChunk(
                chunk_id=f"{Path(source_file).stem}_table_{i}",
                text=enhanced_text,
                chunk_type="table",
                metadata={
                    "source_pdf": Path(source_file).name,
                    "page_number": table_element.page_number,
                    "table_index": i,
                    "extraction_method": table_element.metadata.get('extraction_method', 'unknown'),
                    "table_shape": table_element.metadata.get('table_shape', ''),
                    "relevance_score": table_element.confidence,
                    "contains_strain_data": table_element.metadata.get('contains_strain_data', False),
                    "quality_improved": True
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _enhance_table_context(self, table_text: str, table_element: ExtractedElement) -> str:
        """Добавляет контекст к табличным данным для лучшего поиска"""
        
        enhanced_text = table_text
        
        # Добавляем ключевые слова для лучшего поиска
        if 'YC5194' in table_text:
            enhanced_text = f"ШТАММ YC5194 ХАРАКТЕРИСТИКИ:\n{enhanced_text}"
        
        if any(word in table_text.lower() for word in ['temperature', 'температура']):
            enhanced_text = f"ТЕМПЕРАТУРНЫЕ ХАРАКТЕРИСТИКИ:\n{enhanced_text}"
        
        if any(word in table_text.lower() for word in ['ph', 'кислотность']):
            enhanced_text = f"pH ХАРАКТЕРИСТИКИ:\n{enhanced_text}"
        
        if any(word in table_text.lower() for word in ['growth', 'рост']):
            enhanced_text = f"УСЛОВИЯ РОСТА:\n{enhanced_text}"
        
        if any(word in table_text.lower() for word in ['morphology', 'морфология']):
            enhanced_text = f"МОРФОЛОГИЧЕСКИЕ ХАРАКТЕРИСТИКИ:\n{enhanced_text}"
        
        # Добавляем метаинформацию
        meta_info = f"\nИсточник: страница {table_element.page_number}, "
        meta_info += f"метод извлечения: {table_element.metadata.get('extraction_method', 'unknown')}, "
        meta_info += f"релевантность: {table_element.confidence:.2f}"
        
        enhanced_text += meta_info
        
        return enhanced_text
    
    def _split_text_with_overlap(self, text: str) -> List[str]:
        """Разбивает текст на чанки с перекрытием"""
        
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Ищем ближайший разделитель предложений
            if end < len(text):
                for delimiter in ['. ', '\n\n', '\n', '; ']:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + len(delimiter)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Следующий чанк начинается с перекрытием
            start = end - self.chunk_overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def get_processing_stats(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Возвращает статистику обработки"""
        
        text_chunks = [c for c in chunks if c.chunk_type == 'text']
        table_chunks = [c for c in chunks if c.chunk_type == 'table']
        
        # Подсчитываем упоминания важных штаммов
        yc5194_mentions = sum(1 for c in chunks if 'YC5194' in c.text)
        strain_mentions = sum(1 for c in chunks if 'strain' in c.text.lower())
        
        # Анализируем качество
        total_chars = sum(len(c.text) for c in chunks)
        avg_chunk_size = total_chars / len(chunks) if chunks else 0
        
        return {
            'total_chunks': len(chunks),
            'text_chunks': len(text_chunks),
            'table_chunks': len(table_chunks),
            'yc5194_mentions': yc5194_mentions,
            'strain_mentions': strain_mentions,
            'total_characters': total_chars,
            'avg_chunk_size': avg_chunk_size,
            'quality_improved': all(c.metadata.get('quality_improved', False) for c in chunks)
        } 