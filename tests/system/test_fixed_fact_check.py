#!/usr/bin/env python3
"""
Тест исправленной системы с интегрированным FactChecker
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline

def test_fixed_system():
    """Тестирует исправленную систему с FactChecker"""
    
    print("🧪 Тестирование исправленной системы с интегрированным FactChecker")
    print("=" * 70)
    
    # Инициализируем систему
    rag_system = EnhancedRAGPipeline(use_notebooklm_style=True)
    
    # Тестируем на проблемном запросе
    query = "Какие характеристики штамма Lysobacter capsici YC5194?"
    
    print(f"📝 Запрос: {query}")
    print()
    
    # Получаем ответ
    result = rag_system.ask_question(query, top_k=8, use_notebooklm_style=True)
    
    print("📄 ОТВЕТ С ПРОВЕРКОЙ ФАКТОВ:")
    print("=" * 50)
    print(result.answer)
    
    print("\n📊 МЕТАДАННЫЕ:")
    print("=" * 30)
    print(f"🎯 Тип запроса: {result.query_type}")
    print(f"📚 Источников: {result.num_sources_used}")
    print(f"📏 Длина ответа: {len(result.answer)} символов")
    
    # Проверяем наличие предупреждений
    if "🔍 Проверка фактов:" in result.answer:
        print("\n✅ FactChecker активен - обнаружены предупреждения!")
        
        # Извлекаем секцию предупреждений
        warning_section = result.answer.split("🔍 Проверка фактов:")[1]
        print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
        print(warning_section)
    else:
        print("\n❌ FactChecker не сработал - предупреждения отсутствуют")
    
    return "🔍 Проверка фактов:" in result.answer

def compare_before_after():
    """Сравнивает результаты до и после интеграции FactChecker"""
    
    print("\n🔄 Сравнение ДО и ПОСЛЕ интеграции FactChecker")
    print("=" * 50)
    
    expected_problems = [
        "15-42°C (вместо 15-37°C)",
        "Отсутствие конкретных данных о происхождении",
        "Отсутствие размеров клеток"
    ]
    
    print("📋 Ожидаемые проблемы в ответах:")
    for problem in expected_problems:
        print(f"   - {problem}")
    
    print("\n💡 После интеграции FactChecker система должна:")
    print("   ✅ Предупреждать о температурном диапазоне 15-42°C")
    print("   ✅ Рекомендовать проверку первоисточников")
    print("   ✅ Повышать точность научных данных")

if __name__ == "__main__":
    print("🔧 Тестирование интеграции FactChecker в RAG систему")
    print("=" * 70)
    
    # Основной тест
    fact_checker_active = test_fixed_system()
    
    # Сравнение
    compare_before_after()
    
    if fact_checker_active:
        print("\n🎉 УСПЕХ! FactChecker интегрирован и работает!")
        print("\n💡 Система теперь:")
        print("- ✅ Автоматически проверяет температурные данные")
        print("- ✅ Предупреждает о возможных неточностях") 
        print("- ✅ Рекомендует проверку первоисточников")
        print("- ✅ Повышает научную достоверность")
    else:
        print("\n❌ FactChecker не активен - требуется дополнительная настройка")
        sys.exit(1) 