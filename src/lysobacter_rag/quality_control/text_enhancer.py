"""
Продвинутый улучшитель качества научного текста
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from loguru import logger

@dataclass
class EnhancementMetrics:
    """Метрики улучшения текста"""
    total_fixes: int = 0
    strain_fixes: int = 0
    formula_fixes: int = 0
    unit_fixes: int = 0
    term_fixes: int = 0
    number_fixes: int = 0

class ScientificTextEnhancer:
    """Продвинутый улучшитель научного текста"""
    
    def __init__(self):
        self.metrics = EnhancementMetrics()
        self._load_scientific_rules()
    
    def _load_scientific_rules(self):
        """Загружает правила для научного текста"""
        
        # Правила для штаммовых номеров
        self.strain_patterns = [
            # Основные паттерны
            (r'GW\s*1-\s*5\s*9\s*T', 'GW1-59T'),
            (r'(\w+)\s*-\s*(\d+)\s+T', r'\1-\2T'),
            (r'(\w+)\s+(\d+)\s*-\s*(\w+)', r'\1 \2-\3'),
            
            # Коллекции культур
            (r'KCTC\s+(\d+)\s*T', r'KCTC \1T'),
            (r'DSM\s+(\d+)', r'DSM \1'),
            (r'ATCC\s+(\d+)', r'ATCC \1'),
            (r'JCM\s+(\d+)', r'JCM \1'),
            
            # Типовые штаммы
            (r'Ko\s*(\d+)\s*T', r'Ko\1T'),
            (r'([A-Z]+)\s*(\d+)\s*T', r'\1\2T'),
        ]
        
        # Правила для химических формул
        self.formula_patterns = [
            # Жирные кислоты
            (r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2'),
            (r'iso-\s*C\s+(\d+)', r'iso-C\1'),
            (r'anteiso-\s*C\s+(\d+)', r'anteiso-C\1'),
            (r'(\w+)-\s*C\s+(\d+)', r'\1-C\2'),
            
            # Хиноны
            (r'Q-\s*(\d+)', r'Q-\1'),
            (r'MK-\s*(\d+)', r'MK-\1'),
            (r'ubiquinone-\s*(\d+)', r'ubiquinone-\1'),
            
            # Другие формулы
            (r'G\s*\+\s*C', 'G+C'),
            (r'(\d+)\s*%\s*G\s*\+\s*C', r'\1% G+C'),
        ]
        
        # Правила для единиц измерения
        self.unit_patterns = [
            # Температура
            (r'(\d+)\s*[-–]\s*(\d+)\s*°?\s*C', r'\1–\2°C'),
            (r'(\d+)\s*uC', r'\1°C'),
            (r'(\d+)\s*degrees?\s*C', r'\1°C'),
            (r'optimum,?\s*(\d+)\s*°C', r'optimum \1°C'),
            
            # pH
            (r'pH\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'pH \1–\2'),
            (r'pH\s+range\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'pH range \1–\2'),
            
            # Концентрации
            (r'(\d+)\s*[-–]\s*(\d+)\s*%\s*(w/v)', r'\1–\2% (w/v)'),
            (r'(\d+)\s*[-–]\s*(\d+)\s*%.*?NaCl', r'\1–\2% NaCl'),
            (r'NaCl.*?(\d+)\s*[-–]\s*(\d+)\s*%', r'NaCl \1–\2%'),
            
            # Размеры
            (r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*μm', r'\1–\2 μm'),
            (r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*×\s*(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*μm', 
             r'\1–\2 × \3–\4 μm'),
            
            # Геном
            (r'(\d+\.?\d*)\s*Mb', r'\1 Mb'),
            (r'(\d+),(\d+),(\d+)\s*bp', r'\1,\2,\3 bp'),
        ]
        
        # Правила для научных терминов
        self.term_patterns = [
            # Разорванные термины
            (r'Lyso\s*bacter', 'Lysobacter'),
            (r'phylo\s*genetically', 'phylogenetically'),
            (r'chemo\s*taxonomic', 'chemotaxonomic'),
            (r'pheno\s*typic', 'phenotypic'),
            (r'geno\s*typic', 'genotypic'),
            
            # Методы
            (r'16S\s*rRNA', '16S rRNA'),
            (r'DNA-\s*DNA\s*hybridization', 'DNA-DNA hybridization'),
            (r'eggNOG-\s*mapper', 'eggNOG-mapper'),
            
            # Номенклатура
            (r'sp\.\s*nov\.?', 'sp. nov.'),
            (r'type\s+strain', 'type strain'),
            (r'novel\s+species', 'novel species'),
        ]
        
        # Правила для чисел
        self.number_patterns = [
            # Десятичные числа
            (r'(\d+)\s*\.\s*(\d+)', r'\1.\2'),
            (r'(\d+)\s*,\s*(\d+)', r'\1,\2'),
            
            # Проценты
            (r'(\d+\.?\d*)\s*%', r'\1%'),
            
            # Диапазоны
            (r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'\1–\2'),
        ]
    
    def enhance_text(self, text: str) -> Tuple[str, EnhancementMetrics]:
        """Улучшает качество научного текста"""
        
        # Сбрасываем метрики
        self.metrics = EnhancementMetrics()
        original_text = text
        
        # Применяем правила по категориям
        text = self._fix_strain_nomenclature(text)
        text = self._fix_chemical_formulas(text)
        text = self._fix_units_and_measurements(text)
        text = self._fix_scientific_terms(text)
        text = self._fix_numbers(text)
        text = self._fix_general_formatting(text)
        
        # Подсчитываем общее количество исправлений
        if text != original_text:
            self.metrics.total_fixes = 1
        
        return text, self.metrics
    
    def _fix_strain_nomenclature(self, text: str) -> str:
        """Исправляет номенклатуру штаммов"""
        
        original_text = text
        
        for pattern, replacement in self.strain_patterns:
            new_text = re.sub(pattern, replacement, text)
            if new_text != text:
                self.metrics.strain_fixes += 1
                text = new_text
        
        return text
    
    def _fix_chemical_formulas(self, text: str) -> str:
        """Исправляет химические формулы"""
        
        original_text = text
        
        for pattern, replacement in self.formula_patterns:
            new_text = re.sub(pattern, replacement, text)
            if new_text != text:
                self.metrics.formula_fixes += 1
                text = new_text
        
        return text
    
    def _fix_units_and_measurements(self, text: str) -> str:
        """Исправляет единицы измерения"""
        
        original_text = text
        
        for pattern, replacement in self.unit_patterns:
            new_text = re.sub(pattern, replacement, text)
            if new_text != text:
                self.metrics.unit_fixes += 1
                text = new_text
        
        return text
    
    def _fix_scientific_terms(self, text: str) -> str:
        """Исправляет научные термины"""
        
        original_text = text
        
        for pattern, replacement in self.term_patterns:
            new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            if new_text != text:
                self.metrics.term_fixes += 1
                text = new_text
        
        return text
    
    def _fix_numbers(self, text: str) -> str:
        """Исправляет форматирование чисел"""
        
        original_text = text
        
        for pattern, replacement in self.number_patterns:
            new_text = re.sub(pattern, replacement, text)
            if new_text != text:
                self.metrics.number_fixes += 1
                text = new_text
        
        return text
    
    def _fix_general_formatting(self, text: str) -> str:
        """Общие исправления форматирования"""
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Исправляем переносы строк
        text = re.sub(r'\s*-\s*\n\s*', '', text)
        
        # Убираем пробелы в начале и конце
        text = text.strip()
        
        return text
    
    def get_quality_score(self, text: str) -> float:
        """Вычисляет скор качества текста (0-1)"""
        
        issues = 0
        total_checks = 0
        
        # Проверяем наличие проблем
        checks = [
            (r'\w+\s*-\s*\d+\s+T', 'разорванные штаммы'),
            (r'C\s+\d+\s*:\s*\d+', 'разорванные формулы'),
            (r'\d+\s*\.\s*\d+', 'разорванные числа'),
            (r'[a-zA-Z]{50,}', 'слитные слова'),
            (r'\d+\s+°\s+C', 'разорванные единицы'),
        ]
        
        for pattern, description in checks:
            total_checks += 1
            if re.search(pattern, text):
                issues += 1
        
        if total_checks == 0:
            return 1.0
        
        return max(0.0, 1.0 - (issues / total_checks))
    
    def validate_enhancement(self, original: str, enhanced: str) -> Dict[str, any]:
        """Валидирует качество улучшения"""
        
        original_score = self.get_quality_score(original)
        enhanced_score = self.get_quality_score(enhanced)
        
        return {
            'original_score': original_score,
            'enhanced_score': enhanced_score,
            'improvement': enhanced_score - original_score,
            'successful': enhanced_score > original_score,
            'metrics': self.metrics
        }
    
    def add_custom_rule(self, pattern: str, replacement: str, category: str = 'custom'):
        """Добавляет пользовательское правило улучшения"""
        
        if category == 'strain':
            self.strain_patterns.append((pattern, replacement))
        elif category == 'formula':
            self.formula_patterns.append((pattern, replacement))
        elif category == 'unit':
            self.unit_patterns.append((pattern, replacement))
        elif category == 'term':
            self.term_patterns.append((pattern, replacement))
        elif category == 'number':
            self.number_patterns.append((pattern, replacement))
        else:
            # Создаем категорию custom если нет
            if not hasattr(self, 'custom_patterns'):
                self.custom_patterns = []
            self.custom_patterns.append((pattern, replacement))
        
        logger.info(f"Добавлено правило {category}: {pattern} -> {replacement}")
    
    def get_enhancement_report(self) -> Dict[str, any]:
        """Генерирует отчет об улучшениях"""
        
        return {
            'total_fixes': self.metrics.total_fixes,
            'strain_fixes': self.metrics.strain_fixes,
            'formula_fixes': self.metrics.formula_fixes,
            'unit_fixes': self.metrics.unit_fixes,
            'term_fixes': self.metrics.term_fixes,
            'number_fixes': self.metrics.number_fixes,
            'rules_loaded': {
                'strain_patterns': len(self.strain_patterns),
                'formula_patterns': len(self.formula_patterns),
                'unit_patterns': len(self.unit_patterns),
                'term_patterns': len(self.term_patterns),
                'number_patterns': len(self.number_patterns)
            }
        } 