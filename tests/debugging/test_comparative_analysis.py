#!/usr/bin/env python3
"""
Тестирование сравнительного анализа
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lysobacter_rag.rag_pipeline import RAGPipeline

def test_comparative_query():
    """Тестирует сравнительный запрос"""
    print("🧪 ТЕСТИРОВАНИЕ СРАВНИТЕЛЬНОГО АНАЛИЗА")
    print("=" * 60)
    
    # Инициализация RAG системы
    rag = RAGPipeline()
    
    # Тестовый сравнительный запрос (тот же, что провалился)
    query = "Сравните морфологические характеристики различных лизобактерий"
    
    print(f"🔍 Запрос: {query}")
    print("-" * 60)
    
    # Получаем ответ
    response = rag.ask_question(query)
    
    print(f"📊 Тип анализа: {response.get('analysis_type', 'standard')}")
    print(f"🔬 Видов проанализировано: {response.get('species_analyzed', 'N/A')}")
    print(f"🎯 Уверенность: {response.get('confidence', 0):.2f}")
    print(f"📚 Источников использовано: {response.get('num_sources_used', 0)}")
    
    print(f"\n💬 ОТВЕТ СИСТЕМЫ:")
    print("=" * 60)
    print(response.get('answer', 'Ответ отсутствует'))
    
    print(f"\n📖 ИСТОЧНИКИ:")
    sources = response.get('sources', [])
    for i, source in enumerate(sources[:5], 1):
        print(f"{i}. {source.get('document', 'N/A')} (релевантность: {source.get('relevance_score', 0):.2f})")
    
    return response

def test_standard_vs_comparative():
    """Сравнивает стандартный и сравнительный подходы"""
    print("\n\n🔄 СРАВНЕНИЕ СТАНДАРТНОГО И СРАВНИТЕЛЬНОГО ПОДХОДОВ")
    print("=" * 60)
    
    rag = RAGPipeline()
    
    # Запросы для тестирования
    test_queries = [
        "Сравните морфологические характеристики различных лизобактерий",
        "Какие различия существуют между видами Lysobacter?",
        "Опишите общие черты рода Lysobacter",
        "Что известно о штамме YC5194?"  # Для сравнения - стандартный запрос
    ]
    
    for query in test_queries:
        print(f"\n🤔 Запрос: {query}")
        
        response = rag.ask_question(query)
        analysis_type = response.get('analysis_type', 'standard')
        
        print(f"   📊 Тип: {analysis_type}")
        print(f"   🎯 Уверенность: {response.get('confidence', 0):.2f}")
        print(f"   📚 Источников: {response.get('num_sources_used', 0)}")
        
        if analysis_type == 'comparative':
            print(f"   🔬 Видов: {response.get('species_analyzed', 0)}")
        
        # Показываем начало ответа
        answer = response.get('answer', '')
        preview = answer[:200] + "..." if len(answer) > 200 else answer
        print(f"   💬 Ответ: {preview}")
        print("-" * 40)

if __name__ == "__main__":
    test_comparative_query()
    test_standard_vs_comparative() 