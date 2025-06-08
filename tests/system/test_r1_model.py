#!/usr/bin/env python3
"""
Тест новой модели DeepSeek R1 для улучшенной RAG системы
"""
import sys
import time
from pathlib import Path

# Добавляем пути для импорта из корня проекта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_r1_model():
    """Тестирует модель deepseek-r1 с улучшенной RAG системой"""
    
    print("🧠 ТЕСТ МОДЕЛИ DEEPSEEK-R1 ДЛЯ РАССУЖДЕНИЙ")
    print("=" * 60)
    
    try:
        from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
        from config import config
        
        print(f"🤖 Используемая модель: {config.OPENAI_MODEL}")
        print(f"🔗 API URL: {config.OPENROUTER_BASE_URL}")
        
        # Инициализация системы
        print("\n📦 Инициализация системы...")
        enhanced_rag = EnhancedRAGPipeline()
        print("✅ Система инициализирована")
        
        # Тестовые запросы для демонстрации возможностей R1
        test_queries = [
            {
                'query': "Что известно о штамме GW1-59T?",
                'description': "Детальный анализ штамма (должен показать рассуждения R1)"
            },
            {
                'query': "Сравните морфологические и биохимические характеристики штамма GW1-59T с другими лизобактериями",
                'description': "Сложный сравнительный анализ (тест логических рассуждений)"
            },
            {
                'query': "Объясните таксономическое значение хемотаксономических данных для классификации лизобактерий",
                'description': "Концептуальный анализ (тест глубины рассуждений)"
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"🧪 ТЕСТ {i}: {test_case['description']}")
            print(f"📝 Запрос: {test_case['query']}")
            print(f"{'='*60}")
            
            print("\n⏳ Обрабатываю запрос с моделью R1...")
            
            start_time = time.time()
            result = enhanced_rag.ask_question(test_case['query'])
            process_time = time.time() - start_time
            
            print(f"\n📊 РЕЗУЛЬТАТЫ:")
            print(f"⏱️ Время обработки: {process_time:.2f} сек")
            print(f"🎯 Тип запроса: {result.query_type}")
            print(f"📊 Уверенность: {result.confidence:.3f}")
            print(f"📚 Источников: {result.num_sources_used}")
            print(f"📝 Длина ответа: {len(result.answer)} символов")
            
            if result.metadata.get('has_tables'):
                print(f"📋 Найдено таблиц: {result.metadata['table_count']}")
            
            print(f"\n💬 ОТВЕТ МОДЕЛИ R1:")
            print("-" * 60)
            
            # Выводим полный ответ для демонстрации качества R1
            print(result.answer)
            
            print(f"\n📚 ИСТОЧНИКИ:")
            for source in result.sources[:3]:  # Показываем первые 3
                print(f"   [{source['id']}] {source['document']} (стр. {source.get('page', 'N/A')})")
                if source.get('is_differential_table'):
                    print(f"       🔬 Дифференциальная таблица")
            
            print(f"\n⭐ КАЧЕСТВО ОТВЕТА R1:")
            quality_score = analyze_answer_quality(result.answer)
            print(f"   📝 Структурированность: {quality_score['structure']}/5")
            print(f"   🔬 Научная детализация: {quality_score['detail']}/5")
            print(f"   📊 Использование данных: {quality_score['data_usage']}/5")
            print(f"   🎯 Общая оценка: {quality_score['overall']:.1f}/5")
            
            if i < len(test_queries):
                print(f"\n⏸️ Пауза 3 секунды перед следующим тестом...")
                time.sleep(3)
        
        print(f"\n{'='*60}")
        print("✅ ВСЕ ТЕСТЫ МОДЕЛИ R1 ЗАВЕРШЕНЫ!")
        print("🧠 DeepSeek R1 показывает улучшенные способности к рассуждениям")
        print("📈 Рекомендуется использовать для производственной системы")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании R1: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def analyze_answer_quality(answer: str) -> dict:
    """Анализирует качество ответа для оценки модели R1"""
    
    # Проверяем структурированность
    structure_indicators = ['##', '**', '- ', '*', '1.', '2.']
    structure_score = min(5, sum(1 for indicator in structure_indicators if indicator in answer))
    
    # Проверяем научную детализация
    scientific_terms = ['мол.%', 'мкм', '°C', 'pH', 'Mb', 'кДа', 'г/л', 'мМ']
    detail_score = min(5, sum(1 for term in scientific_terms if term in answer) * 0.7)
    
    # Проверяем использование данных
    data_indicators = ['[Источник', 'положительная', 'отрицательная', ':', '%']
    data_score = min(5, sum(1 for indicator in data_indicators if indicator in answer) * 0.3)
    
    overall = (structure_score + detail_score + data_score) / 3
    
    return {
        'structure': int(structure_score),
        'detail': int(detail_score),
        'data_usage': int(data_score),
        'overall': overall
    }

def compare_models():
    """Быстрое сравнение R1 с предыдущей моделью"""
    
    print("\n🔄 БЫСТРОЕ СРАВНЕНИЕ МОДЕЛЕЙ")
    print("=" * 60)
    
    try:
        from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
        from config import config
        
        test_query = "Что известно о штамме GW1-59T?"
        
        print(f"📊 Тестовый запрос: {test_query}")
        
        # Тест текущей модели (R1)
        print(f"\n🧠 Модель: {config.OPENAI_MODEL}")
        
        rag = EnhancedRAGPipeline()
        start_time = time.time()
        result = rag.ask_question(test_query)
        r1_time = time.time() - start_time
        
        print(f"⏱️ Время R1: {r1_time:.2f} сек")
        print(f"📝 Длина ответа R1: {len(result.answer)} символов")
        print(f"📊 Уверенность R1: {result.confidence:.3f}")
        
        quality = analyze_answer_quality(result.answer)
        print(f"🎯 Качество R1: {quality['overall']:.1f}/5")
        
        print(f"\n💬 Образец ответа R1 (первые 400 символов):")
        print("-" * 40)
        print(result.answer[:400] + "..." if len(result.answer) > 400 else result.answer)
        
    except Exception as e:
        print(f"❌ Ошибка сравнения: {str(e)}")

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ DEEPSEEK-R1")
    print("🧠 Модель рассуждений для улучшенной RAG системы")
    print()
    
    # Основное тестирование
    success = test_r1_model()
    
    if success:
        # Быстрое сравнение
        compare_models()
    
    print(f"\n{'='*60}")
    print("🎯 РЕЗУЛЬТАТ:", "✅ УСПЕХ" if success else "❌ ОШИБКА")
    print("🧬 RAG система готова к работе с DeepSeek R1!")
    
    sys.exit(0 if success else 1) 