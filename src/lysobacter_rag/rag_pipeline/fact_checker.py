"""
Модуль проверки фактов для предотвращения "додумывания" данных RAG системой
"""
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class FactCheck:
    """Результат проверки факта"""
    fact: str
    is_accurate: bool
    source_strain: Optional[str]
    evidence: str
    confidence: float

class FactChecker:
    """Система проверки фактов для предотвращения некорректных обобщений"""
    
    def __init__(self):
        self.strain_specific_patterns = [
            r'strain\s+([A-Z0-9\-]+)',
            r'штамм\s+([A-Z0-9\-]+)',
            r'([A-Z0-9\-]+[TН]?)[\s\.,]',
        ]
        
    def check_temperature_claim(self, claim: str, evidence_chunks: List[Dict[str, Any]], target_strain: str) -> FactCheck:
        """
        Проверяет корректность утверждения о температуре для конкретного штамма
        
        Args:
            claim: Утверждение о температуре (например, "15-42°C")
            evidence_chunks: Чанки с доказательствами
            target_strain: Целевой штамм (например, "YC5194")
            
        Returns:
            FactCheck: Результат проверки
        """
        # Извлекаем температурный диапазон из утверждения
        temp_pattern = r'(\d+)\s*[-–]\s*(\d+)\s*°?C'
        claim_match = re.search(temp_pattern, claim)
        
        if not claim_match:
            return FactCheck(
                fact=claim,
                is_accurate=False,
                source_strain=None,
                evidence="Не удалось распознать температурный диапазон",
                confidence=0.0
            )
        
        claimed_min, claimed_max = map(int, claim_match.groups())
        
        # Ищем конкретные данные для целевого штамма
        strain_specific_evidence = []
        general_evidence = []
        
        for chunk in evidence_chunks:
            text = chunk['text'].lower()
            
            # Проверяем, упоминается ли конкретный штамм
            is_strain_specific = False
            for pattern in self.strain_specific_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if target_strain.lower() in match.lower():
                        is_strain_specific = True
                        break
            
            # Ищем температурные данные в тексте
            temp_matches = re.findall(temp_pattern, text)
            if temp_matches:
                if is_strain_specific:
                    strain_specific_evidence.append({
                        'text': chunk['text'],
                        'temperatures': temp_matches,
                        'chunk': chunk
                    })
                else:
                    general_evidence.append({
                        'text': chunk['text'],
                        'temperatures': temp_matches,
                        'chunk': chunk
                    })
        
        # Приоритет: специфичные данные для штамма
        if strain_specific_evidence:
            for evidence in strain_specific_evidence:
                for temp_min, temp_max in evidence['temperatures']:
                    temp_min, temp_max = int(temp_min), int(temp_max)
                    if temp_min == claimed_min and temp_max == claimed_max:
                        return FactCheck(
                            fact=claim,
                            is_accurate=True,
                            source_strain=target_strain,
                            evidence=evidence['text'][:200] + "...",
                            confidence=0.95
                        )
            
            # Если не точное совпадение, но есть специфичные данные
            first_evidence = strain_specific_evidence[0]
            first_temp = first_evidence['temperatures'][0]
            actual_min, actual_max = map(int, first_temp)
            
            return FactCheck(
                fact=claim,
                is_accurate=False,
                source_strain=target_strain,
                evidence=f"Фактический диапазон для {target_strain}: {actual_min}-{actual_max}°C. " +
                         first_evidence['text'][:200] + "...",
                confidence=0.9
            )
        
        # Если нет специфичных данных, но есть общие - помечаем как неточные
        if general_evidence:
            return FactCheck(
                fact=claim,
                is_accurate=False,
                source_strain="общие данные рода",
                evidence="Данные относятся к роду в целом, а не к конкретному штамму",
                confidence=0.3
            )
        
        return FactCheck(
            fact=claim,
            is_accurate=False,
            source_strain=None,
            evidence="Температурные данные не найдены",
            confidence=0.0
        )
    
    def check_ph_claim(self, claim: str, evidence_chunks: List[Dict[str, Any]], target_strain: str) -> FactCheck:
        """Проверяет корректность утверждения о pH для конкретного штамма"""
        ph_pattern = r'pH\s*(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)|(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*pH'
        claim_match = re.search(ph_pattern, claim, re.IGNORECASE)
        
        if not claim_match:
            return FactCheck(
                fact=claim,
                is_accurate=False,
                source_strain=None,
                evidence="Не удалось распознать диапазон pH",
                confidence=0.0
            )
        
        # Аналогично температуре - проверяем специфичность для штамма
        return self._check_numeric_range_claim(claim, evidence_chunks, target_strain, ph_pattern, "pH")
    
    def _check_numeric_range_claim(self, claim: str, evidence_chunks: List[Dict[str, Any]], 
                                   target_strain: str, pattern: str, param_name: str) -> FactCheck:
        """Универсальная проверка численных диапазонов"""
        
        strain_mentions = 0
        general_mentions = 0
        
        for chunk in evidence_chunks:
            text = chunk['text']
            
            # Проверяем упоминание целевого штамма
            if target_strain.lower() in text.lower():
                strain_mentions += 1
            else:
                general_mentions += 1
        
        confidence = strain_mentions / (strain_mentions + general_mentions) if (strain_mentions + general_mentions) > 0 else 0
        
        return FactCheck(
            fact=claim,
            is_accurate=confidence > 0.5,
            source_strain=target_strain if confidence > 0.5 else "неопределено",
            evidence=f"Найдено {strain_mentions} специфичных упоминаний и {general_mentions} общих",
            confidence=confidence
        )
    
    def validate_strain_data(self, strain_data: Dict[str, Any], evidence_chunks: List[Dict[str, Any]], 
                            target_strain: str) -> Dict[str, FactCheck]:
        """
        Валидирует все данные о штамме
        
        Args:
            strain_data: Словарь с данными о штамме
            evidence_chunks: Исходные чанки с доказательствами
            target_strain: Название целевого штамма
            
        Returns:
            Dict[str, FactCheck]: Результаты проверки по каждому параметру
        """
        results = {}
        
        # Проверяем температуру
        if 'temperature_range' in strain_data:
            results['temperature'] = self.check_temperature_claim(
                strain_data['temperature_range'], evidence_chunks, target_strain
            )
        
        # Проверяем pH
        if 'ph_range' in strain_data:
            results['ph'] = self.check_ph_claim(
                strain_data['ph_range'], evidence_chunks, target_strain
            )
        
        return results
    
    def get_accuracy_score(self, fact_checks: Dict[str, FactCheck]) -> float:
        """Возвращает общую оценку точности данных"""
        if not fact_checks:
            return 0.0
        
        accurate_checks = sum(1 for check in fact_checks.values() if check.is_accurate)
        total_checks = len(fact_checks)
        
        return accurate_checks / total_checks 