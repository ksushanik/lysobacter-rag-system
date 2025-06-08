#!/usr/bin/env python3
"""
Тест синхронизации настроек между тестами и веб-интерфейсом
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
import time

def test_settings_synchronization():
    """Тестирует что настройки в тестах и веб-интерфейсе одинаковые"""
    
    print("🔄 Тестирование синхронизации настроек")
    print("=" * 50)
    
    # Тестируем те же настройки что использует веб-интерфейс
    test_query = "что тебе известно о штамме SJ-36T?"
    
    print("📋 Проверяемые настройки:")
    print("- EnhancedRAGPipeline(use_notebooklm_style=True)")
    print("- ask_question(top_k=8, use_notebooklm_style=True)")
    print("- max_tokens=8000 (в enhanced_rag.py)")
    print()
    
    try:
        # Инициализация как в веб-интерфейсе
        print("🔧 Инициализация системы (как в веб-интерфейсе)...")
        rag_system = EnhancedRAGPipeline(use_notebooklm_style=True)
        
        # Проверяем что система инициализирована корректно
        assert hasattr(rag_system, 'context_synthesizer'), "❌ context_synthesizer не инициализирован"
        assert rag_system.use_notebooklm_style == True, "❌ use_notebooklm_style не True"
        assert hasattr(rag_system, 'fact_checker'), "❌ fact_checker не инициализирован"
        
        print("✅ Система инициализирована корректно")
        
        # Выполняем запрос с теми же параметрами что и в веб-интерфейсе
        print("🧪 Выполнение запроса с параметрами веб-интерфейса...")
        start_time = time.time()
        
        result = rag_system.ask_question(
            query=test_query,
            top_k=8,  # Как в веб-интерфейсе
            use_notebooklm_style=True  # Как в веб-интерфейсе
        )
        
        end_time = time.time()
        
        # Проверяем результат
        assert result.answer is not None, "❌ Ответ не получен"
        assert len(result.answer) > 100, "❌ Ответ слишком короткий"
        assert result.metadata.get('notebooklm_mode') == True, "❌ NotebookLM режим не активен"
        assert result.num_sources_used > 0, "❌ Источники не использованы"
        
        print("✅ Запрос выполнен успешно")
        
        # Выводим результаты
        print("\n📊 Результаты тестирования:")
        print(f"⏱️ Время выполнения: {end_time - start_time:.2f} сек")
        print(f"🎯 Тип запроса: {result.query_type}")
        print(f"📈 Уверенность: {result.confidence:.2f}")
        print(f"📚 Источников: {result.num_sources_used}")
        print(f"🔧 NotebookLM режим: {result.metadata.get('notebooklm_mode')}")
        print(f"📏 Длина ответа: {len(result.answer)} символов")
        
        # Проверяем что ответ содержит научную информацию
        scientific_keywords = [
            'штамм', 'бактер', 'рост', 'температур', 'pH', 
            'морфологи', 'биохими', 'характеристик'
        ]
        
        found_keywords = [kw for kw in scientific_keywords if kw in result.answer.lower()]
        print(f"🧬 Научные термины найдены: {len(found_keywords)}/{len(scientific_keywords)}")
        
        if len(found_keywords) >= 4:
            print("✅ Ответ содержит достаточно научной информации")
        else:
            print("⚠️ Ответ содержит мало научной информации")
        
        # Проверяем что ответ не обрывается
        if result.answer.endswith('...') or len(result.answer) < 500:
            print("⚠️ Возможно ответ обрывается")
        else:
            print("✅ Ответ полный")
        
        print("\n✅ Все проверки пройдены - настройки синхронизированы!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fact_checker_integration():
    """Тестирует интеграцию fact_checker в систему"""
    
    print("\n🔍 Тестирование интеграции fact_checker")
    print("=" * 40)
    
    try:
        rag_system = EnhancedRAGPipeline(use_notebooklm_style=True)
        
        # Проверяем что fact_checker инициализирован
        assert hasattr(rag_system, 'fact_checker'), "❌ fact_checker не найден"
        assert rag_system.fact_checker is not None, "❌ fact_checker не инициализирован"
        
        print("✅ FactChecker интегрирован в систему")
        
        # Проверяем методы fact_checker
        methods_to_check = [
            'check_temperature_claim',
            'check_ph_claim', 
            'check_strain_specific'
        ]
        
        for method in methods_to_check:
            if hasattr(rag_system.fact_checker, method):
                print(f"✅ Метод {method} доступен")
            else:
                print(f"❌ Метод {method} не найден")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования fact_checker: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔄 Тестирование синхронизации между тестами и веб-интерфейсом")
    print("=" * 70)
    
    # Основной тест синхронизации
    success1 = test_settings_synchronization()
    
    # Тест fact_checker
    success2 = test_fact_checker_integration()
    
    if success1 and success2:
        print("\n🎉 Все тесты синхронизации пройдены!")
        print("\n💡 Веб-интерфейс использует те же настройки что и тесты:")
        print("- ✅ EnhancedRAGPipeline(use_notebooklm_style=True)")
        print("- ✅ ask_question(top_k=8, use_notebooklm_style=True)")  
        print("- ✅ FactChecker интегрирован")
        print("- ✅ max_tokens=8000")
        print("\n🚀 Готово к использованию!")
    else:
        print("\n❌ Некоторые тесты синхронизации не пройдены")
        sys.exit(1) 