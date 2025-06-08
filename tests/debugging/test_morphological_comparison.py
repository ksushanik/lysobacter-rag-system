#!/usr/bin/env python3
"""
Тестирование морфологического сравнения - ключевой тест для проверки улучшений
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lysobacter_rag.rag_pipeline import RAGPipeline

def test_morphological_comparison():
    """Тестирует ключевой запрос, который ранее провалился"""
    print("🧪 КЛЮЧЕВОЙ ТЕСТ: Сравнение морфологических характеристик")
    print("=" * 70)
    
    # Инициализация RAG системы
    rag = RAGPipeline()
    
    # Проблемный запрос
    query = "Сравните морфологические характеристики различных лизобактерий"
    
    print(f"🔍 Запрос: {query}")
    print("-" * 70)
    
    # Получаем ответ
    response = rag.ask_question(query)
    
    # Анализируем результат
    analysis_type = response.get('analysis_type', 'standard')
    species_count = response.get('species_analyzed', 0)
    confidence = response.get('confidence', 0)
    sources_count = response.get('num_sources_used', 0)
    
    print(f"📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print(f"   Тип анализа: {analysis_type}")
    print(f"   Проанализировано видов: {species_count}")
    print(f"   Уверенность: {confidence:.2f}")
    print(f"   Использовано источников: {sources_count}")
    
    # Оценка успешности
    success_criteria = {
        'comparative_analysis': analysis_type == 'comparative',
        'multiple_species': species_count >= 10,
        'high_confidence': confidence >= 0.5,
        'sufficient_sources': sources_count >= 10
    }
    
    print(f"\n✅ КРИТЕРИИ УСПЕШНОСТИ:")
    for criterion, passed in success_criteria.items():
        status = "✅ ПРОЙДЕН" if passed else "❌ НЕ ПРОЙДЕН"
        print(f"   {criterion}: {status}")
    
    overall_success = all(success_criteria.values())
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'✅ УСПЕХ' if overall_success else '❌ ТРЕБУЕТ ДОРАБОТКИ'}")
    
    # Показываем начало ответа
    answer = response.get('answer', '')
    if len(answer) > 500:
        preview = answer[:500] + "..."
    else:
        preview = answer
        
    print(f"\n💬 РАЗВЕРНУТЫЙ ОТВЕТ (превью):")
    print("-" * 70)
    print(preview)
    
    # Проверяем качество ответа
    quality_indicators = {
        'has_table': '|' in answer and 'Вид' in answer,
        'has_species_names': 'Lysobacter' in answer,
        'has_morphological_terms': any(term in answer.lower() for term in ['морфолог', 'форма', 'размер', 'клетк']),
        'structured_format': '###' in answer or '##' in answer,
        'has_conclusions': 'ВЫВОДЫ' in answer or 'выводы' in answer
    }
    
    print(f"\n📋 КАЧЕСТВО ОТВЕТА:")
    for indicator, present in quality_indicators.items():
        status = "✅" if present else "❌"
        print(f"   {status} {indicator}")
    
    quality_score = sum(quality_indicators.values()) / len(quality_indicators)
    print(f"\n📊 Оценка качества: {quality_score:.1%}")
    
    return {
        'success': overall_success,
        'quality_score': quality_score,
        'species_analyzed': species_count,
        'response': response
    }

def compare_with_old_system():
    """Сравнивает с предыдущим результатом системы"""
    print("\n\n🔄 СРАВНЕНИЕ С ПРЕДЫДУЩИМ РЕЗУЛЬТАТОМ")
    print("=" * 70)
    
    old_result = {
        'answer': "Предоставленный контекст не содержит информации о морфологических характеристиках различных видов лизобактерий.",
        'species_analyzed': 0,
        'has_table': False,
        'quality_score': 0.0
    }
    
    print("❌ СТАРЫЙ РЕЗУЛЬТАТ:")
    print(f"   Ответ: {old_result['answer']}")
    print(f"   Видов: {old_result['species_analyzed']}")
    print(f"   Качество: {old_result['quality_score']:.1%}")
    
    # Тестируем новую систему
    result = test_morphological_comparison()
    
    print(f"\n✅ НОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   Видов: {result['species_analyzed']}")
    print(f"   Качество: {result['quality_score']:.1%}")
    
    improvement = {
        'species_increase': result['species_analyzed'] - old_result['species_analyzed'],
        'quality_improvement': result['quality_score'] - old_result['quality_score'],
        'functionality_added': result['success']
    }
    
    print(f"\n🚀 УЛУЧШЕНИЯ:")
    print(f"   Количество видов: +{improvement['species_increase']}")
    print(f"   Качество ответа: +{improvement['quality_improvement']:.1%}")
    print(f"   Новая функциональность: {'Да' if improvement['functionality_added'] else 'Нет'}")
    
    return improvement

if __name__ == "__main__":
    compare_with_old_system() 