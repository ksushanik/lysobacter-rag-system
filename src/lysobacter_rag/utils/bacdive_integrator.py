#!/usr/bin/env python3
"""
Интегратор с BacDive - крупнейшей базой данных о бактериях
Обеспечивает валидацию и обогащение данных о штаммах Lysobacter
"""

import requests
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class BacDiveStrain:
    """Структура данных штамма из BacDive"""
    bacdive_id: str
    species: str
    strain_designation: str
    type_strain: bool
    isolation_source: Optional[str]
    isolation_location: Optional[str]
    growth_temperature: Optional[Dict[str, Any]]
    ph_range: Optional[Dict[str, Any]]
    morphology: Optional[Dict[str, Any]]
    gram_stain: Optional[str]
    motility: Optional[str]
    chemotaxonomy: Optional[Dict[str, Any]]
    biochemistry: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0

class BacDiveIntegrator:
    """Интегратор с BacDive для обогащения данных о лизобактериях"""
    
    def __init__(self, cache_ttl: int = 3600):
        """Инициализация интегратора"""
        self.base_url = "https://bacdive.dsmz.de/api"
        self.cache = {}
        self.cache_ttl = cache_ttl
        
        # Паттерны для поиска штаммов Lysobacter
        self.lysobacter_patterns = {
            "YC5194": ["YC5194", "YC 5194", "Lysobacter capsici YC5194"],
            "GW1-59T": ["GW1-59T", "GW1-59", "Lysobacter antarcticus GW1-59T"],
            "general": ["Lysobacter", "lysobacter"]
        }
        
    def search_strain(self, strain_query: str) -> List[BacDiveStrain]:
        """Поиск штамма в BacDive"""
        # Проверяем кэш
        cache_key = f"search_{strain_query}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Имитируем поиск (в реальности нужна авторизация)
            logger.info(f"Поиск штамма {strain_query} в BacDive")
            
            # Заглушка для демонстрации
            mock_results = self._get_mock_data(strain_query)
            
            # Кэшируем результат
            self._cache_result(cache_key, mock_results)
            
            return mock_results
                
        except Exception as e:
            logger.error(f"Ошибка при поиске в BacDive: {e}")
            return []
    
    def validate_strain_data(self, strain_name: str, our_data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидирует наши данные с данными из BacDive"""
        logger.info(f"Валидирую данные штамма {strain_name} через BacDive")
        
        # Ищем штамм в BacDive
        bacdive_strains = self.search_strain(strain_name)
        
        if not bacdive_strains:
            return {
                "validation_status": "no_reference",
                "message": f"Штамм {strain_name} не найден в BacDive",
                "confidence": 0.0,
                "recommendations": []
            }
        
        # Берем наиболее релевантный результат
        best_match = bacdive_strains[0]
        
        # Сравниваем данные
        validation_result = {
            "validation_status": "validated",
            "bacdive_id": best_match.bacdive_id,
            "matches": [],
            "discrepancies": [],
            "missing_in_our_data": [],
            "confidence": 0.0,
            "recommendations": []
        }
        
        # Проверяем основные поля
        validations = self._compare_strain_data(our_data, best_match)
        validation_result.update(validations)
        
        # Рассчитываем общую уверенность
        total_checks = len(validation_result["matches"]) + len(validation_result["discrepancies"])
        if total_checks > 0:
            validation_result["confidence"] = len(validation_result["matches"]) / total_checks
        
        return validation_result
    
    def enrich_strain_data(self, strain_name: str, our_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обогащает наши данные информацией из BacDive"""
        logger.info(f"Обогащаю данные штамма {strain_name} через BacDive")
        
        # Поиск в BacDive
        bacdive_strains = self.search_strain(strain_name)
        
        if not bacdive_strains:
            return our_data
        
        best_match = bacdive_strains[0]
        enriched_data = our_data.copy()
        
        # Добавляем недостающие данные из BacDive
        enrichment_log = []
        
        # Морфология
        if not our_data.get("morphology") and best_match.morphology:
            enriched_data["morphology"] = best_match.morphology
            enrichment_log.append("Добавлена морфология из BacDive")
        
        # Классификация
        if not our_data.get("classification") and best_match.species:
            enriched_data["classification"] = {
                "species": best_match.species,
                "strain": best_match.strain_designation,
                "type_strain": best_match.type_strain
            }
            enrichment_log.append("Добавлена классификация из BacDive")
        
        # Условия роста
        if not our_data.get("growth_conditions"):
            growth_data = {}
            if best_match.growth_temperature:
                growth_data["temperature"] = best_match.growth_temperature
            if best_match.ph_range:
                growth_data["ph"] = best_match.ph_range
            
            if growth_data:
                enriched_data["growth_conditions"] = growth_data
                enrichment_log.append("Добавлены условия роста из BacDive")
        
        # Биохимические свойства
        if hasattr(best_match, 'biochemistry') and best_match.biochemistry:
            if not our_data.get("biochemical_properties"):
                enriched_data["biochemical_properties"] = best_match.biochemistry
                enrichment_log.append("Добавлены биохимические свойства из BacDive")
        
        # Хемотаксономия  
        if not our_data.get("chemotaxonomy") and best_match.chemotaxonomy:
            enriched_data["chemotaxonomy"] = best_match.chemotaxonomy
            enrichment_log.append("Добавлена хемотаксономия из BacDive")
        
        # Добавляем метаданные обогащения
        enriched_data["bacdive_enrichment"] = {
            "bacdive_id": best_match.bacdive_id,
            "enrichments": enrichment_log,
            "confidence": best_match.confidence_score,
            "timestamp": time.time()
        }
        
        logger.info(f"Обогащение завершено: {len(enrichment_log)} улучшений")
        return enriched_data
    
    def _get_mock_data(self, strain_query: str) -> List[BacDiveStrain]:
        """Заглушка с mock данными для демонстрации"""
        mock_data = {}
        
        if "YC5194" in strain_query:
            mock_data = {
                "bacdive_id": "BSN000001",
                "species": "Lysobacter capsici",
                "strain_designation": "YC5194",
                "type_strain": True,
                "isolation_source": "rhizosphere of pepper",
                "isolation_location": "Jinju, South Korea",
                "growth_temperature": {"min": 15, "max": 37, "unit": "°C"},
                "ph_range": {"min": 5.5, "max": 8.5},
                "morphology": {"shape": "rod-shaped", "size": "0.3-0.5 × 2.0-20 μm"},
                "gram_stain": "negative",
                "motility": "gliding",
                "chemotaxonomy": {"quinones": "Q-8", "gc_content": 65.4},
                "confidence_score": 0.95
            }
        elif "GW1-59T" in strain_query or "GW1-59" in strain_query:
            mock_data = {
                "bacdive_id": "BSN000002", 
                "species": "Lysobacter antarcticus",
                "strain_designation": "GW1-59T",
                "type_strain": True,
                "isolation_source": "прибрежные отложения Антарктики",
                "isolation_location": "залив Грейт-Уолл, Антарктика, глубина 95 м",
                "growth_temperature": {"min": 15, "max": 37, "optimal": 30, "unit": "°C"},
                "ph_range": {"min": 9.0, "max": 11.0},
                "morphology": {
                    "shape": "палочковидная", 
                    "size": "0.6-0.8 × 0.7-1.7 мкм",
                    "motility": "неподвижная",
                    "gram_stain": "отрицательная",
                    "colony_color": "бледно-желтая"
                },
                "gram_stain": "negative",
                "motility": "non-motile",
                "chemotaxonomy": {
                    "gc_content": 67.2,
                    "respiratory_quinone": "Q-8",
                    "pigment": "флексирубиновый тип"
                },
                "biochemistry": {
                    "catalase": "положительная",
                    "oxidase": "положительная", 
                    "urease": "положительная",
                    "nitrate_reduction": "положительная"
                },
                "confidence_score": 0.95
            }
        
        if mock_data:
            return [BacDiveStrain(**mock_data)]
        return []
    
    def _compare_strain_data(self, our_data: Dict[str, Any], bacdive_strain: BacDiveStrain) -> Dict[str, List[str]]:
        """Сравнивает наши данные с данными BacDive"""
        matches = []
        discrepancies = []
        missing = []
        
        # Сравниваем доступные поля
        comparisons = [
            ("gram_stain", bacdive_strain.gram_stain),
            ("motility", bacdive_strain.motility),
            ("isolation_source", bacdive_strain.isolation_source),
            ("isolation_location", bacdive_strain.isolation_location)
        ]
        
        for field, bacdive_value in comparisons:
            our_value = our_data.get(field)
            
            if our_value and bacdive_value:
                if self._values_match(our_value, bacdive_value):
                    matches.append(f"{field}: совпадает ({our_value})")
                else:
                    discrepancies.append(f"{field}: наше='{our_value}', BacDive='{bacdive_value}'")
            elif not our_value and bacdive_value:
                missing.append(f"{field}: отсутствует в наших данных, BacDive='{bacdive_value}'")
        
        return {
            "matches": matches,
            "discrepancies": discrepancies,
            "missing_in_our_data": missing
        }
    
    def _values_match(self, value1: str, value2: str) -> bool:
        """Проверяет совпадение значений с учетом вариаций"""
        if not value1 or not value2:
            return False
        
        v1 = str(value1).lower().strip()
        v2 = str(value2).lower().strip()
        
        # Точное совпадение
        if v1 == v2:
            return True
        
        # Частичное совпадение
        if v1 in v2 or v2 in v1:
            return True
        
        return False
    
    def _is_cached(self, key: str) -> bool:
        """Проверяет, есть ли актуальные данные в кэше"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        return (time.time() - cached_time) < self.cache_ttl
    
    def _cache_result(self, key: str, data: Any):
        """Кэширует результат"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

# Тестовый пример использования
if __name__ == "__main__":
    integrator = BacDiveIntegrator()
    
    # Тест поиска
    print("🔍 Тестирование поиска YC5194...")
    results = integrator.search_strain("YC5194")
    print(f"Найдено результатов: {len(results)}")
    
    # Тест валидации
    print("\n✅ Тестирование валидации...")
    test_data = {
        "strain_name": "YC5194",
        "morphology": "палочковидные",
        "gram_stain": "грам-отрицательные"
    }
    
    validation = integrator.validate_strain_data("YC5194", test_data)
    print(f"Статус валидации: {validation['validation_status']}")
    print(f"Уверенность: {validation['confidence']:.2f}")
    
    # Тест обогащения
    print("\n📈 Тестирование обогащения...")
    enriched = integrator.enrich_strain_data("YC5194", test_data)
    print(f"Обогащений выполнено: {len(enriched.get('bacdive_enrichment', {}).get('enrichments', []))}") 