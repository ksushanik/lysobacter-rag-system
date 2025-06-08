#!/usr/bin/env python3
"""
Исправление системы поиска - добавляем гибридный поиск
"""
import sys
sys.path.insert(0, 'src')

from lysobacter_rag.indexer import Indexer
import re
from typing import List, Dict, Any

class ImprovedSearchEngine:
    def __init__(self):
        self.indexer = Indexer()
        self.collection = self.indexer.collection
        
    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Гибридный поиск: семантический + ключевые слова
        """
        print(f"🔍 Выполняю гибридный поиск для: '{query}'")
        
        # 1. Проверяем на точные совпадения (например, штаммы)
        exact_matches = self._exact_keyword_search(query, top_k=top_k)
        
        # 2. Семантический поиск
        semantic_results = self.indexer.search(query, top_k=top_k)
        
        # 3. Объединяем и ранжируем результаты
        combined_results = self._combine_and_rank_results(
            exact_matches, semantic_results, query
        )
        
        return combined_results[:top_k]
    
    def _exact_keyword_search(self, query: str, top_k: int = 50) -> List[Dict[str, Any]]:
        """
        Точный поиск по ключевым словам в документах
        """
        # Извлекаем потенциальные идентификаторы штаммов
        strain_patterns = [
            r'\b[A-Z]{1,3}\d{3,5}[A-Z]?\b',  # YC5194, GW1-59T и т.д.
            r'\b[A-Z]+-?\d+[A-Z]*\b',        # различные варианты
        ]
        
        keywords = [query.strip()]
        
        # Ищем паттерны штаммов в запросе
        for pattern in strain_patterns:
            matches = re.findall(pattern, query.upper())
            keywords.extend(matches)
        
        # Получаем все документы
        all_data = self.collection.get()
        
        exact_results = []
        
        if all_data['documents']:
            for i, doc in enumerate(all_data['documents']):
                doc_upper = doc.upper()
                score = 0
                
                # Подсчитываем точные совпадения
                for keyword in keywords:
                    keyword_upper = keyword.upper()
                    count = doc_upper.count(keyword_upper)
                    if count > 0:
                        score += count * 10  # Высокий вес для точных совпадений
                
                if score > 0:
                    metadata = all_data['metadatas'][i]
                    exact_results.append({
                        'text': doc,
                        'metadata': metadata,
                        'relevance_score': min(score / 100.0, 1.0),
                        'search_type': 'exact'
                    })
        
        # Сортируем по релевантности
        exact_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"📍 Найдено {len(exact_results)} точных совпадений")
        
        return exact_results[:top_k]
    
    def _combine_and_rank_results(self, exact_results, semantic_results, query):
        """
        Объединяем точные и семантические результаты
        """
        combined = {}
        
        # Добавляем точные результаты с высоким приоритетом
        for result in exact_results:
            doc_text = result['text']
            if doc_text not in combined:
                combined[doc_text] = result
                combined[doc_text]['final_score'] = result['relevance_score'] + 0.5  # Бонус за точность
            
        # Добавляем семантические результаты
        for result in semantic_results:
            doc_text = result['text']
            if doc_text not in combined:
                combined[doc_text] = result
                combined[doc_text]['final_score'] = result['relevance_score']
                combined[doc_text]['search_type'] = 'semantic'
            else:
                # Если документ уже есть, комбинируем скоры
                combined[doc_text]['final_score'] += result['relevance_score'] * 0.3
        
        # Сортируем по финальному скору
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return final_results

def test_improved_search():
    """
    Тестируем улучшенную систему поиска
    """
    print("🚀 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ СИСТЕМЫ ПОИСКА")
    print("=" * 60)
    
    search_engine = ImprovedSearchEngine()
    
    test_queries = [
        "YC5194",
        "Lysobacter capsici YC5194", 
        "Какие характеристики штамма Lysobacter capsici YC5194?",
        "GW1-59T",
        "Что известно о штамме GW1-59T?"
    ]
    
    for query in test_queries:
        print(f"\n🧪 ТЕСТ: '{query}'")
        print("-" * 50)
        
        results = search_engine.hybrid_search(query, top_k=5)
        
        yc_found = any('YC5194' in result['text'] for result in results if 'YC5194' in query)
        gw_found = any('GW1-59' in result['text'] for result in results if 'GW1-59' in query)
        
        print(f"📊 Найдено результатов: {len(results)}")
        print(f"🎯 Искомый штамм найден: {yc_found or gw_found}")
        
        for i, result in enumerate(results[:3]):
            search_type = result.get('search_type', 'unknown')
            
            print(f"\n{i+1}. [{search_type.upper()}] Скор: {result['final_score']:.3f}")
            print(f"   Файл: {result['metadata'].get('source_pdf', 'неизвестен')}")
            
            # Проверяем наличие искомых штаммов
            contains_yc = 'YC5194' in result['text']
            contains_gw = 'GW1-59' in result['text'] 
            
            if contains_yc:
                print(f"   ✅ Содержит YC5194")
            if contains_gw:
                print(f"   ✅ Содержит GW1-59T")
                
            print(f"   Первые 150 символов: {result['text'][:150]}...")
            
        print("\n" + "="*60)

def demo_fix():
    """
    Демонстрируем исправленный поиск для проблемного запроса
    """
    print("🎯 ДЕМОНСТРАЦИЯ ИСПРАВЛЕНИЯ ПОИСКА YC5194")
    print("=" * 50)
    
    search_engine = ImprovedSearchEngine()
    
    query = "Какие характеристики штамма Lysobacter capsici YC5194?"
    print(f"Запрос: {query}")
    
    results = search_engine.hybrid_search(query, top_k=10)
    
    yc_results = [r for r in results if 'YC5194' in r['text']]
    
    print(f"\n📊 Всего результатов: {len(results)}")
    print(f"🎯 Результатов с YC5194: {len(yc_results)}")
    
    if yc_results:
        print(f"\n✅ УСПЕХ! Найдены релевантные результаты:")
        for i, result in enumerate(yc_results[:5]):
            print(f"\n{i+1}. Файл: {result['metadata'].get('source_pdf', 'неизвестен')}")
            print(f"   Тип: {result['metadata'].get('chunk_type', 'неизвестен')}")
            print(f"   Скор: {result['final_score']:.3f}")
            print(f"   Содержание: {result['text'][:200]}...")
    else:
        print("❌ YC5194 все еще не найден")

if __name__ == "__main__":
    test_improved_search()
    print("\n\n")
    demo_fix() 