"""
Утилита для перевода запросов между языками
"""
from typing import Optional
import requests
import json
import logging

logger = logging.getLogger(__name__)

class QueryTranslator:
    """Переводчик запросов для многоязычного поиска"""
    
    def __init__(self):
        """Инициализация переводчика"""
        pass
    
    def translate_to_english(self, query: str) -> str:
        """
        Переводит запрос с русского на английский
        
        Args:
            query: Запрос на русском языке
            
        Returns:
            str: Переведенный запрос на английском языке
        """
        # Простой словарь научных терминов
        terms_dict = {
            'штамм': 'strain',
            'лизобактер': 'lysobacter',
            'лизобактерий': 'lysobacter',
            'лизобактерия': 'lysobacter',
            'характеристики': 'characteristics',
            'морфология': 'morphology',
            'биохимический': 'biochemical',
            'биохимические': 'biochemical',
            'свойства': 'properties',
            'филогенетический': 'phylogenetic',
            'анализ': 'analysis',
            'жирнокислотный': 'fatty acid',
            'состав': 'composition',
            'выделен': 'isolated',
            'источник': 'source',
            'условия': 'conditions',
            'роста': 'growth',
            'отличия': 'differences',
            'родственники': 'relatives',
            'ближайшие': 'closest',
            'таксономический': 'taxonomic',
            'положение': 'position',
            'где': 'where',
            'что': 'what',
            'какие': 'which',
            'найди': 'find',
            'информация': 'information',
            'описание': 'description',
            'GW1-59T': 'GW1-59T'
        }
        
        # Переводим термины
        translated = query.lower()
        for ru_term, en_term in terms_dict.items():
            translated = translated.replace(ru_term.lower(), en_term)
        
        logger.info(f"Переведен запрос: '{query}' -> '{translated}'")
        return translated
    
    def expand_query(self, query: str) -> list[str]:
        """
        Расширяет запрос синонимами для лучшего поиска
        
        Args:
            query: Исходный запрос
            
        Returns:
            list[str]: Список расширенных запросов
        """
        expanded_queries = [query]
        
        # Добавляем синонимы для общих терминов
        if 'штамм' in query.lower():
            expanded_queries.append(query.replace('штамм', 'изолят'))
            expanded_queries.append(query.replace('штамм', 'культура'))
        
        if 'характеристики' in query.lower():
            expanded_queries.append(query.replace('характеристики', 'свойства'))
            expanded_queries.append(query.replace('характеристики', 'признаки'))
        
        return expanded_queries 