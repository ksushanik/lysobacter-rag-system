#!/usr/bin/env python3
"""
Диагностика проблемы с извлечением контекста из источников RAG системы
"""

import sys
import os
sys.path.append('src')

from src.lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
import json

def debug_context_extraction():
    """Диагностирует проблему с пустым контекстом"""
    
    print("🔍 Диагностика проблемы извлечения контекста")
    print("=" * 50)
    
    # Инициализация RAG системы
    try:
        rag = EnhancedRAGPipeline(use_notebooklm_style=True)
        print("✅ RAG система инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Тестируем на YC5194
    test_query = "Какие характеристики штамма Lysobacter capsici YC5194?"
    
    print(f"\n🔍 Тестирую запрос: {test_query}")
    
    try:
        # Получаем результат
        result = rag.ask_question(query=test_query, top_k=10)
        
        print(f"\n📊 Результат анализа:")
        print(f"- Количество источников: {len(result.sources)}")
        print(f"- Уверенность: {result.confidence}")
        print(f"- Тип ответа: {result.query_type}")
        
        # Анализируем структуру источников
        print(f"\n🔬 Анализ структуры источников:")
        for i, source in enumerate(result.sources):
            print(f"\nИсточник {i+1}:")
            print(f"  Ключи: {list(source.keys())}")
            
            # Проверяем различные поля
            content_fields = ['content', 'text', 'page_content', 'chunk_text']
            content_found = False
            
            for field in content_fields:
                if field in source and source[field]:
                    print(f"  ✅ {field}: {len(str(source[field]))} символов")
                    print(f"     Начало: {str(source[field])[:100]}...")
                    content_found = True
                    break
            
            if not content_found:
                print(f"  ❌ Контент не найден в полях: {content_fields}")
                
            # Показываем все доступные данные
            for key, value in source.items():
                if key not in content_fields:
                    print(f"  📋 {key}: {type(value)} - {str(value)[:50]}...")
        
        # Проверяем базовый ответ RAG
        print(f"\n📝 Базовый ответ RAG:")
        print(f"Длина: {len(result.answer)} символов")
        print(f"Начало: {result.answer[:200]}...")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

def test_direct_search():
    """Тестирует прямой поиск в индексере"""
    
    print(f"\n🔍 Тестирование прямого поиска в индексере")
    print("-" * 40)
    
    try:
        from src.lysobacter_rag.indexer import Indexer
        
        indexer = Indexer()
        
        # Тестируем разные запросы
        test_queries = [
            "YC5194",
            "Lysobacter capsici",
            "capsici YC5194",
            "GW1-59T",
            "Lysobacter antarcticus"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Запрос: '{query}'")
            
            results = indexer.search(query, top_k=5)
            print(f"Найдено: {len(results)} результатов")
            
            for i, result in enumerate(results):
                print(f"  {i+1}. Релевантность: {result.get('distance', 'N/A')}")
                
                # Ищем текст в результате
                text = None
                for field in ['text', 'content', 'page_content', 'chunk_text']:
                    if field in result and result[field]:
                        text = result[field]
                        break
                
                if text:
                    print(f"     Текст ({len(text)} символов): {text[:100]}...")
                else:
                    print(f"     ❌ Текст не найден. Ключи: {list(result.keys())}")
        
    except Exception as e:
        print(f"❌ Ошибка при прямом поиске: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_context_extraction()
    test_direct_search() 