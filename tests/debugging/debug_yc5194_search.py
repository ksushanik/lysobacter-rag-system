#!/usr/bin/env python3
"""
Диагностика проблемы с поиском штамма YC5194
"""
import sys
sys.path.insert(0, 'src')

from lysobacter_rag.indexer import Indexer

def main():
    print("🔍 ДИАГНОСТИКА ПОИСКА YC5194")
    print("=" * 50)
    
    indexer = Indexer()
    
    # 1. Поиск YC5194
    print("\n=== ПОИСК 'YC5194' ===")
    results = indexer.search('YC5194', top_k=5)
    print(f"Найдено результатов: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"\n{i+1}. Релевантность: {result['relevance_score']:.3f}")
        print(f"   Содержит 'YC5194': {'YC5194' in result['text']}")
        print(f"   Источник: {result['metadata'].get('source_pdf', 'неизвестен')}")
        print(f"   Первые 150 символов: {result['text'][:150]}...")
    
    # 2. Поиск Lysobacter capsici  
    print("\n\n=== ПОИСК 'Lysobacter capsici' ===")
    results2 = indexer.search('Lysobacter capsici', top_k=5)
    print(f"Найдено результатов: {len(results2)}")
    
    for i, result in enumerate(results2):
        print(f"\n{i+1}. Релевантность: {result['relevance_score']:.3f}")
        print(f"   Содержит 'capsici': {'capsici' in result['text'].lower()}")
        print(f"   Источник: {result['metadata'].get('source_pdf', 'неизвестен')}")
        print(f"   Первые 150 символов: {result['text'][:150]}...")
    
    # 3. Поиск точного файла
    print("\n\n=== ПОИСК В ФАЙЛЕ 'Lysobacter capsici_sp_nov_with_antimicro.pdf' ===")
    
    # Получаем статистику коллекции
    stats = indexer.get_collection_stats()
    print(f"\nСтатистика коллекции:")
    print(f"Всего чанков: {stats.get('total_documents', stats.get('document_count', 'неизвестно'))}")
    
    # Ищем чанки из конкретного файла
    collection = indexer.collection
    results_from_file = collection.get(
        where={"source_pdf": {"$contains": "capsici"}}
    )
    
    print(f"\nЧанки из файлов с 'capsici': {len(results_from_file['documents']) if results_from_file['documents'] else 0}")
    
    if results_from_file['documents']:
        for i, (doc, metadata) in enumerate(zip(results_from_file['documents'], results_from_file['metadatas'])):
            if 'YC5194' in doc:
                print(f"\n🎯 НАЙДЕН ЧАНК С YC5194 #{i+1}:")
                print(f"   Файл: {metadata.get('source_pdf', 'неизвестен')}")
                print(f"   Тип: {metadata.get('chunk_type', 'неизвестен')}")
                print(f"   Содержание: {doc[:300]}...")
                break
    
    # 4. Прямой поиск в документах
    print("\n\n=== ПРЯМОЙ ПОИСК В ДОКУМЕНТАХ ===")
    all_results = collection.get()
    yc5194_chunks = []
    
    if all_results['documents']:
        for i, (doc, metadata) in enumerate(zip(all_results['documents'], all_results['metadatas'])):
            if 'YC5194' in doc:
                yc5194_chunks.append({
                    'index': i,
                    'text': doc,
                    'metadata': metadata
                })
    
    print(f"Найдено чанков с YC5194: {len(yc5194_chunks)}")
    
    for i, chunk in enumerate(yc5194_chunks[:3]):  # Показываем первые 3
        print(f"\n📄 Чанк {i+1}:")
        print(f"   Файл: {chunk['metadata'].get('source_pdf', 'неизвестен')}")
        print(f"   Тип: {chunk['metadata'].get('chunk_type', 'неизвестен')}")
        print(f"   Длина: {len(chunk['text'])} символов")
        print(f"   Содержание: {chunk['text'][:200]}...")

if __name__ == "__main__":
    main() 