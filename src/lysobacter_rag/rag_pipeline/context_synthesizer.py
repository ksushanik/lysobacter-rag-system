"""
Модуль для синтеза контекста в стиле NotebookLM
Объединяет разрозненную информацию в связное научное повествование
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class FactExtraction:
    """Извлеченный факт с метаданными"""
    category: str  # морфология, биохимия, геном и т.д.
    subcategory: str  # размер клеток, ферменты и т.д.
    value: str  # конкретное значение
    unit: Optional[str]  # единица измерения
    source_id: str  # идентификатор источника
    confidence: float  # уверенность в извлечении
    
@dataclass
class ContextStructure:
    """Структурированный контекст для ответа"""
    origin_info: Dict[str, Any]  # происхождение и изоляция
    morphology: Dict[str, Any]  # морфологические характеристики
    physiology: Dict[str, Any]  # физиологические условия
    biochemistry: Dict[str, Any]  # биохимические свойства
    chemotaxonomy: Dict[str, Any]  # хемотаксономия
    genomics: Dict[str, Any]  # геномные характеристики
    ecology: Dict[str, Any]  # экологическая информация
    methodology: Dict[str, Any]  # методы исследования

class ContextSynthesizer:
    """Синтезатор контекста в стиле NotebookLM"""
    
    def __init__(self):
        """Инициализация синтезатора"""
        self.fact_extractors = self._initialize_extractors()
        self.category_weights = self._initialize_weights()
    
    def _initialize_extractors(self) -> Dict[str, Dict]:
        """Инициализирует извлекатели фактов по категориям"""
        return {
            "origin": {
                "patterns": [
                    r"изолирован[а-я]* из ([^.]+)",
                    r"выделен[а-я]* из ([^.]+)",
                    r"источник[:\s]*([^.]+)",
                    r"место выделения[:\s]*([^.]+)",
                    r"депозитарн[а-я]* номер[а-я]*[:\s]*([A-Z0-9\s=,T]+)"
                ],
                "keywords": ["изоляция", "выделение", "источник", "место", "депозитарный", "номер"]
            },
            "morphology": {
                "patterns": [
                    r"размер[а-я]*[:\s]*([0-9.,–-]+\s*[мкμµ]м)",
                    r"форма[:\s]*([а-я]+)",
                    r"грам[- ]?(положительн|отрицательн)[а-я]*",
                    r"колони[а-я]*[:\s]*([^.]+)",
                    r"цвет[:\s]*([а-я]+)"
                ],
                "keywords": ["размер", "форма", "грам", "колонии", "цвет", "морфология"]
            },
            "physiology": {
                "patterns": [
                    r"температур[а-я]*[:\s]*([0-9–-]+)\s*°?C",
                    r"pH[:\s]*([0-9.,–-]+)",
                    r"NaCl[:\s]*([0-9.,–-]+)\s*%",
                    r"аэробн[а-я]*|анаэробн[а-я]*",
                    r"среда[:\s]*([^.]+)"
                ],
                "keywords": ["температура", "pH", "NaCl", "аэробный", "анаэробный", "среда"]
            },
            "biochemistry": {
                "patterns": [
                    r"каталаза[:\s]*(положительн|отрицательн)[а-я]*",
                    r"оксидаза[:\s]*(положительн|отрицательн)[а-я]*",
                    r"фермент[а-я]*[:\s]*([^.]+)",
                    r"гидролиз[:\s]*([^.]+)",
                    r"утилизаци[а-я]*[:\s]*([^.]+)"
                ],
                "keywords": ["каталаза", "оксидаза", "фермент", "гидролиз", "утилизация"]
            },
            "chemotaxonomy": {
                "patterns": [
                    r"Q-([0-9]+)",
                    r"хинон[:\s]*([^.]+)",
                    r"жирн[а-я]* кислот[а-я]*[:\s]*([^.]+)",
                    r"iso-C([0-9:]+)",
                    r"G\+C[:\s]*([0-9.,]+)\s*%"
                ],
                "keywords": ["хинон", "жирные кислоты", "липиды", "G+C", "мол"]
            },
            "genomics": {
                "patterns": [
                    r"геном[а-я]*[:\s]*([0-9.,]+)\s*(Mb|п\.н\.|bp)",
                    r"ANI[:\s]*([0-9.,]+)\s*%",
                    r"16S рРНК[:\s]*([0-9.,]+)\s*%",
                    r"ген[а-я]*[:\s]*([0-9]+)",
                    r"CDS[:\s]*([0-9]+)"
                ],
                "keywords": ["геном", "ANI", "16S", "рРНК", "гены", "CDS"]
            }
        }
    
    def _initialize_weights(self) -> Dict[str, float]:
        """Инициализирует веса важности категорий"""
        return {
            "origin": 1.0,  # происхождение очень важно
            "morphology": 0.9,
            "physiology": 0.8,
            "biochemistry": 0.7,
            "chemotaxonomy": 0.8,
            "genomics": 0.9,
            "ecology": 0.6,
            "methodology": 0.5
        }
    
    def synthesize_for_notebooklm_style(self, text_chunks: List[str], query: str) -> str:
        """Синтезирует контекст в стиле NotebookLM"""
        facts = self.extract_facts(text_chunks)
        context = self.synthesize_context(text_chunks, [])
        
        # Создаем связное повествование
        narrative_parts = []
        
        # Заголовок в стиле NotebookLM
        strain_name = self._extract_strain_name(query, text_chunks)
        narrative_parts.append(f"## Штамм {strain_name}")
        
        # Происхождение и контекст
        if context.origin_info.get("isolation_source"):
            narrative_parts.append(f"\nЭтот бактериальный штамм был изолирован из {context.origin_info['isolation_source'][0]}.")
        
        # Таксономическая информация
        narrative_parts.append(f"\n### Таксономическая классификация")
        narrative_parts.append(f"Штамм {strain_name} представляет собой грам-отрицательную бактерию рода Lysobacter.")
        
        # Морфология
        if context.morphology.get("cell_size"):
            size_info = context.morphology["cell_size"][0]
            narrative_parts.append(f"\n### Морфологические характеристики")
            narrative_parts.append(f"Клетки имеют палочковидную форму с размерами {size_info}.")
        
        # Физиологические условия
        if any(context.physiology.values()):
            narrative_parts.append(f"\n### Условия роста")
            
            conditions = []
            if context.physiology.get("temperature"):
                conditions.append(f"температуре {context.physiology['temperature'][0]}")
            if context.physiology.get("ph"):
                conditions.append(f"pH {context.physiology['ph'][0]}")
            if context.physiology.get("salinity"):
                conditions.append(f"концентрации NaCl {context.physiology['salinity'][0]}")
            
            if conditions:
                narrative_parts.append(f"Оптимальный рост наблюдается при {', '.join(conditions)}.")
        
        # Биохимические характеристики
        if context.biochemistry.get("enzyme_tests"):
            narrative_parts.append(f"\n### Биохимические свойства")
            for test in context.biochemistry["enzyme_tests"][:3]:
                narrative_parts.append(f"- {test}")
        
        # Хемотаксономия
        if any(context.chemotaxonomy.values()):
            narrative_parts.append(f"\n### Хемотаксономические характеристики")
            
            if context.chemotaxonomy.get("quinones"):
                narrative_parts.append(f"Основной респираторный хинон: {context.chemotaxonomy['quinones'][0]}.")
            
            if context.chemotaxonomy.get("gc_content"):
                narrative_parts.append(f"Содержание G+C: {context.chemotaxonomy['gc_content'][0]}.")
        
        # Геномные характеристики
        if context.genomics.get("genome_size"):
            narrative_parts.append(f"\n### Геномные характеристики")
            narrative_parts.append(f"Размер генома составляет {context.genomics['genome_size'][0]}.")
        
        return "\n".join(narrative_parts)
    
    def _extract_strain_name(self, query: str, text_chunks: List[str]) -> str:
        """Извлекает название штамма"""
        # Ищем в запросе
        strain_patterns = [
            r"штамм[е]?\s+([A-Za-z0-9-]+T?)",
            r"([A-Za-z0-9-]+T)\b"
        ]
        
        for pattern in strain_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Ищем в тексте
        for chunk in text_chunks:
            for pattern in strain_patterns:
                match = re.search(pattern, chunk, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return "неизвестный"
    
    def extract_facts(self, text_chunks: List[str]) -> List[FactExtraction]:
        """Извлекает структурированные факты из текстовых фрагментов"""
        facts = []
        
        for chunk_idx, chunk in enumerate(text_chunks):
            chunk_lower = chunk.lower()
            
            for category, config in self.fact_extractors.items():
                # Извлечение по паттернам
                for pattern in config["patterns"]:
                    matches = re.finditer(pattern, chunk, re.IGNORECASE | re.UNICODE)
                    for match in matches:
                        fact = FactExtraction(
                            category=category,
                            subcategory=self._determine_subcategory(pattern, match.group()),
                            value=match.group(1) if match.groups() else match.group(),
                            unit=self._extract_unit(match.group()),
                            source_id=f"chunk_{chunk_idx}",
                            confidence=self._calculate_confidence(match.group(), chunk)
                        )
                        facts.append(fact)
                
                # Извлечение по ключевым словам
                for keyword in config["keywords"]:
                    if keyword in chunk_lower:
                        context = self._extract_context_around_keyword(chunk, keyword)
                        if context:
                            fact = FactExtraction(
                                category=category,
                                subcategory=keyword,
                                value=context,
                                unit=None,
                                source_id=f"chunk_{chunk_idx}",
                                confidence=0.7
                            )
                            facts.append(fact)
        
        return self._deduplicate_facts(facts)
    
    def _determine_subcategory(self, pattern: str, text: str) -> str:
        """Определяет подкатегорию на основе паттерна"""
        if "размер" in pattern:
            return "cell_size"
        elif "температур" in pattern:
            return "temperature"
        elif "pH" in pattern:
            return "ph_range"
        elif "каталаза" in pattern:
            return "catalase"
        elif "оксидаза" in pattern:
            return "oxidase"
        elif "геном" in pattern:
            return "genome_size"
        else:
            return "general"
    
    def _extract_unit(self, text: str) -> Optional[str]:
        """Извлекает единицу измерения"""
        unit_patterns = [
            r"([мкμµ]м|mm|nm)",
            r"(°C|C)",
            r"(%|процент)",
            r"(Mb|Gb|kb|п\.н\.|bp)",
            r"(мол\.%|mol%)"
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_confidence(self, extracted_value: str, context: str) -> float:
        """Вычисляет уверенность в извлеченном факте"""
        confidence = 0.5  # базовая уверенность
        
        # Увеличиваем уверенность за численные значения
        if re.search(r'\d+', extracted_value):
            confidence += 0.2
        
        # Увеличиваем за единицы измерения
        if self._extract_unit(extracted_value):
            confidence += 0.1
        
        # Увеличиваем за научные термины
        scientific_terms = ["штамм", "типовой", "депозитарный", "номер"]
        for term in scientific_terms:
            if term in context.lower():
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_context_around_keyword(self, text: str, keyword: str, window: int = 50) -> str:
        """Извлекает контекст вокруг ключевого слова"""
        keyword_pos = text.lower().find(keyword.lower())
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - window)
        end = min(len(text), keyword_pos + len(keyword) + window)
        
        return text[start:end].strip()
    
    def _deduplicate_facts(self, facts: List[FactExtraction]) -> List[FactExtraction]:
        """Удаляет дублирующиеся факты"""
        seen = set()
        unique_facts = []
        
        for fact in facts:
            key = (fact.category, fact.subcategory, fact.value.lower().strip())
            if key not in seen:
                seen.add(key)
                unique_facts.append(fact)
        
        return unique_facts
    
    def synthesize_context(self, text_chunks: List[str], metadata: List[Dict]) -> ContextStructure:
        """Синтезирует структурированный контекст из фрагментов"""
        facts = self.extract_facts(text_chunks)
        
        # Группируем факты по категориям
        categorized_facts = defaultdict(list)
        for fact in facts:
            categorized_facts[fact.category].append(fact)
        
        # Создаем структурированный контекст
        context = ContextStructure(
            origin_info=self._build_origin_info(categorized_facts.get("origin", [])),
            morphology=self._build_morphology_info(categorized_facts.get("morphology", [])),
            physiology=self._build_physiology_info(categorized_facts.get("physiology", [])),
            biochemistry=self._build_biochemistry_info(categorized_facts.get("biochemistry", [])),
            chemotaxonomy=self._build_chemotaxonomy_info(categorized_facts.get("chemotaxonomy", [])),
            genomics=self._build_genomics_info(categorized_facts.get("genomics", [])),
            ecology={},
            methodology={}
        )
        
        return context
    
    def _build_origin_info(self, facts: List[FactExtraction]) -> Dict[str, Any]:
        """Строит информацию о происхождении"""
        info = {
            "isolation_source": [],
            "geographic_location": [],
            "depositories": [],
            "isolation_method": []
        }
        
        for fact in facts:
            if "изолирован" in fact.value or "выделен" in fact.value:
                info["isolation_source"].append(fact.value)
            elif any(geo in fact.value.lower() for geo in ["китай", "монголия", "япония", "корея"]):
                info["geographic_location"].append(fact.value)
            elif any(dep in fact.value for dep in ["CGMCC", "KCTC", "DSM", "ATCC"]):
                info["depositories"].append(fact.value)
        
        return info
    
    def _build_morphology_info(self, facts: List[FactExtraction]) -> Dict[str, Any]:
        """Строит морфологическую информацию"""
        info = {
            "cell_size": [],
            "cell_shape": [],
            "gram_stain": [],
            "colony_description": [],
            "pigmentation": []
        }
        
        for fact in facts:
            if fact.subcategory == "cell_size" or "мкм" in fact.value:
                info["cell_size"].append(fact.value)
            elif "палочк" in fact.value or "кокк" in fact.value:
                info["cell_shape"].append(fact.value)
            elif "грам" in fact.value.lower():
                info["gram_stain"].append(fact.value)
        
        return info
    
    def _build_physiology_info(self, facts: List[FactExtraction]) -> Dict[str, Any]:
        """Строит физиологическую информацию"""
        info = {
            "temperature": [],
            "ph": [],
            "salinity": [],
            "oxygen_requirements": [],
            "growth_media": []
        }
        
        for fact in facts:
            if fact.subcategory == "temperature" or "°C" in fact.value:
                info["temperature"].append(fact.value)
            elif fact.subcategory == "ph_range" or "pH" in fact.value:
                info["ph"].append(fact.value)
            elif "NaCl" in fact.value or "%" in fact.value:
                info["salinity"].append(fact.value)
        
        return info
    
    def _build_biochemistry_info(self, facts: List[FactExtraction]) -> Dict[str, Any]:
        """Строит биохимическую информацию"""
        info = {
            "enzyme_tests": [],
            "substrate_utilization": [],
            "metabolic_pathways": []
        }
        
        for fact in facts:
            if fact.subcategory in ["catalase", "oxidase"] or "фермент" in fact.value:
                info["enzyme_tests"].append(fact.value)
            elif "утилизация" in fact.value or "гидролиз" in fact.value:
                info["substrate_utilization"].append(fact.value)
        
        return info
    
    def _build_chemotaxonomy_info(self, facts: List[FactExtraction]) -> Dict[str, Any]:
        """Строит хемотаксономическую информацию"""
        info = {
            "quinones": [],
            "fatty_acids": [],
            "polar_lipids": [],
            "gc_content": []
        }
        
        for fact in facts:
            if "Q-" in fact.value or "хинон" in fact.value:
                info["quinones"].append(fact.value)
            elif "iso-C" in fact.value or "жирн" in fact.value:
                info["fatty_acids"].append(fact.value)
            elif "G+C" in fact.value or "мол%" in fact.value:
                info["gc_content"].append(fact.value)
        
        return info
    
    def _build_genomics_info(self, facts: List[FactExtraction]) -> Dict[str, Any]:
        """Строит геномную информацию"""
        info = {
            "genome_size": [],
            "ani_values": [],
            "rrna_similarity": [],
            "gene_counts": []
        }
        
        for fact in facts:
            if fact.subcategory == "genome_size" or any(unit in fact.value for unit in ["Mb", "п.н.", "bp"]):
                info["genome_size"].append(fact.value)
            elif "ANI" in fact.value:
                info["ani_values"].append(fact.value)
            elif "16S" in fact.value:
                info["rrna_similarity"].append(fact.value)
        
        return info 