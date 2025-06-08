#!/usr/bin/env python3
"""
Тест системы валидации фактов для предотвращения "додумывания" данных
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
from lysobacter_rag.rag_pipeline.fact_checker import FactChecker

def test_fact_validation():
    """Тестирует систему валидации фактов"""
    
    print("🔍 Тестирование системы валидации фактов")
    print("=" * 60)
    
    # Инициализируем систему
    rag = EnhancedRAGPipeline(use_notebooklm_style=True)
    fact_checker = FactChecker()
    
    # Тестовый запрос
    query = "Какие характеристики штамма Lysobacter capsici YC5194?"
    
    print(f"📝 Запрос: {query}")
    print()
    
    # Получаем ответ от системы
    result = rag.ask_question(query, top_k=5)
    
    print("🤖 Ответ системы:")
    print(result.answer[:500] + "..." if len(result.answer) > 500 else result.answer)
    print()
    
    # Извлекаем конкретные утверждения для проверки
    test_claims = {
        "temperature_range": "15-42°C",
        "ph_range": "5.5-11.0"
    }
    
    print("🧪 Проверка фактов:")
    print("-" * 30)
    
    # Преобразуем источники в формат для fact_checker
    evidence_chunks = []
    for source in result.sources:
        chunk = {
            'text': source.get('text_preview', ''),
            'metadata': {'source': source.get('document', '')}
        }
        evidence_chunks.append(chunk)
    
    # Проверяем каждое утверждение
    for claim_type, claim_value in test_claims.items():
        print(f"\n📊 Проверка: {claim_type} = {claim_value}")
        
        if claim_type == "temperature_range":
            fact_check = fact_checker.check_temperature_claim(
                claim_value, 
                evidence_chunks, 
                "YC5194"
            )
        elif claim_type == "ph_range":
            fact_check = fact_checker.check_ph_claim(
                claim_value,
                evidence_chunks,
                "YC5194"
            )
        
        print(f"✅ Точность: {'Да' if fact_check.is_accurate else 'НЕТ'}")
        print(f"🎯 Уверенность: {fact_check.confidence:.2f}")
        print(f"📍 Источник: {fact_check.source_strain}")
        print(f"🔍 Доказательство: {fact_check.evidence[:100]}...")
        
        if not fact_check.is_accurate:
            print("⚠️  ПРЕДУПРЕЖДЕНИЕ: Обнаружено потенциальное 'додумывание' данных!")
    
    print("\n" + "=" * 60)
    print("✅ Тест валидации фактов завершен")

def test_specific_temperature_issue():
    """Тестирует конкретную проблему с температурой YC5194"""
    
    print("\n🌡️  Специальный тест температурной проблемы")
    print("=" * 60)
    
    rag = EnhancedRAGPipeline(use_notebooklm_style=True)
    
    # Точный запрос о температуре
    result = rag.ask_question("Lysobacter capsici YC5194 температурный диапазон роста", top_k=3)
    
    print("📋 Найденные источники:")
    for i, source in enumerate(result.sources[:3], 1):
        preview = source.get('text_preview', 'Нет превью')
        print(f"{i}. {preview[:150]}...")
        
        # Проверяем упоминание YC5194
        if 'YC5194' in preview:
            print("   ✅ Упоминает YC5194")
        else:
            print("   ❌ НЕ упоминает YC5194 - возможно общие данные")
        print()
    
    print("🤖 Ответ системы о температуре:")
    temperature_part = ""
    for line in result.answer.split('\n'):
        if 'температур' in line.lower() or '°C' in line or 'градус' in line.lower():
            temperature_part += line + "\n"
    
    print(temperature_part if temperature_part else "Данные о температуре не найдены")
    
    # Ищем конкретные значения температуры
    import re
    temp_matches = re.findall(r'(\d+)\s*[-–]\s*(\d+)\s*°?C', result.answer)
    if temp_matches:
        print(f"\n🎯 Обнаруженные температурные диапазоны: {temp_matches}")
        for temp_min, temp_max in temp_matches:
            if temp_max == "42":
                print("⚠️  ОБНАРУЖЕНА ПРОБЛЕМА: система указала 42°C!")
                print("📚 Правильный диапазон по источнику: 15-37°C")
            elif temp_max == "37":
                print("✅ Корректное значение: 37°C")

if __name__ == "__main__":
    test_fact_validation()
    test_specific_temperature_issue() 