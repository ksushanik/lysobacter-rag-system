#!/usr/bin/env python3
"""
Тестирование NotebookLM-стиля RAG системы
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
import time

def test_notebooklm_style():
    """Тестирует NotebookLM-стиль ответов"""
    
    print("🧪 Тестирование NotebookLM-стиля RAG системы")
    print("=" * 50)
    
    try:
        # Инициализируем систему с NotebookLM-стилем
        print("📚 Инициализация системы с NotebookLM-стилем...")
        rag_system = EnhancedRAGPipeline(use_notebooklm_style=True)
        
        # Тестовый запрос
        test_query = "что тебе известно о штамме SJ-36T?"
        
        print(f"\n❓ Тестовый запрос: {test_query}")
        print("\n🔍 Генерирую ответ...")
        
        start_time = time.time()
        
        # Получаем ответ
        result = rag_system.ask_question(
            query=test_query,
            top_k=8,
            use_notebooklm_style=True
        )
        
        end_time = time.time()
        
        print("\n" + "="*50)
        print("📄 ОТВЕТ В СТИЛЕ NotebookLM:")
        print("="*50)
        print(result.answer)
        
        print("\n" + "="*50)
        print("📊 МЕТАДАННЫЕ:")
        print("="*50)
        print(f"⏱️ Время выполнения: {end_time - start_time:.2f} сек")
        print(f"🎯 Тип запроса: {result.query_type}")
        print(f"📈 Уверенность: {result.confidence:.2f}")
        print(f"📚 Источников использовано: {result.num_sources_used}")
        print(f"🔧 NotebookLM режим: {result.metadata.get('notebooklm_mode', False)}")
        print(f"📏 Длина контекста: {result.metadata.get('context_length', 0)} символов")
        
        print("\n" + "="*50)
        print("🔗 ИСТОЧНИКИ:")
        print("="*50)
        for i, source in enumerate(result.sources[:3], 1):
            print(f"{i}. {source.get('source', 'Неизвестный источник')}")
            if 'relevance' in source:
                print(f"   Релевантность: {source['relevance']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {str(e)}")
        return False

def compare_styles():
    """Сравнивает стандартный и NotebookLM стили"""
    
    print("\n" + "="*50)
    print("🔄 СРАВНЕНИЕ СТИЛЕЙ")
    print("="*50)
    
    try:
        query = "что тебе известно о штамме SJ-36T?"
        
        # Тест стандартного стиля
        print("\n📝 Стандартный стиль...")
        rag_standard = EnhancedRAGPipeline(use_notebooklm_style=False)
        result_standard = rag_standard.ask_question(query, use_notebooklm_style=False)
        
        # Тест NotebookLM стиля
        print("📚 NotebookLM стиль...")
        rag_notebooklm = EnhancedRAGPipeline(use_notebooklm_style=True)
        result_notebooklm = rag_notebooklm.ask_question(query, use_notebooklm_style=True)
        
        print("\n" + "="*30 + " СТАНДАРТНЫЙ " + "="*30)
        print(result_standard.answer[:500] + "...")
        
        print("\n" + "="*30 + " NOTEBOOKLM " + "="*30)
        print(result_notebooklm.answer[:500] + "...")
        
        print("\n📊 СРАВНЕНИЕ ХАРАКТЕРИСТИК:")
        print(f"Стандартный - Длина: {len(result_standard.answer)}, Источники: {result_standard.num_sources_used}")
        print(f"NotebookLM  - Длина: {len(result_notebooklm.answer)}, Источники: {result_notebooklm.num_sources_used}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сравнения: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧬 Тестирование улучшенной RAG системы в стиле NotebookLM")
    print("=" * 70)
    
    # Основной тест
    success1 = test_notebooklm_style()
    
    # Сравнение стилей
    success2 = compare_styles()
    
    if success1 and success2:
        print("\n✅ Все тесты пройдены успешно!")
        print("\n💡 Рекомендации:")
        print("- Используйте NotebookLM-стиль для научного анализа штаммов")
        print("- Стандартный стиль подходит для простых вопросов")
        print("- NotebookLM-стиль обеспечивает более связное повествование")
    else:
        print("\n❌ Некоторые тесты не пройдены")
        sys.exit(1) 