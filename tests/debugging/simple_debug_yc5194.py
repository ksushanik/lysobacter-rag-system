#!/usr/bin/env python3
"""
Упрощенная диагностика YC5194
"""
import sys
sys.path.insert(0, 'src')

from lysobacter_rag.indexer import Indexer

def main():
    print("🔍 ДИАГНОСТИКА YC5194")
    print("=" * 40)
    
    indexer = Indexer()
    collection = indexer.collection
    
    # Получаем все документы
    print("📊 Получаем все документы...")
    all_data = collection.get()
    
    total_docs = len(all_data['documents']) if all_data['documents'] else 0
    print(f"Всего чанков в базе: {total_docs}")
    
    # Ищем YC5194
    yc5194_count = 0
    capsici_count = 0
    
    print("\n🔍 Ищем упоминания YC5194 и capsici...")
    
    for i, doc in enumerate(all_data['documents']):
        if 'YC5194' in doc:
            yc5194_count += 1
            metadata = all_data['metadatas'][i]
            print(f"\n🎯 НАЙДЕН YC5194 #{yc5194_count}:")
            print(f"   Файл: {metadata.get('source_pdf', 'неизвестен')}")
            print(f"   Тип: {metadata.get('chunk_type', 'неизвестен')}")
            print(f"   Первые 200 символов: {doc[:200]}...")
            
        if 'capsici' in doc.lower():
            capsici_count += 1
            if capsici_count <= 3:  # Показываем только первые 3
                metadata = all_data['metadatas'][i]
                print(f"\n📄 Capsici #{capsici_count}:")
                print(f"   Файл: {metadata.get('source_pdf', 'неизвестен')}")
                print(f"   Содержит YC5194: {'YC5194' in doc}")
                print(f"   Первые 150 символов: {doc[:150]}...")
    
    print(f"\n📈 ИТОГИ:")
    print(f"Всего чанков: {total_docs}")
    print(f"Чанков с YC5194: {yc5194_count}")
    print(f"Чанков с capsici: {capsici_count}")
    
    # Проверим также файлы
    files_with_capsici = set()
    for metadata in all_data['metadatas']:
        source = metadata.get('source_pdf', '')
        if 'capsici' in source.lower():
            files_with_capsici.add(source)
    
    print(f"\nФайлы с 'capsici' в названии: {len(files_with_capsici)}")
    for file in files_with_capsici:
        print(f"  - {file}")

if __name__ == "__main__":
    main() 