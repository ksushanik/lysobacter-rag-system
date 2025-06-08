#!/usr/bin/env python3
"""
Компонент для сравнительного анализа множественных видов Lysobacter
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from loguru import logger

@dataclass
class SpeciesData:
    """Данные о виде для сравнительного анализа"""
    species_name: str
    strain_designation: Optional[str]
    morphology: Dict[str, str]
    physiology: Dict[str, str]
    biochemistry: Dict[str, str]
    ecology: Dict[str, str]
    source_info: List[str]

@dataclass
class ComparativeReport:
    """Результат сравнительного анализа"""
    query_type: str
    species_count: int
    compared_characteristics: List[str]
    common_features: Dict[str, str]
    distinguishing_features: Dict[str, Dict[str, str]]
    summary_table: List[Dict[str, str]]
    formatted_response: str

class ComparativeAnalyzer:
    """Анализатор для сравнения множественных видов Lysobacter"""
    
    def __init__(self):
        self.species_patterns = self._init_species_patterns()
        self.characteristic_patterns = self._init_characteristic_patterns()
        
    def _init_species_patterns(self) -> Dict[str, str]:
        """Инициализирует паттерны для поиска видов"""
        return {
            'species_mention': r'(Lysobacter\s+[a-z]+(?:ensis|icus|atus|ensis|us|is|ae|um|e)?(?:\s+sp\.?\s*nov\.?)?)',
            'strain_designation': r'((?:штамм|strain|isolate)\s+([A-Z0-9-]+T?))',
            'type_strain': r'(\[T\]|\[Т\]|типовой штамм|type strain|type\s+strain)',
        }
    
    def _init_characteristic_patterns(self) -> Dict[str, Dict[str, str]]:
        """Инициализирует паттерны для извлечения характеристик"""
        return {
            'morphology': {
                'cell_shape': r'(палочковидн[ыае]*|rod[s\-]*shaped|сферическ[иае]*|spherical|нитевидн[ыае]*|filamentous|oval|овальн[ыае]*|короткие палочки|short rods)',
                'cell_size': r'(\d+[.,]\d+[-–×]\d+[.,]\d+\s*[мm][кk]?[мm]|\d+[.,]\d+\s*[мm][кk]?[мm]|размер[ыом]*[:\s]*\d+[.,]?\d*[-–×]\d+[.,]?\d*)',
                'gram_stain': r'(грам[-\s]*(отрицательн[ыае]*|положительн[ыае]*)|gram[-\s]*(negative|positive)|Gram[-\s]*(отрицательн[ыае]*|положительн[ыае]*|negative|positive))',
                'motility': r'(подвижн[ыае]*|неподвижн[ыае]*|motile|non[-\s]*motile|скользящ[аяие]*|gliding|flagell[aur]*|жгутик[ами]*)',
                'colony_color': r'(желт[ыаоуе]*|yellow|бледн[ыаоуе]*|pale|кремов[ыаоуе]*|cream|розов[ыаоуе]*|pink|коричнев[ыаоуе]*|brown|зелен[ыаоуе]*|green|белый|white|оранжев[ыаоуе]*|orange)',
                'spore_formation': r'(спорообразующ[ияе]*|не\s+образ[ующие]*.*спор|non[-\s]*spore|spore[-\s]*forming)',
            },
            'physiology': {
                'temperature': r'(\d+[-–]\d+\s*°C|оптимальн.*\d+\s*°C)',
                'ph_range': r'(pH\s+\d+[.,]\d+[-–]\d+[.,]\d+)',
                'oxygen_requirement': r'(аэробн|aerobic|анаэробн|anaerobic|факультативн|facultative)',
                'nacl_tolerance': r'(\d+[.,]?\d*[-–]\d+[.,]?\d*\s*%.*NaCl)',
            },
            'biochemistry': {
                'catalase': r'(каталаз[ая][-\s]*(положительн|отрицательн|positive|negative))',
                'oxidase': r'(оксидаз[ая][-\s]*(положительн|отрицательн|positive|negative))',
                'urease': r'(уреаз[ая][-\s]*(положительн|отрицательн|positive|negative))',
                'hydrolysis': r'(гидролиз.*?(желатин|gelatin|крахмал|starch))',
            },
            'ecology': {
                'habitat': r'(почв|soil|ризосфер|rhizosphere|морск|marine|пресноводн|freshwater)',
                'isolation_source': r'(изолирован|выделен|isolated).*?из\s+([^.]+)',
                'geographic_origin': r'(Корея|Korea|Китай|China|Антарктид|Antarctica|США|USA)',
            }
        }
    
    def analyze_comparative_query(self, context: str, query: str) -> ComparativeReport:
        """Главный метод для сравнительного анализа"""
        logger.info(f"Анализирую сравнительный запрос: {query[:50]}...")
        
        # Определяем тип сравнительного запроса
        query_type = self._identify_query_type(query)
        
        # Извлекаем данные о видах из контекста
        species_data = self._extract_species_data(context)
        
        if not species_data:
            return self._create_no_data_response(query_type)
        
        # Выполняем сравнительный анализ
        if query_type == "morphological":
            return self._compare_morphology(species_data, query)
        elif query_type == "physiological":
            return self._compare_physiology(species_data, query)
        elif query_type == "ecological":
            return self._compare_ecology(species_data, query)
        else:
            return self._general_comparison(species_data, query)
    
    def _identify_query_type(self, query: str) -> str:
        """Определяет тип сравнительного запроса"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['морфолог', 'размер', 'форма', 'morpholog', 'shape', 'size']):
            return "morphological"
        elif any(word in query_lower for word in ['физиолог', 'температур', 'рост', 'physiol', 'growth', 'temperature']):
            return "physiological" 
        elif any(word in query_lower for word in ['биохим', 'фермент', 'biochem', 'enzyme', 'метабол']):
            return "biochemical"
        elif any(word in query_lower for word in ['экология', 'среда', 'местообит', 'ecology', 'habitat', 'environment']):
            return "ecological"
        else:
            return "general"
    
    def _extract_species_data(self, context: str) -> List[SpeciesData]:
        """Извлекает данные о всех видах из контекста"""
        species_list = []
        
        # Находим все упоминания видов Lysobacter
        species_mentions = re.findall(self.species_patterns['species_mention'], context, re.IGNORECASE)
        unique_species = list(set(species_mentions))
        
        for species in unique_species:
            species_data = self._extract_single_species_data(context, species)
            if species_data:
                species_list.append(species_data)
        
        logger.info(f"Извлечено данных о {len(species_list)} видах")
        return species_list
    
    def _extract_single_species_data(self, context: str, species_name: str) -> Optional[SpeciesData]:
        """Извлекает данные об одном виде"""
        # Создаем контекст для конкретного вида
        species_context = self._get_species_context(context, species_name)
        
        if not species_context:
            return None
        
        # Извлекаем характеристики
        morphology = self._extract_characteristics(species_context, 'morphology')
        physiology = self._extract_characteristics(species_context, 'physiology')
        biochemistry = self._extract_characteristics(species_context, 'biochemistry')
        ecology = self._extract_characteristics(species_context, 'ecology')
        
        # Ищем штамм
        strain_match = re.search(self.species_patterns['strain_designation'], species_context, re.IGNORECASE)
        strain = strain_match.group(2) if strain_match else None
        
        return SpeciesData(
            species_name=species_name,
            strain_designation=strain,
            morphology=morphology,
            physiology=physiology,
            biochemistry=biochemistry,
            ecology=ecology,
            source_info=[f"Источник для {species_name}"]
        )
    
    def _get_species_context(self, full_context: str, species_name: str) -> str:
        """Получает релевантный контекст для конкретного вида"""
        # Ищем параграфы, содержащие упоминание вида
        paragraphs = full_context.split('\n')
        relevant_paragraphs = []
        
        for paragraph in paragraphs:
            if species_name.lower() in paragraph.lower():
                relevant_paragraphs.append(paragraph)
        
        return '\n'.join(relevant_paragraphs)
    
    def _extract_characteristics(self, context: str, category: str) -> Dict[str, str]:
        """Извлекает характеристики определенной категории"""
        characteristics = {}
        
        if category in self.characteristic_patterns:
            patterns = self.characteristic_patterns[category]
            
            for char_name, pattern in patterns.items():
                matches = re.search(pattern, context, re.IGNORECASE)
                if matches:
                    characteristics[char_name] = matches.group(0)
        
        return characteristics
    
    def _compare_morphology(self, species_data: List[SpeciesData], query: str) -> ComparativeReport:
        """Сравнивает морфологические характеристики"""
        compared_chars = ['cell_shape', 'cell_size', 'gram_stain', 'motility', 'colony_color']
        
        # Собираем общие черты
        common_features = {}
        distinguishing_features = {}
        summary_table = []
        
        # Анализ общих черт
        for char in compared_chars:
            values = []
            for species in species_data:
                if char in species.morphology:
                    values.append(species.morphology[char])
            
            if values and len(set(values)) == 1:  # Все одинаковые
                common_features[char] = values[0]
        
        # Анализ различающихся черт
        for species in species_data:
            distinguishing_features[species.species_name] = {}
            row = {'species': species.species_name}
            
            for char in compared_chars:
                value = species.morphology.get(char, 'Не указано')
                distinguishing_features[species.species_name][char] = value
                row[char] = value
            
            summary_table.append(row)
        
        # Формируем ответ
        formatted_response = self._format_morphological_response(
            species_data, common_features, distinguishing_features, summary_table
        )
        
        return ComparativeReport(
            query_type="morphological",
            species_count=len(species_data),
            compared_characteristics=compared_chars,
            common_features=common_features,
            distinguishing_features=distinguishing_features,
            summary_table=summary_table,
            formatted_response=formatted_response
        )
    
    def _format_morphological_response(self, species_data: List[SpeciesData], 
                                     common_features: Dict[str, str],
                                     distinguishing_features: Dict[str, Dict[str, str]],
                                     summary_table: List[Dict[str, str]]) -> str:
        """Форматирует ответ о морфологических характеристиках"""
        
        response = f"## СРАВНИТЕЛЬНЫЙ АНАЛИЗ МОРФОЛОГИЧЕСКИХ ХАРАКТЕРИСТИК\n\n"
        response += f"Проанализировано **{len(species_data)} видов** рода *Lysobacter*.\n\n"
        
        # Общие черты
        if common_features:
            response += "### 🔄 ОБЩИЕ МОРФОЛОГИЧЕСКИЕ ЧЕРТЫ:\n"
            for char, value in common_features.items():
                char_name = self._translate_characteristic(char)
                response += f"- **{char_name}**: {value}\n"
            response += "\n"
        
        # Различающиеся черты
        response += "### 🔍 ВИДОВЫЕ РАЗЛИЧИЯ:\n\n"
        for species_name, characteristics in distinguishing_features.items():
            response += f"**{species_name}**:\n"
            for char, value in characteristics.items():
                if value != 'Не указано':
                    char_name = self._translate_characteristic(char)
                    response += f"- {char_name}: {value}\n"
            response += "\n"
        
        # Сводная таблица
        response += "### 📊 СВОДНАЯ ТАБЛИЦА:\n\n"
        response += "| Вид | Форма клеток | Размер | Окраска по Граму | Подвижность | Цвет колоний |\n"
        response += "|-----|-------------|---------|------------------|-------------|-------------|\n"
        
        for row in summary_table:
            species = row.get('species', '')
            cell_shape = row.get('cell_shape', 'Н/Д')[:20]
            cell_size = row.get('cell_size', 'Н/Д')[:15]
            gram_stain = row.get('gram_stain', 'Н/Д')[:15]
            motility = row.get('motility', 'Н/Д')[:15]
            colony_color = row.get('colony_color', 'Н/Д')[:15]
            
            response += f"| {species} | {cell_shape} | {cell_size} | {gram_stain} | {motility} | {colony_color} |\n"
        
        response += "\n### 💡 ВЫВОДЫ:\n"
        response += f"Анализ показал значительное **морфологическое разнообразие** среди {len(species_data)} видов рода *Lysobacter*. "
        
        if common_features:
            response += "Обнаружены общие черты, характерные для всего рода. "
        
        response += "Видовые различия позволяют проводить таксономическое разграничение."
        
        return response
    
    def _format_physiological_response(self, species_data: List[SpeciesData], 
                                      common_features: Dict[str, str],
                                      distinguishing_features: Dict[str, Dict[str, str]],
                                      summary_table: List[Dict[str, str]]) -> str:
        """Форматирует ответ о физиологических характеристиках"""
        
        response = f"## СРАВНИТЕЛЬНЫЙ АНАЛИЗ ФИЗИОЛОГИЧЕСКИХ ХАРАКТЕРИСТИК\n\n"
        response += f"Проанализировано **{len(species_data)} видов** рода *Lysobacter*.\n\n"
        
        # Общие черты
        if common_features:
            response += "### 🔄 ОБЩИЕ ФИЗИОЛОГИЧЕСКИЕ ЧЕРТЫ:\n"
            for char, value in common_features.items():
                char_name = self._translate_characteristic(char)
                response += f"- **{char_name}**: {value}\n"
            response += "\n"
        
        # Различающиеся черты
        response += "### 🔍 ВИДОВЫЕ РАЗЛИЧИЯ:\n\n"
        for species_name, characteristics in distinguishing_features.items():
            response += f"**{species_name}**:\n"
            for char, value in characteristics.items():
                if value != 'Не указано':
                    char_name = self._translate_characteristic(char)
                    response += f"- {char_name}: {value}\n"
            response += "\n"
        
        # Сводная таблица
        response += "### 📊 СВОДНАЯ ТАБЛИЦА:\n\n"
        response += "| Вид | Температура | pH диапазон | Кислород | NaCl толерантность |\n"
        response += "|-----|-------------|-------------|----------|-------------------|\n"
        
        for row in summary_table:
            species = row.get('species', '')
            temperature = row.get('temperature', 'Н/Д')[:15]
            ph_range = row.get('ph_range', 'Н/Д')[:15]
            oxygen = row.get('oxygen_requirement', 'Н/Д')[:15]
            nacl = row.get('nacl_tolerance', 'Н/Д')[:15]
            
            response += f"| {species} | {temperature} | {ph_range} | {oxygen} | {nacl} |\n"
        
        response += "\n### 💡 ВЫВОДЫ:\n"
        response += f"Анализ показал **физиологическое разнообразие** среди {len(species_data)} видов рода *Lysobacter*."
        
        return response
    
    def _format_ecological_response(self, species_data: List[SpeciesData], 
                                   common_features: Dict[str, str],
                                   distinguishing_features: Dict[str, Dict[str, str]],
                                   summary_table: List[Dict[str, str]]) -> str:
        """Форматирует ответ об экологических характеристиках"""
        
        response = f"## СРАВНИТЕЛЬНЫЙ АНАЛИЗ ЭКОЛОГИЧЕСКИХ ХАРАКТЕРИСТИК\n\n"
        response += f"Проанализировано **{len(species_data)} видов** рода *Lysobacter*.\n\n"
        
        # Общие черты
        if common_features:
            response += "### 🔄 ОБЩИЕ ЭКОЛОГИЧЕСКИЕ ЧЕРТЫ:\n"
            for char, value in common_features.items():
                char_name = self._translate_characteristic(char)
                response += f"- **{char_name}**: {value}\n"
            response += "\n"
        
        # Различающиеся черты
        response += "### 🔍 ВИДОВЫЕ РАЗЛИЧИЯ:\n\n"
        for species_name, characteristics in distinguishing_features.items():
            response += f"**{species_name}**:\n"
            for char, value in characteristics.items():
                if value != 'Не указано':
                    char_name = self._translate_characteristic(char)
                    response += f"- {char_name}: {value}\n"
            response += "\n"
        
        # Сводная таблица
        response += "### 📊 СВОДНАЯ ТАБЛИЦА:\n\n"
        response += "| Вид | Местообитание | Источник изоляции | Географическое происхождение |\n"
        response += "|-----|---------------|-------------------|------------------------------|\n"
        
        for row in summary_table:
            species = row.get('species', '')
            habitat = row.get('habitat', 'Н/Д')[:20]
            isolation = row.get('isolation_source', 'Н/Д')[:20]
            geography = row.get('geographic_origin', 'Н/Д')[:20]
            
            response += f"| {species} | {habitat} | {isolation} | {geography} |\n"
        
        response += "\n### 💡 ВЫВОДЫ:\n"
        response += f"Анализ показал **экологическое разнообразие** среди {len(species_data)} видов рода *Lysobacter*."
        
        return response
    
    def _format_general_response(self, species_data: List[SpeciesData], 
                                common_features: Dict[str, str],
                                distinguishing_features: Dict[str, Dict[str, str]],
                                summary_table: List[Dict[str, str]]) -> str:
        """Форматирует общий сравнительный ответ"""
        
        response = f"## ОБЩИЙ СРАВНИТЕЛЬНЫЙ АНАЛИЗ ВИДОВ LYSOBACTER\n\n"
        response += f"Проанализировано **{len(species_data)} видов** рода *Lysobacter*.\n\n"
        
        # Общие черты
        if common_features:
            response += "### 🔄 ОБЩИЕ ЧЕРТЫ РОДА:\n"
            for char, value in common_features.items():
                char_name = self._translate_characteristic(char)
                response += f"- **{char_name}**: {value}\n"
            response += "\n"
        
        # Различающиеся черты (показываем только первые 10 для краткости)
        response += "### 🔍 ОСНОВНЫЕ ВИДОВЫЕ РАЗЛИЧИЯ:\n\n"
        species_shown = 0
        for species_name, characteristics in distinguishing_features.items():
            if species_shown >= 10:
                response += f"*... и еще {len(distinguishing_features) - 10} видов*\n"
                break
                
            response += f"**{species_name}**:\n"
            key_chars = 0
            for char, value in characteristics.items():
                if value != 'Не указано' and key_chars < 3:
                    char_name = self._translate_characteristic(char)
                    response += f"- {char_name}: {value}\n"
                    key_chars += 1
            response += "\n"
            species_shown += 1
        
        response += "### 💡 ВЫВОДЫ:\n"
        response += f"Род *Lysobacter* демонстрирует значительное **фенотипическое разнообразие** среди {len(species_data)} проанализированных видов. "
        response += "Это разнообразие отражает адаптацию к различным экологическим нишам и имеет важное таксономическое значение."
        
        return response
    
    def _translate_characteristic(self, char: str) -> str:
        """Переводит названия характеристик на русский"""
        translations = {
            'cell_shape': 'Форма клеток',
            'cell_size': 'Размер клеток', 
            'gram_stain': 'Окраска по Граму',
            'motility': 'Подвижность',
            'colony_color': 'Цвет колоний',
            'spore_formation': 'Спорообразование',
            'temperature': 'Температурный диапазон',
            'ph_range': 'pH диапазон',
            'oxygen_requirement': 'Потребность в кислороде',
            'habitat': 'Местообитание'
        }
        return translations.get(char, char)
    
    def _compare_physiology(self, species_data: List[SpeciesData], query: str) -> ComparativeReport:
        """Сравнивает физиологические характеристики"""
        compared_chars = ['temperature', 'ph_range', 'oxygen_requirement', 'nacl_tolerance']
        
        # Собираем общие черты
        common_features = {}
        distinguishing_features = {}
        summary_table = []
        
        # Анализ общих черт
        for char in compared_chars:
            values = []
            for species in species_data:
                if char in species.physiology:
                    values.append(species.physiology[char])
            
            if values and len(set(values)) == 1:  # Все одинаковые
                common_features[char] = values[0]
        
        # Анализ различающихся черт
        for species in species_data:
            distinguishing_features[species.species_name] = {}
            row = {'species': species.species_name}
            
            for char in compared_chars:
                value = species.physiology.get(char, 'Не указано')
                distinguishing_features[species.species_name][char] = value
                row[char] = value
            
            summary_table.append(row)
        
        # Формируем ответ
        formatted_response = self._format_physiological_response(
            species_data, common_features, distinguishing_features, summary_table
        )
        
        return ComparativeReport(
            query_type="physiological",
            species_count=len(species_data),
            compared_characteristics=compared_chars,
            common_features=common_features,
            distinguishing_features=distinguishing_features,
            summary_table=summary_table,
            formatted_response=formatted_response
        )
    
    def _compare_ecology(self, species_data: List[SpeciesData], query: str) -> ComparativeReport:
        """Сравнивает экологические характеристики"""
        compared_chars = ['habitat', 'isolation_source', 'geographic_origin']
        
        # Собираем общие черты
        common_features = {}
        distinguishing_features = {}
        summary_table = []
        
        # Анализ общих черт
        for char in compared_chars:
            values = []
            for species in species_data:
                if char in species.ecology:
                    values.append(species.ecology[char])
            
            if values and len(set(values)) == 1:  # Все одинаковые
                common_features[char] = values[0]
        
        # Анализ различающихся черт
        for species in species_data:
            distinguishing_features[species.species_name] = {}
            row = {'species': species.species_name}
            
            for char in compared_chars:
                value = species.ecology.get(char, 'Не указано')
                distinguishing_features[species.species_name][char] = value
                row[char] = value
            
            summary_table.append(row)
        
        # Формируем ответ
        formatted_response = self._format_ecological_response(
            species_data, common_features, distinguishing_features, summary_table
        )
        
        return ComparativeReport(
            query_type="ecological",
            species_count=len(species_data),
            compared_characteristics=compared_chars,
            common_features=common_features,
            distinguishing_features=distinguishing_features,
            summary_table=summary_table,
            formatted_response=formatted_response
        )
    
    def _general_comparison(self, species_data: List[SpeciesData], query: str) -> ComparativeReport:
        """Общее сравнение всех характеристик"""
        # Используем все доступные характеристики
        all_chars = ['cell_shape', 'cell_size', 'gram_stain', 'motility', 'colony_color', 
                    'temperature', 'ph_range', 'habitat', 'isolation_source']
        
        # Собираем данные из всех категорий
        common_features = {}
        distinguishing_features = {}
        summary_table = []
        
        for species in species_data:
            distinguishing_features[species.species_name] = {}
            row = {'species': species.species_name}
            
            # Объединяем все характеристики
            all_characteristics = {**species.morphology, **species.physiology, **species.ecology}
            
            for char in all_chars:
                value = all_characteristics.get(char, 'Не указано')
                distinguishing_features[species.species_name][char] = value
                row[char] = value
            
            summary_table.append(row)
        
        # Формируем ответ
        formatted_response = self._format_general_response(
            species_data, common_features, distinguishing_features, summary_table
        )
        
        return ComparativeReport(
            query_type="general",
            species_count=len(species_data),
            compared_characteristics=all_chars,
            common_features=common_features,
            distinguishing_features=distinguishing_features,
            summary_table=summary_table,
            formatted_response=formatted_response
        )
    
    def _create_no_data_response(self, query_type: str) -> ComparativeReport:
        """Создает ответ при отсутствии данных"""
        return ComparativeReport(
            query_type=query_type,
            species_count=0,
            compared_characteristics=[],
            common_features={},
            distinguishing_features={},
            summary_table=[],
            formatted_response="К сожалению, в предоставленном контексте недостаточно данных для сравнительного анализа видов Lysobacter."
        )

# Тестирование
if __name__ == "__main__":
    analyzer = ComparativeAnalyzer()
    
    # Тестовый контекст
    test_context = """
    Lysobacter capsici штамм YC5194 - палочковидные клетки размером 0.3-0.5 × 2.0-20 мкм, грам-отрицательные, подвижные.
    Lysobacter antarcticus штамм GW1-59T - палочковидные клетки 0.6-0.8 × 0.7-1.7 мкм, грам-отрицательные, неподвижные, желтые колонии.
    """
    
    query = "Сравните морфологические характеристики различных лизобактерий"
    result = analyzer.analyze_comparative_query(test_context, query)
    
    print("🧪 ТЕСТ СРАВНИТЕЛЬНОГО АНАЛИЗАТОРА")
    print("=" * 50)
    print(result.formatted_response) 