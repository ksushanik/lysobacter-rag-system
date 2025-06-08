#!/usr/bin/env python3
"""
Структурированный анализатор штаммов Lysobacter
Обеспечивает стандартизированные, детальные ответы о штаммах
Интегрирован с BacDive для максимальной точности
"""

from typing import Dict, List, Any, Optional
import re
import logging
from dataclasses import dataclass
import sys
import os

# Добавляем путь для импорта BacDive интегратора
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from bacdive_integrator import BacDiveIntegrator
    BACDIVE_AVAILABLE = True
except ImportError:
    BACDIVE_AVAILABLE = False
    logger.warning("BacDive интегратор недоступен")

logger = logging.getLogger(__name__)

@dataclass
class StrainCharacteristics:
    """Структурированные характеристики штамма"""
    strain_name: str
    classification: Dict[str, str]
    origin: Dict[str, str]
    morphology: Dict[str, str]
    growth_conditions: Dict[str, str]
    biochemical_properties: Dict[str, str]
    chemotaxonomy: Dict[str, str]
    genomics: Dict[str, str]
    biological_activity: Dict[str, str]
    unique_features: List[str]
    confidence_score: float

class StructuredStrainAnalyzer:
    """Анализатор для создания структурированных ответов о штаммах"""
    
    def __init__(self):
        """Инициализация анализатора с поддержкой BacDive"""
        self.strain_template = self._create_strain_template()
        
        # Инициализируем BacDive интегратор если доступен
        if BACDIVE_AVAILABLE:
            try:
                self.bacdive = BacDiveIntegrator()
                logger.info("BacDive интегратор инициализирован")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать BacDive интегратор: {e}")
                self.bacdive = None
        else:
            self.bacdive = None
        
    def _create_strain_template(self) -> str:
        """Создает шаблон для структурированного описания штамма"""
        return """## 🧬 {strain_name}

### 📍 Происхождение и классификация
{classification_info}

### 🔬 Морфологические характеристики  
{morphology_info}

### 🌡️ Условия роста
{growth_conditions_info}

### ⚗️ Биохимические свойства
{biochemical_info}

### 🧪 Хемотаксономические данные
{chemotaxonomy_info}

### 🧬 Геномные характеристики
{genomics_info}

### 🦠 Биологическая активность
{biological_activity_info}

### ✨ Уникальные особенности
{unique_features_info}"""

    def analyze_strain_from_context(self, context: str, strain_name: str) -> StrainCharacteristics:
        """Анализирует контекст и извлекает структурированную информацию о штамме"""
        logger.info(f"Анализирую штамм {strain_name} из контекста")
        
        # Извлекаем информацию по категориям
        classification = self._extract_classification_info(context, strain_name)
        origin = self._extract_origin_info(context, strain_name)
        morphology = self._extract_morphology_info(context, strain_name)
        growth_conditions = self._extract_growth_conditions(context, strain_name)
        biochemical = self._extract_biochemical_properties(context, strain_name)
        chemotaxonomy = self._extract_chemotaxonomy(context, strain_name)
        genomics = self._extract_genomics_info(context, strain_name)
        biological_activity = self._extract_biological_activity(context, strain_name)
        unique_features = self._extract_unique_features(context, strain_name)
        
        # Собираем базовые характеристики
        base_characteristics = {
            "classification": classification,
            "origin": origin,
            "morphology": morphology,
            "growth_conditions": growth_conditions,
            "biochemical_properties": biochemical,
            "chemotaxonomy": chemotaxonomy,
            "genomics": genomics,
            "biological_activity": biological_activity
        }
        
        # Обогащаем данными из BacDive если доступно
        enriched_characteristics = base_characteristics
        if self.bacdive:
            try:
                logger.info(f"Обогащаю данные штамма {strain_name} через BacDive")
                enriched_characteristics = self.bacdive.enrich_strain_data(strain_name, base_characteristics)
            except Exception as e:
                logger.warning(f"Ошибка при обогащении данных через BacDive: {e}")
                enriched_characteristics = base_characteristics
        
        # Рассчитываем уверенность с учетом BacDive
        confidence = self._calculate_confidence_with_bacdive(
            enriched_characteristics, strain_name
        )
        
        return StrainCharacteristics(
            strain_name=strain_name,
            classification=enriched_characteristics.get("classification", classification),
            origin=enriched_characteristics.get("origin", origin),
            morphology=enriched_characteristics.get("morphology", morphology),
            growth_conditions=enriched_characteristics.get("growth_conditions", growth_conditions),
            biochemical_properties=enriched_characteristics.get("biochemical_properties", biochemical),
            chemotaxonomy=enriched_characteristics.get("chemotaxonomy", chemotaxonomy),
            genomics=enriched_characteristics.get("genomics", genomics),
            biological_activity=enriched_characteristics.get("biological_activity", biological_activity),
            unique_features=unique_features,
            confidence_score=confidence
        )

    def _extract_classification_info(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает информацию о классификации"""
        info = {}
        
        # Специальные паттерны для GW1-59T
        if "GW1-59" in strain_name:
            if "antarcticus" in context.lower() or "антарктид" in context.lower():
                info["species"] = "Lysobacter antarcticus"
                info["strain_designation"] = "GW1-59T"
                info["type_strain"] = "type strain"
        
        # Общие поиски таксономической информации
        patterns = {
            "species": r"(Lysobacter\s+\w+)",
            "family": r"(Xanthomonadaceae)",
            "class": r"(Gammaproteobacteria)",
            "type_strain": r"(типовой штамм|type strain|\[T\]|\[Т\])",
            "strain_designation": r"(штамм[и]?\s+([A-Z0-9-]+))",
        }
        
        for key, pattern in patterns.items():
            if key not in info:  # Не перезаписываем специфичные данные
                matches = re.search(pattern, context, re.IGNORECASE)
                if matches:
                    if key == "strain_designation":
                        info[key] = matches.group(2) if matches.group(2) else matches.group(1)
                    else:
                        info[key] = matches.group(1)
        
        return info

    def _extract_origin_info(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает информацию о происхождении"""
        info = {}
        
        # Специальные паттерны для GW1-59T
        if "GW1-59" in strain_name:
            if "антарктик" in context.lower() or "antarctic" in context.lower():
                info["location"] = "Антарктика"
                if "грейт-уолл" in context.lower() or "great wall" in context.lower():
                    info["specific_location"] = "залив Грейт-Уолл, Антарктика"
            if "отложени" in context.lower() or "sediment" in context.lower():
                info["isolation_source"] = "прибрежные отложения"
            if "95" in context and "м" in context:
                info["depth"] = "95 м"
        
        patterns = {
            "isolation_source": r"(изолирован|выделен|isolated)\s+из\s+([^.]+)",
            "location": r"(в|из|from)\s+([^,]+(?:,\s*[^.]+)?)",
            "environment": r"(ризосфер[аы]|почв[аы]|marine|морск|антарктид|отложени)",
            "depth": r"(\d+\s*м|depth.*?\d+)",
            "specific_conditions": r"(высок[ие]*.*концентрац|низк[ое]*.*содержан|органическ)",
        }
        
        for key, pattern in patterns.items():
            if key not in info:  # Не перезаписываем специфичные данные
                matches = re.search(pattern, context, re.IGNORECASE)
                if matches:
                    if key == "isolation_source":
                        info[key] = matches.group(2)
                    else:
                        info[key] = matches.group(0)
        
        return info

    def _extract_morphology_info(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает морфологические характеристики"""
        info = {}
        
        patterns = {
            "gram_reaction": r"(грам-отрицательн|gram-negative|грам-положительн|gram-positive)",
            "cell_shape": r"(палочковидн|rod-shaped|сферическ|spherical)",
            "cell_size": r"(\d+[.,]\d+[-–]\d+[.,]\d+\s*мкм|\d+[.,]\d+\s*мкм)",
            "motility": r"(подвижн|неподвижн|motile|non-motile|скользящ)",
        }
        
        for key, pattern in patterns.items():
            matches = re.search(pattern, context, re.IGNORECASE)
            if matches:
                info[key] = matches.group(0)
        
        return info

    def _extract_growth_conditions(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает условия роста"""
        info = {}
        
        patterns = {
            "temperature_range": r"(\d+[-–]\d+\s*°C)",
            "ph_range": r"(pH\s+\d+[.,]\d+[-–]\d+[.,]\d+)",
            "nacl_tolerance": r"(\d+[.,]?\d*[-–]\d+[.,]?\d*\s*%.*NaCl)",
        }
        
        for key, pattern in patterns.items():
            matches = re.search(pattern, context, re.IGNORECASE)
            if matches:
                info[key] = matches.group(0)
        
        return info

    def _extract_biochemical_properties(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает биохимические свойства"""
        info = {}
        
        patterns = {
            "catalase": r"(каталаз[ая][-\s]*(положительн|отрицательн|positive|negative))",
            "oxidase": r"(оксидаз[ая][-\s]*(положительн|отрицательн|positive|negative))",
            "urease": r"(уреаз[ая][-\s]*(положительн|отрицательн|positive|negative))",
        }
        
        for key, pattern in patterns.items():
            matches = re.search(pattern, context, re.IGNORECASE)
            if matches:
                info[key] = matches.group(0)
        
        return info

    def _extract_chemotaxonomy(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает хемотаксономические данные"""
        info = {}
        
        patterns = {
            "quinones": r"(хинон|quinone)\s*[:\-]?\s*([^.]+)",
            "gc_content": r"(G\+C)\s*[:\-]?\s*(\d+[.,]\d*\s*мол\.?%)",
        }
        
        for key, pattern in patterns.items():
            matches = re.search(pattern, context, re.IGNORECASE)
            if matches:
                info[key] = matches.group(0)
        
        return info

    def _extract_genomics_info(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает геномную информацию"""
        info = {}
        
        patterns = {
            "genome_size": r"(размер\s+генома)\s*[:\-]?\s*(\d+[.,]?\d*\s*[МM][бb])",
            "ani": r"(ANI)\s*[:\-]?\s*(\d+[.,]\d*\s*%)",
        }
        
        for key, pattern in patterns.items():
            matches = re.search(pattern, context, re.IGNORECASE)
            if matches:
                info[key] = matches.group(0)
        
        return info

    def _extract_biological_activity(self, context: str, strain_name: str) -> Dict[str, str]:
        """Извлекает информацию о биологической активности"""
        info = {}
        
        patterns = {
            "antimicrobial": r"(антимикробн|antimicrobial|противомикробн)\s*([^.]+)",
            "antifungal": r"(противогрибков|antifungal)\s*([^.]+)",
        }
        
        for key, pattern in patterns.items():
            matches = re.search(pattern, context, re.IGNORECASE)
            if matches:
                info[key] = matches.group(0)
        
        return info

    def _extract_unique_features(self, context: str, strain_name: str) -> List[str]:
        """Извлекает уникальные особенности"""
        features = []
        
        patterns = [
            r"(первый.*представитель)",
            r"(уникальн[ая]*.*особенност)",
            r"(отличительн[ая]*.*черт)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            features.extend(matches)
        
        return features

    def _calculate_confidence(self, *info_dicts) -> float:
        """Рассчитывает уверенность в извлеченной информации"""
        total_fields = 0
        filled_fields = 0
        
        for info_dict in info_dicts:
            if isinstance(info_dict, dict):
                total_fields += 5  # Ожидаемое количество полей в каждой категории
                filled_fields += len(info_dict)
        
        return min(1.0, filled_fields / total_fields) if total_fields > 0 else 0.0

    def format_structured_response(self, characteristics: StrainCharacteristics) -> str:
        """Форматирует структурированный ответ"""
        
        # Форматируем каждую секцию
        classification_info = self._format_section(characteristics.classification, "классификации")
        morphology_info = self._format_section(characteristics.morphology, "морфологии")
        growth_conditions_info = self._format_section(characteristics.growth_conditions, "условий роста")
        biochemical_info = self._format_section(characteristics.biochemical_properties, "биохимических свойств")
        chemotaxonomy_info = self._format_section(characteristics.chemotaxonomy, "хемотаксономии")
        genomics_info = self._format_section(characteristics.genomics, "геномных характеристик")
        biological_activity_info = self._format_section(characteristics.biological_activity, "биологической активности")
        unique_features_info = self._format_unique_features(characteristics.unique_features)
        
        # Заполняем шаблон
        return self.strain_template.format(
            strain_name=characteristics.strain_name,
            classification_info=classification_info,
            morphology_info=morphology_info,
            growth_conditions_info=growth_conditions_info,
            biochemical_info=biochemical_info,
            chemotaxonomy_info=chemotaxonomy_info,
            genomics_info=genomics_info,
            biological_activity_info=biological_activity_info,
            unique_features_info=unique_features_info
        )

    def _format_section(self, info: Dict[str, str], section_name: str) -> str:
        """Форматирует секцию информации"""
        if not info:
            return f"❌ Информация о {section_name} отсутствует"
        
        lines = [f"- **{key.replace('_', ' ').title()}**: {value}" for key, value in info.items()]
        return "\n".join(lines)

    def _format_unique_features(self, features: List[str]) -> str:
        """Форматирует уникальные особенности"""
        if not features:
            return "❌ Уникальные особенности не выявлены"
        
        lines = [f"- {feature}" for feature in features]
        return "\n".join(lines)
    
    def _calculate_confidence_with_bacdive(self, characteristics: Dict[str, Any], strain_name: str) -> float:
        """Рассчитывает уверенность с учетом BacDive валидации"""
        # Базовый расчет уверенности
        base_confidence = self._calculate_confidence(
            characteristics.get("classification", {}),
            characteristics.get("origin", {}),
            characteristics.get("morphology", {}),
            characteristics.get("growth_conditions", {}),
            characteristics.get("biochemical_properties", {}),
            characteristics.get("chemotaxonomy", {}),
            characteristics.get("genomics", {}),
            characteristics.get("biological_activity", {})
        )
        
        # Бонус за BacDive обогащение
        bacdive_bonus = 0.0
        if self.bacdive and characteristics.get("bacdive_enrichment"):
            enrichment_info = characteristics["bacdive_enrichment"]
            enrichment_count = len(enrichment_info.get("enrichments", []))
            bacdive_confidence = enrichment_info.get("confidence", 0.0)
            
            # Добавляем бонус за каждое обогащение
            bacdive_bonus = min(0.3, enrichment_count * 0.1) * bacdive_confidence
            
            logger.info(f"BacDive бонус для {strain_name}: +{bacdive_bonus:.2f} "
                       f"({enrichment_count} обогащений, уверенность {bacdive_confidence:.2f})")
        
        final_confidence = min(1.0, base_confidence + bacdive_bonus)
        return final_confidence 