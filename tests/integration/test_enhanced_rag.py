#!/usr/bin/env python3
"""
Тестирование улучшенной RAG системы для лизобактерий
"""
import sys
import time
from pathlib import Path

# Добавляем пути для импорта из корня проекта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline, QueryType
from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
from config import config

def test_enhanced_vs_standard():
    """Сравнение улучшенной и стандартной RAG систем"""
    
    print("🔬 СРАВНЕНИЕ RAG СИСТЕМ")
    print("=" * 60)
    
    # Тестовые запросы разных типов
    test_queries = [
        {
            'query': "Что известно о штамме GW1-59T?",
            'expected_type': QueryType.STRAIN_ANALYSIS,
            'description': "Анализ штамма"
        },
        {
            'query': "Сравните штаммы GW1-59T и другие лизобактерии",
            'expected_type': QueryType.COMPARATIVE_ANALYSIS,
            'description': "Сравнительный анализ"
        },
        {
            'query': "Интерпретируйте данные в таблице дифференциальных характеристик",
            'expected_type': QueryType.TABLE_INTERPRETATION,
            'description': "Интерпретация таблиц"
        }
    ]
    
    try:
        # Инициализация систем
        print("🚀 Инициализация систем...")
        enhanced_rag = EnhancedRAGPipeline()
        standard_rag = RAGPipeline()
        
        print("✅ Системы инициализированы успешно")
        print(f"📊 Доступные типы запросов: {len(enhanced_rag.get_query_types())}")
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"🧪 ТЕСТ {i}: {test_case['description']}")
            print(f"📝 Запрос: {test_case['query']}")
            print(f"🎯 Ожидаемый тип: {test_case['expected_type'].value}")
            print(f"{'='*60}")
            
            # Тест улучшенной системы
            print("\n🔬 УЛУЧШЕННАЯ RAG СИСТЕМА:")
            print("-" * 40)
            
            start_time = time.time()
            enhanced_result = enhanced_rag.ask_question(test_case['query'])
            enhanced_time = time.time() - start_time
            
            print(f"⏱️ Время: {enhanced_time:.2f} сек")
            print(f"🎯 Определенный тип: {enhanced_result.query_type}")
            print(f"📊 Уверенность: {enhanced_result.confidence:.3f}")
            print(f"📚 Источников: {enhanced_result.num_sources_used}")
            print(f"📋 Метаданные: {enhanced_result.metadata}")
            print(f"📝 Ответ ({len(enhanced_result.answer)} символов):")
            print(enhanced_result.answer[:300] + "..." if len(enhanced_result.answer) > 300 else enhanced_result.answer)
            
            # Тест стандартной системы
            print("\n📚 СТАНДАРТНАЯ RAG СИСТЕМА:")
            print("-" * 40)
            
            start_time = time.time()
            standard_result = standard_rag.ask_question(test_case['query'])
            standard_time = time.time() - start_time
            
            print(f"⏱️ Время: {standard_time:.2f} сек")
            print(f"📊 Уверенность: {standard_result['confidence']:.3f}")
            print(f"📚 Источников: {standard_result['num_sources_used']}")
            print(f"📝 Ответ ({len(standard_result['answer'])} символов):")
            print(standard_result['answer'][:300] + "..." if len(standard_result['answer']) > 300 else standard_result['answer'])
            
            # Сравнение
            print(f"\n📈 СРАВНЕНИЕ:")
            print(f"   Время: Улучшенная {enhanced_time:.2f}с vs Стандартная {standard_time:.2f}с")
            print(f"   Длина ответа: {len(enhanced_result.answer)} vs {len(standard_result['answer'])} символов")
            print(f"   Уверенность: {enhanced_result.confidence:.3f} vs {standard_result['confidence']:.3f}")
            
            time.sleep(2)  # Пауза между тестами
        
        # Статистика систем
        print(f"\n{'='*60}")
        print("📊 СТАТИСТИКА СИСТЕМ")
        print(f"{'='*60}")
        
        enhanced_stats = enhanced_rag.get_pipeline_stats()
        standard_stats = standard_rag.get_pipeline_stats()
        
        print("\n🔬 Улучшенная система:")
        print(f"   Специализированных промптов: {enhanced_stats['enhanced_features']['specialized_prompts']}")
        print(f"   Типов запросов: {len(enhanced_stats['enhanced_features']['query_types'])}")
        print(f"   Приоритизация таблиц: {enhanced_stats['enhanced_features']['table_prioritization']}")
        
        print("\n📚 Стандартная система:")
        print(f"   Документов в базе: {standard_stats.get('total_documents', 'N/A')}")
        print(f"   Коллекций: {standard_stats.get('collections', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {str(e)}")
        import traceback
        traceback.print_exc()

