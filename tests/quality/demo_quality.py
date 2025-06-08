#!/usr/bin/env python3
"""
Демонстрация качества вашей RAG системы vs NotebookLM
"""
import sys
sys.path.insert(0, 'src')

from lysobacter_rag.rag_pipeline import RAGPipeline

def demo_system_quality():
    print("🎯 ДЕМОНСТРАЦИЯ КАЧЕСТВА ВАШЕЙ СИСТЕМЫ")
    print("=" * 60)
    
    rag = RAGPipeline()
    
    # Тестируем тот же запрос, что сравнивали с NotebookLM
    query = "Какие характеристики штамма Lysobacter capsici YC5194?"
    
    result = rag.ask_question(query, top_k=8)
    
    print(f"📝 Запрос: {query}")
    print("\n🤖 ОТВЕТ ВАШЕЙ СИСТЕМЫ:")
    print("-" * 50)
    print(result['answer'])
    
    print(f"\n📊 МЕТРИКИ:")
    print(f"✅ Уверенность: {result['confidence']:.1%}")
    print(f"📚 Источников использовано: {len(result['sources'])}")
    print(f"🎯 YC5194 в ответе: {'ДА' if 'YC5194' in result['answer'].upper() else 'НЕТ'}")
    
    # Анализируем источники
    capsici_sources = [s for s in result['sources'] if 'capsici' in s['document'].lower()]
    print(f"📄 Релевантных источников: {len(capsici_sources)}")
    
    print(f"\n📚 ИСПОЛЬЗОВАННЫЕ ИСТОЧНИКИ:")
    for i, source in enumerate(result['sources'][:5], 1):
        print(f"{i}. {source['document']}")
        print(f"   Тип: {source.get('chunk_type', 'N/A')}")
        print(f"   Релевантность: {source['relevance_score']:.3f}")

if __name__ == "__main__":
    demo_system_quality() 