"""
Современный высококачественный PDF экстрактор
Использует лучшие библиотеки для максимального качества извлечения текста и таблиц
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import pandas as pd
from tqdm import tqdm

# Современные PDF библиотеки
import pymupdf4llm
import pdfplumber
import tabula

from .text_quality_improver import text_quality_improver
from .scientific_chunker import ScientificTextChunker


@dataclass
class ExtractedElement:
    """Извлечённый элемент документа"""
    element_type: str  # 'text', 'table', 'header', 'list'
    content: str
    page_number: int
    confidence: float
    metadata: Dict[str, Any]
    raw_data: Any = None


@dataclass
class AdvancedExtractedDocument:
    """Документ, извлечённый с помощью продвинутого экстрактора"""
    file_path: str
    title: str
    total_pages: int
    elements: List[ExtractedElement]
    metadata: Dict[str, Any]
    extraction_stats: Dict[str, Any]


class AdvancedPDFExtractor:
    """Продвинутый PDF экстрактор с поддержкой таблиц и высоким качеством"""
    
    def __init__(self, use_smart_chunking: bool = True):
        """Инициализация экстрактора"""
        self.quality_improver = text_quality_improver
        self.use_smart_chunking = use_smart_chunking
        
        # Инициализируем умный чанкер
        if use_smart_chunking:
            self.chunker = ScientificTextChunker(target_chunk_size=350, overlap=50)
            logger.info("✅ Активирован умный чанкинг (размер: 350, перекрытие: 50)")
        else:
            self.chunker = None
            logger.info("⚠️ Умный чанкинг отключён")
        
        # Настройки для табличных данных
        self.table_keywords = [
            'table', 'таблица', 'characteristics', 'характеристики',
            'strain', 'штамм', 'species', 'вид', 'temperature', 'температура',
            'growth', 'рост', 'pH', 'морфология', 'biochemical', 'биохимический'
        ]
        
        logger.info("Инициализирован продвинутый PDF экстрактор")
    
    def extract_document(self, pdf_path: Path) -> AdvancedExtractedDocument:
        """
        Извлекает документ с использованием множественных методов
        
        Args:
            pdf_path (Path): Путь к PDF файлу
            
        Returns:
            AdvancedExtractedDocument: Извлечённый документ
        """
        logger.info(f"🚀 Начинаю продвинутое извлечение: {pdf_path.name}")
        
        elements = []
        extraction_stats = {
            'total_pages': 0,
            'text_elements': 0,
            'table_elements': 0,
            'quality_score': 0,
            'methods_used': []
        }
        
        try:
            # Метод 1: pymupdf4llm для высококачественного текста
            logger.info("📝 Извлекаю текст с помощью pymupdf4llm...")
            text_elements = self._extract_with_pymupdf4llm(pdf_path)
            elements.extend(text_elements)
            extraction_stats['text_elements'] = len(text_elements)
            extraction_stats['methods_used'].append('pymupdf4llm')
            
            # Метод 2: pdfplumber для таблиц
            logger.info("📊 Извлекаю таблицы с помощью pdfplumber...")
            table_elements = self._extract_tables_pdfplumber(pdf_path)
            elements.extend(table_elements)
            extraction_stats['table_elements'] = len(table_elements)
            extraction_stats['methods_used'].append('pdfplumber')
            
            # Метод 3: tabula для сложных таблиц
            logger.info("📋 Дополнительное извлечение таблиц с tabula...")
            tabula_elements = self._extract_tables_tabula(pdf_path)
            elements.extend(tabula_elements)
            extraction_stats['methods_used'].append('tabula')
            
            # Получаем общее количество страниц
            with pdfplumber.open(pdf_path) as pdf:
                extraction_stats['total_pages'] = len(pdf.pages)
            
            # Оценка качества
            total_text_length = sum(len(e.content) for e in elements if e.element_type == 'text')
            quality_score = min(100, max(0, (total_text_length / 1000) * 10))
            extraction_stats['quality_score'] = quality_score
            
            logger.info(f"✅ Извлечение завершено: {len(elements)} элементов")
            logger.info(f"   📝 Текст: {extraction_stats['text_elements']}")
            logger.info(f"   📊 Таблицы: {extraction_stats['table_elements']}")
            logger.info(f"   📈 Качество: {quality_score:.1f}%")
            
            return AdvancedExtractedDocument(
                file_path=str(pdf_path),
                title=pdf_path.stem,
                total_pages=extraction_stats['total_pages'],
                elements=elements,
                metadata={
                    'extraction_timestamp': pd.Timestamp.now().isoformat(),
                    'file_size_mb': pdf_path.stat().st_size / (1024 * 1024),
                    'extractor_version': '3.0_smart_chunking'
                },
                extraction_stats=extraction_stats
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка при извлечении {pdf_path}: {e}")
            return self._create_fallback_document(pdf_path, str(e))
    
    def get_smart_chunks(self, document: AdvancedExtractedDocument) -> List[Dict]:
        """
        Получает умные чанки из извлечённого документа
        
        Args:
            document: Извлечённый документ
            
        Returns:
            Список умных чанков для индексации
        """
        if not self.use_smart_chunking or not self.chunker:
            logger.warning("⚠️ Умный чанкинг отключён, возвращаю элементы как есть")
            return self._convert_elements_to_chunks(document.elements)
        
        logger.info(f"🧬 Применяю умный чанкинг к {len(document.elements)} элементам")
        
        # Конвертируем элементы в формат для чанкера
        elements_for_chunking = []
        for element in document.elements:
            elements_for_chunking.append({
                'content': element.content,
                'element_type': element.element_type,
                'page_number': element.page_number,
                'confidence': element.confidence,
                'metadata': element.metadata
            })
        
        # Применяем умный чанкинг
        smart_chunks = self.chunker.chunk_extracted_elements(elements_for_chunking)
        
        # Добавляем информацию о документе в метаданные
        for chunk in smart_chunks:
            chunk['metadata']['source_pdf'] = document.title + '.pdf'
            chunk['metadata']['extractor_version'] = '3.0_smart_chunking'
            chunk['metadata']['total_pages'] = document.total_pages
        
        logger.info(f"✅ Создано {len(smart_chunks)} умных чанков")
        
        return smart_chunks
    
    def _convert_elements_to_chunks(self, elements: List[ExtractedElement]) -> List[Dict]:
        """Конвертирует элементы в простые чанки (без умного чанкинга)"""
        chunks = []
        
        for element in elements:
            chunk = {
                'content': element.content,
                'metadata': element.metadata.copy(),
                'page_number': element.page_number,
                'confidence': element.confidence
            }
            
            chunk['metadata']['chunk_type'] = element.element_type
            chunk['metadata']['chunking_method'] = 'simple'
            
            chunks.append(chunk)
        
        return chunks
    
    def _extract_with_pymupdf4llm(self, pdf_path: Path) -> List[ExtractedElement]:
        """Извлекает текст с помощью pymupdf4llm (высокое качество)"""
        
        elements = []
        
        try:
            # Используем pymupdf4llm для качественного извлечения
            markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
            
            if not markdown_text or len(markdown_text.strip()) < 50:
                logger.warning("pymupdf4llm вернул мало текста, используем базовый метод")
                return self._extract_with_basic_pymupdf(pdf_path)
            
            # Разбиваем на страницы (приблизительно)
            pages = self._split_markdown_by_pages(markdown_text)
            
            for page_num, page_content in enumerate(pages, 1):
                if len(page_content.strip()) < 20:
                    continue
                
                # Улучшаем качество текста
                improved_text = self.quality_improver.improve_text_quality(page_content)
                
                # Определяем тип контента
                element_type = self._classify_content(improved_text)
                
                element = ExtractedElement(
                    element_type=element_type,
                    content=improved_text,
                    page_number=page_num,
                    confidence=0.9,  # Высокая уверенность для pymupdf4llm
                    metadata={
                        'extraction_method': 'pymupdf4llm',
                        'original_length': len(page_content),
                        'improved_length': len(improved_text),
                        'content_type': element_type
                    }
                )
                
                elements.append(element)
            
            logger.info(f"✅ pymupdf4llm извлёк {len(elements)} текстовых элементов")
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка pymupdf4llm: {e}, переключаюсь на базовый метод")
            return self._extract_with_basic_pymupdf(pdf_path)
        
        return elements
    
    def _extract_tables_pdfplumber(self, pdf_path: Path) -> List[ExtractedElement]:
        """Извлекает таблицы с помощью pdfplumber"""
        
        table_elements = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Извлекаем таблицы
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Конвертируем в структурированный текст
                        table_text = self._table_to_structured_text(
                            table, page_num, table_idx
                        )
                        
                        if len(table_text.strip()) < 20:
                            continue
                        
                        # Улучшаем качество
                        improved_table_text = self.quality_improver.improve_text_quality(table_text)
                        
                        # Проверяем релевантность (содержит ли научные термины)
                        relevance = self._assess_table_relevance(improved_table_text)
                        
                        element = ExtractedElement(
                            element_type='table',
                            content=improved_table_text,
                            page_number=page_num,
                            confidence=relevance,
                            metadata={
                                'extraction_method': 'pdfplumber',
                                'table_index': table_idx,
                                'table_shape': f"{len(table)}x{len(table[0]) if table else 0}",
                                'relevance_score': relevance,
                                'contains_strain_data': 'strain' in improved_table_text.lower()
                            },
                            raw_data=table
                        )
                        
                        table_elements.append(element)
            
            logger.info(f"✅ pdfplumber извлёк {len(table_elements)} таблиц")
            
        except Exception as e:
            logger.error(f"❌ Ошибка pdfplumber: {e}")
        
        return table_elements
    
    def _extract_tables_tabula(self, pdf_path: Path) -> List[ExtractedElement]:
        """Извлекает таблицы с помощью tabula (для сложных случаев)"""
        
        table_elements = []
        
        try:
            # Пытаемся извлечь таблицы со всех страниц
            dfs = tabula.read_pdf(
                str(pdf_path), 
                pages='all', 
                multiple_tables=True,
                pandas_options={'header': 0}
            )
            
            for table_idx, df in enumerate(dfs):
                if df.empty or len(df) < 2:
                    continue
                
                # Конвертируем DataFrame в текст
                table_text = self._dataframe_to_structured_text(df, table_idx)
                
                if len(table_text.strip()) < 20:
                    continue
                
                # Улучшаем качество
                improved_table_text = self.quality_improver.improve_text_quality(table_text)
                
                # Оценка релевантности
                relevance = self._assess_table_relevance(improved_table_text)
                
                if relevance < 0.3:  # Пропускаем нерелевантные таблицы
                    continue
                
                element = ExtractedElement(
                    element_type='table',
                    content=improved_table_text,
                    page_number=1,  # tabula не даёт точную страницу
                    confidence=relevance,
                    metadata={
                        'extraction_method': 'tabula',
                        'table_index': table_idx,
                        'table_shape': f"{len(df)}x{len(df.columns)}",
                        'relevance_score': relevance,
                        'column_count': len(df.columns)
                    },
                    raw_data=df
                )
                
                table_elements.append(element)
            
            logger.info(f"✅ tabula извлёк {len(table_elements)} дополнительных таблиц")
            
        except Exception as e:
            logger.warning(f"⚠️ tabula недоступен или ошибка: {e}")
        
        return table_elements
    
    def _table_to_structured_text(self, table: List[List], page_num: int, table_idx: int) -> str:
        """Конвертирует таблицу в структурированный текст"""
        
        if not table or len(table) < 2:
            return ""
        
        # Извлекаем заголовки
        headers = [str(cell).strip() if cell else "" for cell in table[0]]
        headers = [h for h in headers if h]  # Удаляем пустые
        
        if not headers:
            return ""
        
        # Формируем структурированный текст
        structured_text = f"ТАБЛИЦА {table_idx + 1} (Страница {page_num}):\n"
        structured_text += f"Столбцы: {' | '.join(headers)}\n\n"
        
        # Обрабатываем строки данных
        for row_idx, row in enumerate(table[1:], 1):
            if not any(cell for cell in row):  # Пропускаем пустые строки
                continue
            
            row_data = [str(cell).strip() if cell else "-" for cell in row]
            
            # Создаём читаемую строку
            row_text = ""
            for i, (header, value) in enumerate(zip(headers, row_data[:len(headers)])):
                if value and value != "-":
                    row_text += f"{header}: {value}; "
            
            if row_text:
                structured_text += f"Строка {row_idx}: {row_text.rstrip('; ')}\n"
        
        return structured_text
    
    def _dataframe_to_structured_text(self, df: pd.DataFrame, table_idx: int) -> str:
        """Конвертирует DataFrame в структурированный текст"""
        
        structured_text = f"ТАБЛИЦА {table_idx + 1} (tabula):\n"
        structured_text += f"Столбцы: {' | '.join(df.columns)}\n\n"
        
        for idx, row in df.iterrows():
            row_text = ""
            for col in df.columns:
                value = str(row[col]).strip()
                if value and value not in ['nan', 'NaN', '']:
                    row_text += f"{col}: {value}; "
            
            if row_text:
                structured_text += f"Строка {idx + 1}: {row_text.rstrip('; ')}\n"
        
        return structured_text
    
    def _assess_table_relevance(self, table_text: str) -> float:
        """Оценивает релевантность таблицы для научного контента"""
        
        table_lower = table_text.lower()
        relevance_score = 0.0
        
        # Ключевые слова для микробиологии
        microbiology_keywords = [
            'strain', 'штамм', 'lysobacter', 'species', 'temperature', 'температура',
            'growth', 'рост', 'ph', 'характеристики', 'characteristics',
            'biochemical', 'биохимический', 'morphology', 'морфология',
            'gram', 'catalase', 'oxidase', 'glucose', 'размер', 'size'
        ]
        
        # Подсчитываем совпадения
        for keyword in microbiology_keywords:
            if keyword in table_lower:
                relevance_score += 0.1
        
        # Бонус за штаммы
        strain_patterns = [r'[A-Z]{1,3}[-\s]?\d{1,6}[A-Z]?', r'YC\d+', r'strain\s+\w+']
        for pattern in strain_patterns:
            if re.search(pattern, table_text, re.IGNORECASE):
                relevance_score += 0.2
        
        # Бонус за числовые данные (температуры, pH и т.д.)
        numeric_patterns = [r'\d+[-–]\d+°?[CcС]', r'pH\s*\d', r'\d+\.\d+']
        for pattern in numeric_patterns:
            if re.search(pattern, table_text):
                relevance_score += 0.1
        
        return min(1.0, relevance_score)
    
    def _classify_content(self, text: str) -> str:
        """Классифицирует тип контента"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['table', 'таблица', '|']):
            return 'table'
        elif any(word in text_lower for word in ['abstract', 'introduction', 'conclusion']):
            return 'section'
        elif len(text.split()) < 10:
            return 'header'
        else:
            return 'text'
    
    def _split_markdown_by_pages(self, markdown_text: str) -> List[str]:
        """Разбивает markdown на примерные страницы"""
        
        # Простое разбиение по размеру (можно улучшить)
        avg_page_size = 2000  # символов на страницу
        pages = []
        
        current_page = ""
        for line in markdown_text.split('\n'):
            current_page += line + '\n'
            
            if len(current_page) > avg_page_size:
                pages.append(current_page)
                current_page = ""
        
        if current_page.strip():
            pages.append(current_page)
        
        return pages
    
    def _extract_with_basic_pymupdf(self, pdf_path: Path) -> List[ExtractedElement]:
        """Fallback метод с базовым PyMuPDF"""
        
        import fitz
        
        elements = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text and len(text.strip()) > 20:
                    improved_text = self.quality_improver.improve_text_quality(text)
                    
                    element = ExtractedElement(
                        element_type='text',
                        content=improved_text,
                        page_number=page_num + 1,
                        confidence=0.7,  # Средняя уверенность
                        metadata={
                            'extraction_method': 'basic_pymupdf',
                            'fallback': True
                        }
                    )
                    
                    elements.append(element)
            
            doc.close()
            
        except Exception as e:
            logger.error(f"❌ Даже fallback метод не сработал: {e}")
        
        return elements
    
    def _create_fallback_document(self, pdf_path: Path, error_msg: str) -> AdvancedExtractedDocument:
        """Создаёт минимальный документ при ошибке"""
        
        return AdvancedExtractedDocument(
            file_path=str(pdf_path),
            title=pdf_path.stem,
            total_pages=0,
            elements=[],
            metadata={
                'error': error_msg,
                'extraction_failed': True
            },
            extraction_stats={
                'total_pages': 0,
                'text_elements': 0,
                'table_elements': 0,
                'quality_score': 0,
                'methods_used': []
            }
        ) 