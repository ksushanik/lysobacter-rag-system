"""
Модуль для улучшения качества извлечённого текста
Исправляет распространённые проблемы PDF экстракции
"""

import re
from typing import List, Dict, Any
from loguru import logger


class TextQualityImprover:
    """Улучшает качество извлечённого из PDF текста"""
    
    def __init__(self):
        """Инициализация с паттернами исправлений"""
        
        # Паттерны для исправления слитных слов
        self.word_split_patterns = [
            # Распространённые комбинации
            (r'([a-z])([A-Z])', r'\1 \2'),  # camelCase -> camel Case
            (r'(\d)([A-Za-z])', r'\1 \2'),  # 25C -> 25 C
            (r'([a-z])(\d)', r'\1 \2'),     # growth25 -> growth 25
            (r'([a-z])\+', r'\1 +'),        # pH7+ -> pH 7+
            (r'([a-z])-([a-z])', r'\1 - \2'),  # acid-base -> acid - base
        ]
        
        # Паттерны для научных терминов
        self.scientific_patterns = [
            # Штаммы
            (r'([A-Z][a-z]+)([A-Z]{2,}\d+)', r'\1 \2'),  # LysobacterYC5194 -> Lysobacter YC5194
            (r'strain([A-Z])', r'strain \1'),             # strainYC5194 -> strain YC5194
            (r'sp\.nov\.', 'sp. nov.'),                   # sp.nov. -> sp. nov.
            
            # Температуры
            (r'(\d+)°?C', r'\1°C'),                       # Нормализация температур
            (r'(\d+)-(\d+)°C', r'\1-\2°C'),              # Диапазоны температур
            
            # pH значения
            (r'pH(\d)', r'pH \1'),                        # pH7 -> pH 7
            (r'pH(\d+)\.(\d+)', r'pH \1.\2'),            # pH7.5 -> pH 7.5
            
            # Размеры
            (r'(\d+)×(\d+)', r'\1 × \2'),                # 2×5 -> 2 × 5  
            (r'(\d+)x(\d+)', r'\1 × \2'),                # 2x5 -> 2 × 5
            (r'(\d+)μm', r'\1 μm'),                       # 5μm -> 5 μm
        ]
        
        # Паттерны для биохимических тестов
        self.biochemical_patterns = [
            (r'(\+|\-)([A-Za-z])', r'\1 \2'),            # +glucose -> + glucose
            (r'([A-Za-z])(\+|\-)', r'\1 \2'),            # glucose+ -> glucose +
        ]
        
        # Словарь часто встречающихся научных терминов
        self.scientific_terms = {
            'Lysobacter': ['Lysobact', 'L.'],
            'temperature': ['temp', 'temperatur'],
            'characteristics': ['charact', 'character'],
            'growth': ['grow'],
            'strain': ['strn'],
            'capsici': ['caps'],
            'YC5194': ['YC5194T', 'YC-5194'],
        }
    
    def improve_text_quality(self, text: str) -> str:
        """
        Улучшает качество текста
        
        Args:
            text (str): Исходный текст
            
        Returns:
            str: Улучшенный текст
        """
        if not text or len(text.strip()) < 10:
            return text
        
        improved_text = text
        
        try:
            # 1. Основная очистка
            improved_text = self._basic_cleanup(improved_text)
            
            # 2. Исправление слитных слов
            improved_text = self._fix_merged_words(improved_text)
            
            # 3. Нормализация научных терминов
            improved_text = self._normalize_scientific_terms(improved_text)
            
            # 4. Исправление биохимических обозначений
            improved_text = self._fix_biochemical_notation(improved_text)
            
            # 5. Финальная очистка
            improved_text = self._final_cleanup(improved_text)
            
            return improved_text
            
        except Exception as e:
            logger.warning(f"Ошибка при улучшении текста: {e}")
            return text
    
    def _basic_cleanup(self, text: str) -> str:
        """Базовая очистка текста"""
        
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем символы таблиц
        text = re.sub(r'[|─━┌┐└┘├┤┬┴┼]', ' ', text)
        
        # Исправляем кодировку
        text = text.replace('â', '-')
        text = text.replace('°', '°')
        text = text.replace('μ', 'μ')
        
        return text.strip()
    
    def _fix_merged_words(self, text: str) -> str:
        """Исправляет слитные слова"""
        
        for pattern, replacement in self.word_split_patterns:
            text = re.sub(pattern, replacement, text)
        
        # Специальные случаи для научных текстов
        
        # Разделяем числа и единицы измерения
        text = re.sub(r'(\d+)(mg|ml|μl|°C|pH)', r'\1 \2', text)
        
        # Разделяем слова после точек (не в сокращениях)
        text = re.sub(r'\.([A-Z][a-z])', r'. \1', text)
        
        # Исправляем слитные предложения
        text = re.sub(r'([a-z])([A-Z][a-z])', r'\1. \2', text)
        
        return text
    
    def _normalize_scientific_terms(self, text: str) -> str:
        """Нормализует научные термины"""
        
        for pattern, replacement in self.scientific_patterns:
            text = re.sub(pattern, replacement, text)
        
        # Исправляем распространённые ошибки
        text = re.sub(r'L\.(\w)', r'L. \1', text)  # L.capsici -> L. capsici
        text = re.sub(r'(\w)T(\s|$)', r'\1T\2', text)  # YC5194 T -> YC5194T
        
        return text
    
    def _fix_biochemical_notation(self, text: str) -> str:
        """Исправляет биохимические обозначения"""
        
        for pattern, replacement in self.biochemical_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Финальная очистка"""
        
        # Удаляем множественные пробелы
        text = re.sub(r'\s{2,}', ' ', text)
        
        # Исправляем пунктуацию
        text = re.sub(r'\s+([,.;:])', r'\1', text)
        text = re.sub(r'([,.;:])\s*([A-Z])', r'\1 \2', text)
        
        # Исправляем скобки
        text = re.sub(r'\s+\)', ')', text)
        text = re.sub(r'\(\s+', '(', text)
        
        return text.strip()
    
    def analyze_text_quality(self, text: str) -> Dict[str, Any]:
        """
        Анализирует качество текста
        
        Args:
            text (str): Текст для анализа
            
        Returns:
            Dict[str, Any]: Метрики качества
        """
        if not text:
            return {'quality_score': 0, 'issues': ['Empty text']}
        
        issues = []
        
        # Проверяем слитные слова
        merged_words = len(re.findall(r'[a-z][A-Z]', text))
        if merged_words > 0:
            issues.append(f'Merged words: {merged_words}')
        
        # Проверяем отсутствие пробелов
        no_spaces = len(re.findall(r'[a-z]\d', text)) + len(re.findall(r'\d[a-z]', text))
        if no_spaces > 0:
            issues.append(f'Missing spaces: {no_spaces}')
        
        # Проверяем символы таблиц
        table_chars = len(re.findall(r'[|─━┌┐└┘├┤┬┴┼]', text))
        if table_chars > 0:
            issues.append(f'Table characters: {table_chars}')
        
        # Общий счёт качества
        total_issues = merged_words + no_spaces + table_chars
        quality_score = max(0, 100 - total_issues * 5)
        
        return {
            'quality_score': quality_score,
            'issues': issues,
            'merged_words': merged_words,
            'missing_spaces': no_spaces,
            'table_chars': table_chars
        }


# Глобальный экземпляр для использования
text_quality_improver = TextQualityImprover() 