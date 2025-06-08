#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

print("🔍 БЫСТРАЯ ПРОВЕРКА YC5194")
print("=" * 30)

try:
    from lysobacter_rag.indexer.indexer import Indexer
    from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
    
    # Проверяем индексер
    indexer = Indexer()
    stats = indexer.get_collection_stats()
    print(f'📊 Всего чанков: {stats.get("total_chunks", 0)}')
    
    # Поиск YC5194
    yc_results = indexer.search('YC5194', top_k=3)
    print(f'🔍 YC5194 найдено результатов: {len(yc_results)}')
    
    if yc_results:
        for i, result in enumerate(yc_results, 1):
            rel = result.get('relevance_score', 0)
            source = result['metadata'].get('source_pdf', 'N/A')
            chunk_type = result['metadata'].get('chunk_type', 'N/A')
            print(f'   {i}. {source} ({chunk_type}) - {rel:.3f}')
    
    # Тест RAG
    print(f'\n🤖 ТЕСТ RAG:')
    rag = RAGPipeline()
    query = "Lysobacter capsici YC5194 характеристики"
    response = rag.ask_question(query)
    
    print(f'💬 Содержит YC5194: {"YC5194" in response["answer"]}')
    print(f'📊 Источников: {response["num_sources_used"]}')
    print(f'⭐ Уверенность: {response["confidence"]:.3f}')
    
except Exception as e:
    print(f"❌ Ошибка: {e}") 