"""
Исправленный модуль для извлечения данных из PDF файлов лизобактов
Использует только pdfplumber для устранения ошибок page_count_fz
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import pandas as pd
import pdfplumber
from thefuzz import fuzz
from tqdm import tqdm

from config import config


@dataclass
class ExtractedTable:
    """Класс для хранения извлеченной таблицы и ее метаданных"""
    source_pdf: str
    page_number: int
    title: str
    description: str
    table_data: pd.DataFrame
    legend: str
    confidence_score: float


@dataclass
class ExtractedDocument:
    """Класс для хранения извлеченного документа"""
    source_pdf: str
    text_content: str
    tables: List[ExtractedTable]
    total_pages: int


class PDFExtractor:
    """Исправленный класс для извлечения данных из PDF файлов"""
    
    def __init__(self):
        """Инициализация экстрактора"""
        self.target_patterns = config.TARGET_TITLE_PATTERNS
        self.threshold = config.FUZZY_MATCH_THRESHOLD
        
    def extract_all_pdfs(self, pdf_dir: str) -> List[ExtractedDocument]:
        """
        Извлекает данные из всех PDF файлов в указанной директории
        
        Args:
            pdf_dir (str): Путь к директории с PDF файлами
            
        Returns:
            List[ExtractedDocument]: Список извлеченных документов
        """
        pdf_path = Path(pdf_dir)
        pdf_files = list(pdf_path.glob("*.pdf"))
        
        logger.info(f"Найдено {len(pdf_files)} PDF файлов для обработки")
        
        extracted_docs = []
        
        for pdf_file in tqdm(pdf_files, desc="Обработка PDF файлов"):
            try:
                doc = self.extract_from_pdf(str(pdf_file))
                if doc:
                    extracted_docs.append(doc)
                    logger.info(f"Успешно обработан {pdf_file.name}")
            except Exception as e:
                logger.error(f"Ошибка при обработке {pdf_file.name}: {str(e)}")
                
        logger.info(f"Всего обработано {len(extracted_docs)} документов")
        return extracted_docs
    
    def extract_from_pdf(self, pdf_path: str) -> Optional[ExtractedDocument]:
        """
        Извлекает данные из одного PDF файла используя только pdfplumber
        
        Args:
            pdf_path (str): Путь к PDF файлу
            
        Returns:
            Optional[ExtractedDocument]: Извлеченный документ или None при ошибке
        """
        try:
            all_text = ""
            extracted_tables = []
            total_pages = 0
            
            logger.info(f"Обработка PDF: {Path(pdf_path).name}")
            
            # Открываем PDF с помощью pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                # Обрабатываем каждую страницу
                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Извлекаем текст
                        page_text = page.extract_text() or ""
                        all_text += f"\n=== СТРАНИЦА {page_num + 1} ===\n" + page_text
                        
                        # Ищем релевантные таблицы на странице
                        tables = self._find_tables_on_page(pdf_path, page_num, page_text, page)
                        extracted_tables.extend(tables)
                        
                    except Exception as e:
                        logger.warning(f"Ошибка при обработке страницы {page_num + 1}: {str(e)}")
                        continue
            
            logger.info(f"Успешно обработан PDF: {Path(pdf_path).name} ({total_pages} страниц, {len(extracted_tables)} таблиц)")
            
            return ExtractedDocument(
                source_pdf=Path(pdf_path).name,
                text_content=all_text,
                tables=extracted_tables,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении из {pdf_path}: {str(e)}")
            return None
    
    def _find_tables_on_page(self, pdf_path: str, page_num: int, page_text: str, page_obj) -> List[ExtractedTable]:
        """
        Ищет релевантные таблицы на странице
        
        Args:
            pdf_path (str): Путь к PDF файлу
            page_num (int): Номер страницы
            page_text (str): Текст страницы
            page_obj: Объект страницы pdfplumber
            
        Returns:
            List[ExtractedTable]: Список найденных таблиц
        """
        found_tables = []
        
        # Ищем заголовки таблиц с помощью нечеткого поиска
        lines = page_text.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if len(line_clean) < 10:  # Пропускаем слишком короткие строки
                continue
                
            # Проверяем соответствие паттернам заголовков
            best_match_score = 0
            best_pattern = ""
            
            for pattern in self.target_patterns:
                score = fuzz.partial_ratio(pattern.lower(), line_clean.lower())
                if score > best_match_score:
                    best_match_score = score
                    best_pattern = pattern
            
            # Если найдено совпадение выше порога
            if best_match_score >= self.threshold:
                logger.info(f"Найден заголовок таблицы: '{line_clean}' (совпадение: {best_match_score}%)")
                
                # Извлекаем таблицу
                table = self._extract_table_data(pdf_path, page_num, i, lines, line_clean, best_match_score, page_obj)
                if table:
                    found_tables.append(table)
        
        return found_tables
    
    def _extract_table_data(self, pdf_path: str, page_num: int, title_line_idx: int, 
                           page_lines: List[str], title: str, confidence: float, page_obj) -> Optional[ExtractedTable]:
        """
        Извлекает данные таблицы с помощью pdfplumber
        
        Args:
            pdf_path (str): Путь к PDF файлу
            page_num (int): Номер страницы
            title_line_idx (int): Индекс строки с заголовком
            page_lines (List[str]): Все строки страницы
            title (str): Заголовок таблицы
            confidence (float): Уверенность в совпадении
            page_obj: Объект страницы pdfplumber
            
        Returns:
            Optional[ExtractedTable]: Извлеченная таблица или None
        """
        try:
            # Используем переданный объект страницы для извлечения таблиц
            tables = page_obj.extract_tables()
            
            if not tables:
                logger.warning(f"На странице {page_num + 1} не найдено таблиц")
                return None
            
            # Берем первую найденную таблицу (можно улучшить логику выбора)
            table_data = tables[0]
            
            # Преобразуем в DataFrame
            if len(table_data) > 1:
                headers = table_data[0]
                data = table_data[1:]
                df = pd.DataFrame(data, columns=headers)
            else:
                df = pd.DataFrame(table_data)
            
            # Очищаем пустые строки и столбцы
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Извлекаем описание (строки перед заголовком)
            description = self._extract_description(page_lines, title_line_idx)
            
            # Извлекаем легенду (строки после таблицы)
            legend = self._extract_legend(page_lines, title_line_idx)
            
            return ExtractedTable(
                source_pdf=Path(pdf_path).name,
                page_number=page_num + 1,
                title=title,
                description=description,
                table_data=df,
                legend=legend,
                confidence_score=confidence
            )
                
        except Exception as e:
            logger.error(f"Ошибка при извлечении таблицы: {str(e)}")
            return None
    
    def _extract_description(self, lines: List[str], title_idx: int) -> str:
        """
        Извлекает описание таблицы (текст перед заголовком)
        
        Args:
            lines (List[str]): Строки страницы
            title_idx (int): Индекс заголовка таблицы
            
        Returns:
            str: Описание таблицы
        """
        description_lines = []
        
        # Ищем описание в 5 строках перед заголовком
        start_idx = max(0, title_idx - 5)
        
        for i in range(start_idx, title_idx):
            line = lines[i].strip()
            if line and not self._is_header_or_footer(line):
                description_lines.append(line)
        
        return " ".join(description_lines)
    
    def _extract_legend(self, lines: List[str], title_idx: int) -> str:
        """
        Извлекает легенду таблицы (текст после таблицы)
        
        Args:
            lines (List[str]): Строки страницы
            title_idx (int): Индекс заголовка таблицы
            
        Returns:
            str: Легенда таблицы
        """
        legend_lines = []
        legend_keywords = ['note:', 'legend:', 'abbreviations:', 'symbols:', 'footnote:']
        
        # Ищем легенду в 10 строках после заголовка
        end_idx = min(len(lines), title_idx + 15)
        
        for i in range(title_idx + 1, end_idx):
            line = lines[i].strip().lower()
            
            # Проверяем, начинается ли строка с ключевых слов легенды
            if any(keyword in line for keyword in legend_keywords):
                # Собираем все следующие строки как часть легенды
                for j in range(i, min(len(lines), i + 5)):
                    legend_line = lines[j].strip()
                    if legend_line:
                        legend_lines.append(legend_line)
                break
        
        return " ".join(legend_lines)
    
    def _is_header_or_footer(self, line: str) -> bool:
        """
        Проверяет, является ли строка заголовком или футером страницы
        
        Args:
            line (str): Строка для проверки
            
        Returns:
            bool: True если это заголовок/футер
        """
        line_lower = line.lower()
        
        # Признаки заголовков/футеров
        header_footer_patterns = [
            r'page \d+',
            r'^\d+$',  # только номер
            r'copyright',
            r'doi:',
            r'journal',
            r'volume',
            r'issue',
        ]
        
        return any(re.search(pattern, line_lower) for pattern in header_footer_patterns)
    
    def save_extracted_data(self, extracted_docs: List[ExtractedDocument], output_dir: str):
        """
        Сохраняет извлеченные данные в файлы
        
        Args:
            extracted_docs (List[ExtractedDocument]): Извлеченные документы
            output_dir (str): Директория для сохранения
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Сохраняем информацию о найденных таблицах
        tables_info = []
        
        for doc in extracted_docs:
            for table in doc.tables:
                tables_info.append({
                    'source_pdf': table.source_pdf,
                    'page_number': table.page_number,
                    'title': table.title,
                    'description': table.description,
                    'legend': table.legend,
                    'confidence_score': table.confidence_score,
                    'table_shape': f"{table.table_data.shape[0]}x{table.table_data.shape[1]}"
                })
                
                # Сохраняем каждую таблицу отдельно
                table_filename = f"{table.source_pdf}_page_{table.page_number}_table.csv"
                table.table_data.to_csv(output_path / table_filename, index=False)
        
        # Сохраняем сводную информацию
        tables_df = pd.DataFrame(tables_info)
        tables_df.to_csv(output_path / "extracted_tables_summary.csv", index=False)
        
        logger.info(f"Сохранено {len(tables_info)} таблиц в {output_dir}")


if __name__ == "__main__":
    # Пример использования
    extractor = PDFExtractor()
    docs = extractor.extract_all_pdfs(str(config.DATA_DIR))
    extractor.save_extracted_data(docs, str(config.STORAGE_DIR / "extracted_data")) 