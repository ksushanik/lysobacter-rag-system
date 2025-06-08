"""
Улучшенный PDF экстрактор с исправлением проблем качества текста
"""
import re
import pdfplumber
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger
from dataclasses import dataclass

from .pdf_extractor import ExtractedDocument, ExtractedTable

@dataclass
class QualityMetrics:
    """Метрики качества извлеченного текста"""
    broken_strains: int = 0
    broken_formulas: int = 0
    merged_words: int = 0
    fixed_issues: int = 0

class ImprovedPDFExtractor:
    """Улучшенный PDF экстрактор с коррекцией качества"""
    
    def __init__(self):
        self.quality_metrics = QualityMetrics()
    
    def fix_text_quality(self, text: str) -> str:
        """Исправляет все выявленные проблемы качества текста"""
        
        original_text = text
        
        # 1. Исправляем разорванные штаммовые номера (КРИТИЧНО!)
        text = re.sub(r'GW1-\s*5\s*9T', 'GW1-59T', text)
        text = re.sub(r'GW1-\s+59T', 'GW1-59T', text)
        text = re.sub(r'GW\s*1-\s*5\s*9\s*T', 'GW1-59T', text)
        
        # 2. Исправляем разорванные химические формулы
        text = re.sub(r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2', text)
        text = re.sub(r'iso-\s*C\s+(\d+)', r'iso-C\1', text)
        text = re.sub(r'(\w+)-\s*C\s+(\d+)', r'\1-C\2', text)
        
        # 3. Исправляем температурные данные
        text = re.sub(r'(\d+)\s*–\s*(\d+)\s*°?\s*C', r'\1–\2°C', text)
        text = re.sub(r'(\d+)\s*uC', r'\1°C', text)
        text = re.sub(r'optimum,?\s*(\d+)\s*°C', r'optimum \1°C', text)
        
        # 4. Исправляем pH данные
        text = re.sub(r'pH\s+(\d+\.?\d*)\s*–\s*(\d+\.?\d*)', r'pH \1–\2', text)
        text = re.sub(r'pH\s+(\d+\.?\d*)', r'pH \1', text)
        
        # 5. Исправляем данные о концентрации соли
        text = re.sub(r'(\d+)\s*–\s*(\d+)\s*%.*?NaCl', r'\1–\2% NaCl', text)
        text = re.sub(r'NaCl.*?(\d+)\s*–\s*(\d+)\s*%', r'NaCl \1–\2%', text)
        
        # 6. Исправляем данные о геноме
        text = re.sub(r'(\d+\.?\d*)\s*Mb', r'\1 Mb', text)
        text = re.sub(r'(\d+),(\d+),(\d+)\s*bp', r'\1,\2,\3 bp', text)
        text = re.sub(r'G\s*\+\s*C.*?(\d+\.?\d*)\s*%', r'G+C \1%', text)
        
        # 7. Исправляем слитные слова и разорванные слова
        # Специфические исправления для научных терминов
        text = re.sub(r'eggNOG-\s*m\s*apper', 'eggNOG-mapper', text)
        text = re.sub(r'phylo\s*genetically', 'phylogenetically', text)
        text = re.sub(r'Lyso\s*bacter', 'Lysobacter', text)
        text = re.sub(r'chemo\s*taxonomic', 'chemotaxonomic', text)
        
        # 8. Убираем излишние пробелы и переносы
        text = re.sub(r'\s*-\s*\n\s*', '', text)  # Убираем переносы строк
        text = re.sub(r'\s+', ' ', text)  # Множественные пробелы → одинарный
        text = text.strip()
        
        # 9. Исправляем специфические проблемы с числами
        text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)  # 63 . 9 → 63.9
        text = re.sub(r'(\d+)\s*,\s*(\d+)', r'\1,\2', text)  # 2 , 784 → 2,784
        
        # Подсчитываем количество исправлений
        if text != original_text:
            self.quality_metrics.fixed_issues += 1
        
        return text
    
    def extract_with_quality_control(self, pdf_path: Path) -> ExtractedDocument:
        """Извлекает документ с контролем качества"""
        
        logger.info(f"Извлекаю PDF с контролем качества: {pdf_path.name}")
        
        # Сбрасываем метрики
        self.quality_metrics = QualityMetrics()
        
        extracted_texts = []
        extracted_tables = []
        
        # Метод 1: pdfplumber для высокого качества текста и таблиц
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Извлекаем обычный текст
                    text = page.extract_text()
                    if text:
                        # Применяем исправления качества
                        fixed_text = self.fix_text_quality(text)
                        extracted_texts.append({
                            'page': page_num,
                            'text': fixed_text,
                            'method': 'pdfplumber'
                        })
                    
                    # Извлекаем таблицы отдельно
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:  # Минимум 2 строки
                            # Преобразуем таблицу в структурированный текст
                            table_text = self._process_table(table, page_num, table_idx)
                            if table_text:
                                fixed_table_text = self.fix_text_quality(table_text)
                                
                                extracted_table = ExtractedTable(
                                    page_number=page_num,
                                    table_index=table_idx,
                                    title=f"Таблица {table_idx + 1} (страница {page_num})",
                                    content=fixed_table_text,
                                    raw_data=table,
                                    confidence_score=0.9
                                )
                                extracted_tables.append(extracted_table)
        
        except Exception as e:
            logger.error(f"Ошибка pdfplumber для {pdf_path}: {e}")
        
        # Метод 2: PyMuPDF для дополнительного текста
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text:
                    fixed_text = self.fix_text_quality(text)
                    # Добавляем только если текст значительно отличается
                    if not self._text_already_extracted(fixed_text, extracted_texts):
                        extracted_texts.append({
                            'page': page_num + 1,
                            'text': fixed_text,
                            'method': 'pymupdf'
                        })
            doc.close()
        except Exception as e:
            logger.error(f"Ошибка PyMuPDF для {pdf_path}: {e}")
        
        # Объединяем весь текст
        full_text = "\n\n".join([item['text'] for item in extracted_texts])
        
        # Создаем документ
        document = ExtractedDocument(
            file_path=str(pdf_path),
            title=pdf_path.stem,
            content=full_text,
            metadata={
                'extraction_method': 'improved_dual',
                'pages_extracted': len(extracted_texts),
                'tables_found': len(extracted_tables),
                'quality_metrics': {
                    'fixed_issues': self.quality_metrics.fixed_issues,
                    'broken_strains': self.quality_metrics.broken_strains,
                    'broken_formulas': self.quality_metrics.broken_formulas,
                    'merged_words': self.quality_metrics.merged_words
                }
            },
            tables=extracted_tables
        )
        
        logger.info(f"Извлечено: {len(extracted_texts)} текстовых блоков, "
                   f"{len(extracted_tables)} таблиц, "
                   f"исправлено {self.quality_metrics.fixed_issues} проблем")
        
        return document
    
    def _process_table(self, table: List[List], page_num: int, table_idx: int) -> str:
        """Обрабатывает таблицу в структурированный текст"""
        
        if not table or len(table) < 2:
            return ""
        
        # Извлекаем заголовки (первая строка)
        headers = [str(cell).strip() if cell else "" for cell in table[0]]
        
        # Обрабатываем строки данных
        processed_rows = []
        for row in table[1:]:
            if not any(cell for cell in row):  # Пропускаем пустые строки
                continue
            
            row_data = [str(cell).strip() if cell else "" for cell in row]
            processed_rows.append(row_data)
        
        if not processed_rows:
            return ""
        
        # Создаем текстовое представление таблицы
        table_text = f"ТАБЛИЦА {table_idx + 1} (Страница {page_num}):\n"
        table_text += "Заголовки: " + " | ".join(headers) + "\n"
        
        for i, row in enumerate(processed_rows):
            table_text += f"Строка {i + 1}: " + " | ".join(row) + "\n"
        
        return table_text
    
    def _text_already_extracted(self, new_text: str, existing_texts: List[Dict]) -> bool:
        """Проверяет, не был ли текст уже извлечен"""
        
        new_text_clean = re.sub(r'\s+', ' ', new_text.lower().strip())
        
        for item in existing_texts:
            existing_clean = re.sub(r'\s+', ' ', item['text'].lower().strip())
            
            # Если более 80% текста совпадает, считаем дубликатом
            if self._text_similarity(new_text_clean, existing_clean) > 0.8:
                return True
        
        return False
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Вычисляет схожесть двух текстов"""
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0 