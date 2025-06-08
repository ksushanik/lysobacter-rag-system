#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline

print("🔬 КОНСОЛЬНЫЙ ТЕСТ YC5194")
print("=" * 40)

rag = RAGPipeline()
query = "Какие характеристики штамма Lysobacter capsici YC5194?"

print(f"❓ Вопрос: {query}")
print("\n⏳ Обрабатываю...")

response = rag.ask_question(query)

print(f"\n💬 ОТВЕТ:")
print("=" * 40)
print(response["answer"])
print("=" * 40)

print(f"\n📊 МЕТРИКИ:")
print(f"🎯 Источников использовано: {response['num_sources_used']}")
print(f"⭐ Уверенность: {response['confidence']:.3f}")
print(f"🔍 Содержит YC5194: {'YC5194' in response['answer']}")

if response['sources']:
    print(f"\n📚 ИСТОЧНИКИ:")
    for i, source in enumerate(response['sources'][:3], 1):
        pdf = source['metadata'].get('source_pdf', 'N/A')
        chunk_type = source['metadata'].get('chunk_type', 'N/A')
        score = source.get('relevance_score', 0)
        print(f"   {i}. {pdf} ({chunk_type}) - {score:.3f}") 