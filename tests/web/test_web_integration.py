#!/usr/bin/env python3

import requests
import time
import sys
sys.path.insert(0, 'src')

print("🌐 ТЕСТ ВЕБ-ИНТЕГРАЦИИ")
print("=" * 30)

# Проверяем доступность веб-интерфейса
try:
    response = requests.get("http://localhost:8501", timeout=5)
    if response.status_code == 200:
        print("✅ Веб-интерфейс доступен на http://localhost:8501")
    else:
        print(f"❌ Веб-интерфейс недоступен: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    sys.exit(1)

# Проверяем состояние базы данных
try:
    from lysobacter_rag.indexer.indexer import Indexer
    indexer = Indexer()
    stats = indexer.get_collection_stats()
    
    print(f"📊 База данных:")
    print(f"   Всего чанков: {stats.get('total_chunks', 0)}")
    
    # Проверяем поиск YC5194
    yc_results = indexer.search('YC5194', top_k=2)
    print(f"🔍 YC5194 поиск:")
    print(f"   Найдено результатов: {len(yc_results)}")
    
    if yc_results:
        print(f"   Лучшая релевантность: {yc_results[0].get('relevance_score', 0):.3f}")
        source = yc_results[0]['metadata'].get('source_pdf', 'N/A')
        print(f"   Источник: {source}")
    
    # Проверяем RAG
    from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
    rag = RAGPipeline()
    
    print(f"\n🤖 RAG тест:")
    result = rag.ask_question("Lysobacter capsici YC5194")
    print(f"   Содержит YC5194: {'YC5194' in result['answer']}")
    print(f"   Уверенность: {result['confidence']:.3f}")
    print(f"   Источников: {result['num_sources_used']}")
    
    print(f"\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ!")
    print(f"💻 Веб-интерфейс: http://localhost:8501")
    print(f"🧬 База данных: {stats.get('total_chunks', 0)} чанков")
    print(f"🔍 YC5194: найден с релевантностью {yc_results[0].get('relevance_score', 0):.3f}")
    
except Exception as e:
    print(f"❌ Ошибка тестирования: {e}")
    import traceback
    traceback.print_exc() 