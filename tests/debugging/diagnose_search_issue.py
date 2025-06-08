#!/usr/bin/env python3
"""
Диагностика проблемы семантического поиска
"""
import sys
sys.path.insert(0, 'src')

from lysobacter_rag.indexer import Indexer
import numpy as np

def main():
    print("🔬 ДИАГНОСТИКА СЕМАНТИЧЕСКОГО ПОИСКА")
    print("=" * 50)
    
    indexer = Indexer()
    collection = indexer.collection
    
    # Получаем эмбеддинг для запроса YC5194
    query_embedding = indexer.embedding_model.encode(["YC5194"])
    
    print(f"🧬 Эмбеддинг для 'YC5194' создан: {len(query_embedding[0])} размерность")
    
    # Делаем поиск через ChromaDB напрямую
    print("\n=== ПОИСК ЧЕРЕЗ CHROMADB НАПРЯМУЮ ===")
    chroma_results = collection.query(
        query_embeddings=[query_embedding[0].tolist()],
        n_results=10,
        include=['documents', 'metadatas', 'distances']
    )
    
    print(f"Найдено результатов через ChromaDB: {len(chroma_results['documents'][0])}")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        chroma_results['documents'][0],
        chroma_results['metadatas'][0], 
        chroma_results['distances'][0]
    )):
        contains_yc = 'YC5194' in doc
        print(f"\n{i+1}. Дистанция: {distance:.3f}")
        print(f"   Содержит YC5194: {contains_yc}")
        print(f"   Файл: {metadata.get('source_pdf', 'неизвестен')}")
        print(f"   Первые 100 символов: {doc[:100]}...")
    
    # Теперь поиск через наш индексер
    print("\n\n=== ПОИСК ЧЕРЕЗ НАШ INDEXER ===")
    indexer_results = indexer.search("YC5194", top_k=10)
    
    print(f"Найдено результатов через indexer: {len(indexer_results)}")
    
    for i, result in enumerate(indexer_results):
        contains_yc = 'YC5194' in result['text']
        print(f"\n{i+1}. Релевантность: {result['relevance_score']:.3f}")
        print(f"   Содержит YC5194: {contains_yc}")
        print(f"   Файл: {result['metadata'].get('source_pdf', 'неизвестен')}")
        print(f"   Первые 100 символов: {result['text'][:100]}...")
    
    # Тестируем другие запросы
    print("\n\n=== ТЕСТИРУЕМ ДРУГИЕ ЗАПРОСЫ ===")
    test_queries = [
        "Lysobacter capsici YC5194",
        "штамм YC5194", 
        "characteristics YC5194",
        "YC5194 pepper rhizosphere"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Запрос: '{query}'")
        results = indexer.search(query, top_k=3)
        
        yc_found = False
        for result in results:
            if 'YC5194' in result['text']:
                yc_found = True
                break
                
        print(f"   Найден YC5194: {yc_found}")
        if results:
            print(f"   Лучший результат: {results[0]['relevance_score']:.3f}")
            print(f"   Содержит YC5194: {'YC5194' in results[0]['text']}")
    
    # Проверим эмбеддинги известных чанков с YC5194
    print("\n\n=== АНАЛИЗ ЭМБЕДДИНГОВ ЧАНКОВ С YC5194 ===")
    
    all_data = collection.get()
    yc_chunks = []
    yc_indices = []
    
    for i, doc in enumerate(all_data['documents']):
        if 'YC5194' in doc:
            yc_chunks.append(doc)
            yc_indices.append(i)
    
    print(f"Проанализируем первые 5 из {len(yc_chunks)} чанков с YC5194...")
    
    # Получаем эмбеддинги для этих чанков
    for i, (chunk, idx) in enumerate(zip(yc_chunks[:5], yc_indices[:5])):
        chunk_embedding = indexer.embedding_model.encode([chunk])
        
        # Вычисляем косинусное сходство с запросом "YC5194"
        similarity = np.dot(query_embedding[0], chunk_embedding[0]) / (
            np.linalg.norm(query_embedding[0]) * np.linalg.norm(chunk_embedding[0])
        )
        
        metadata = all_data['metadatas'][idx]
        
        print(f"\n📄 Чанк {i+1}:")
        print(f"   Косинусное сходство с 'YC5194': {similarity:.3f}")
        print(f"   Файл: {metadata.get('source_pdf', 'неизвестен')}")
        print(f"   Тип: {metadata.get('chunk_type', 'неизвестен')}")
        print(f"   Первые 150 символов: {chunk[:150]}...")

if __name__ == "__main__":
    main() 