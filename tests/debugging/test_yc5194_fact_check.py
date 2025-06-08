#!/usr/bin/env python3
"""
Тест проверки фактов для штамма Lysobacter capsici YC5194
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
from lysobacter_rag.rag_pipeline.fact_checker import FactChecker

def test_yc5194_facts():
    """Тестирует проверку фактов для YC5194"""
    
    print("🔍 Проверка фактов для штамма Lysobacter capsici YC5194")
    print("=" * 60)
    
    # Инициализируем систему
    rag_system = EnhancedRAGPipeline(use_notebooklm_style=True)
    fact_checker = FactChecker()
    
    # Получаем ответ от системы
    query = "Какие характеристики штамма Lysobacter capsici YC5194?"
    result = rag_system.ask_question(query, top_k=8, use_notebooklm_style=True)
    
    print(f"📝 Ответ системы (первые 500 символов):")
    print(result.answer[:500] + "...")
    print()
    
    # Преобразуем источники для fact_checker
    evidence_chunks = []
    for source in result.sources:
        if hasattr(source, 'get'):
            text = source.get('content', source.get('text', ''))
        else:
            text = str(source)
        
        chunk = {
            'text': text,
            'metadata': {'source': 'database'}
        }
        evidence_chunks.append(chunk)
    
    print("📚 Источники для проверки:")
    for i, chunk in enumerate(evidence_chunks[:3], 1):
        preview = chunk['text'][:100].replace('\n', ' ')
        print(f"{i}. {preview}...")
    print()
    
    # Проверяем температурные данные
    print("🌡️ Проверка температурных данных:")
    
    # Ищем температурные утверждения в ответе
    import re
    temp_patterns = [
        r'(\d+)\s*[–-]\s*(\d+)\s*°C',
        r'от\s+(\d+)\s*°C\s+до\s+(\d+)\s*°C',
        r'диапазон.*?(\d+).*?(\d+)\s*°C'
    ]
    
    found_temps = []
    for pattern in temp_patterns:
        matches = re.findall(pattern, result.answer)
        for match in matches:
            temp_range = f"{match[0]}-{match[1]}°C"
            found_temps.append(temp_range)
    
    print(f"🔍 Найденные температурные диапазоны: {found_temps}")
    
    # Проверяем каждый найденный диапазон
    for temp_claim in found_temps:
        fact_check = fact_checker.check_temperature_claim(
            temp_claim, 
            evidence_chunks, 
            "YC5194"
        )
        
        status = "✅ ТОЧНО" if fact_check.is_accurate else "❌ НЕТОЧНО"
        print(f"   {temp_claim}: {status}")
        print(f"   Доказательство: {fact_check.evidence[:150]}...")
        print(f"   Уверенность: {fact_check.confidence:.2f}")
        print()
    
    # Проверяем pH данные
    print("⚗️ Проверка pH данных:")
    ph_patterns = [
        r'pH\s+(\d+[.,]\d+)\s*[–-]\s*(\d+[.,]\d+)',
        r'от\s+pH\s+(\d+[.,]\d+)\s+до\s+(\d+[.,]\d+)',
        r'диапазон.*?pH.*?(\d+[.,]\d+).*?(\d+[.,]\d+)'
    ]
    
    found_ph = []
    for pattern in ph_patterns:
        matches = re.findall(pattern, result.answer)
        for match in matches:
            ph_range = f"pH {match[0]}-{match[1]}"
            found_ph.append(ph_range)
    
    print(f"🔍 Найденные pH диапазоны: {found_ph}")
    
    for ph_claim in found_ph:
        fact_check = fact_checker.check_ph_claim(
            ph_claim,
            evidence_chunks,
            "YC5194"
        )
        
        status = "✅ ТОЧНО" if fact_check.is_accurate else "❌ НЕТОЧНО"
        print(f"   {ph_claim}: {status}")
        print(f"   Доказательство: {fact_check.evidence[:150]}...")
        print(f"   Уверенность: {fact_check.confidence:.2f}")
        print()

def compare_with_notebooklm():
    """Сравнивает ключевые факты с NotebookLM"""
    
    print("🆚 Сравнение с NotebookLM")
    print("=" * 30)
    
    notebooklm_facts = {
        "температурный_диапазон": "15-37°C",
        "происхождение": "ризосфера перца, Чинджу, Корея",
        "размер_клеток": "0,3-0,5 × 2,0-20 мкм",
        "pH_диапазон": "5,5-8,5",
        "оптимальная_температура": "28°C",
        "оптимальный_pH": "7,0-7,5"
    }
    
    print("📋 Эталонные факты от NotebookLM:")
    for key, value in notebooklm_facts.items():
        print(f"   {key}: {value}")
    
    print("\n💡 Задача: RAG система должна давать точно такие же факты!")

if __name__ == "__main__":
    print("🧪 Тестирование проверки фактов для YC5194")
    print("=" * 70)
    
    test_yc5194_facts()
    compare_with_notebooklm()
    
    print("\n🎯 Выводы:")
    print("1. Необходимо активировать FactChecker в основном коде")
    print("2. Система должна предупреждать о неточностях")
    print("3. Приоритет точности над полнотой ответа") 