def test_query_type_detection():
    """Тестирование определения типов запросов"""
    
    print("\n🎯 ТЕСТИРОВАНИЕ ОПРЕДЕЛЕНИЯ ТИПОВ ЗАПРОСОВ")
    print("=" * 60)
    
    try:
        enhanced_rag = EnhancedRAGPipeline()
        
        test_queries = [
            ("Что известно о штамме GW1-59T?", QueryType.STRAIN_ANALYSIS),
            ("Сравните штаммы лизобактерий", QueryType.COMPARATIVE_ANALYSIS),
            ("Какие различия между штаммами?", QueryType.COMPARATIVE_ANALYSIS),
            ("Интерпретируйте таблицу", QueryType.TABLE_INTERPRETATION),
            ("Как определить вид лизобактерии?", QueryType.METHODOLOGY),
            ("Расскажите о лизобактериях", QueryType.GENERAL_SYNTHESIS),
        ]
        
        for query, expected_type in test_queries:
            detected_type = enhanced_rag.prompt_system.detect_query_type(query)
            status = "✅" if detected_type == expected_type else "❌"
            print(f"{status} '{query}' -> {detected_type.value} (ожидался: {expected_type.value})")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

def interactive_test():
    """Интерактивное тестирование"""
    
    print("\n🎮 ИНТЕРАКТИВНОЕ ТЕСТИРОВАНИЕ")
    print("=" * 60)
    print("Введите 'exit' для выхода")
    
    try:
        enhanced_rag = EnhancedRAGPipeline()
        
        while True:
            query = input("\n🔍 Ваш вопрос: ").strip()
            
            if query.lower() in ['exit', 'выход', 'quit']:
                break
            
            if not query:
                continue
            
            print("\n⏳ Обрабатываю запрос...")
            
            start_time = time.time()
            result = enhanced_rag.ask_question(query)
            process_time = time.time() - start_time
            
            print(f"\n📊 РЕЗУЛЬТАТ:")
            print(f"⏱️ Время обработки: {process_time:.2f} сек")
            print(f"🎯 Тип запроса: {result.query_type}")
            print(f"📊 Уверенность: {result.confidence:.3f}")
            print(f"📚 Источников использовано: {result.num_sources_used}")
            
            if result.metadata.get('has_tables'):
                print(f"📋 Найдено таблиц: {result.metadata['table_count']}")
            
            print(f"\n💬 ОТВЕТ:")
            print("-" * 40)
            print(result.answer)
            
            if result.sources:
                print(f"\n📚 ИСТОЧНИКИ:")
                for source in result.sources[:3]:  # Показываем первые 3
                    print(f"   [{source['id']}] {source['document']} (стр. {source.get('page', 'N/A')})")
                    if source.get('is_differential_table'):
                        print(f"       🔬 Дифференциальная таблица")
    
    except KeyboardInterrupt:
        print("\n👋 Тестирование прервано пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    print("🧬 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ RAG СИСТЕМЫ ДЛЯ ЛИЗОБАКТЕРИЙ")
    print("=" * 60)
    
    # Основное сравнение
    test_enhanced_vs_standard()
    
    # Тестирование определения типов
    test_query_type_detection()
    
    # Интерактивный режим
    try:
        response = input("\n🎮 Запустить интерактивное тестирование? (y/n): ").strip().lower()
        if response in ['y', 'yes', 'да', 'д']:
            interactive_test()
    except KeyboardInterrupt:
        pass
    
    print("\n✅ Тестирование завершено!") 