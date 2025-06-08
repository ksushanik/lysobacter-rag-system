#!/usr/bin/env python3
"""
СРОЧНОЕ ДОБАВЛЕНИЕ YC5194 В БАЗУ
"""

import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.indexer.indexer import Indexer
from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
from lysobacter_rag.data_processor import DocumentChunk

def add_yc5194():
    """Добавляет файл с YC5194 в базу"""
    
    print("🎯 СРОЧНОЕ ДОБАВЛЕНИЕ YC5194")
    print("=" * 40)
    
    # Файл с YC5194
    yc5194_file = Path("data/Lysobacter capsici_sp_nov_with_antimicro.pdf")
    
    if not yc5194_file.exists():
        print(f"❌ Файл не найден: {yc5194_file}")
        return False
    
    print(f"📖 Обрабатываю: {yc5194_file.name}")
    
    # Инициализация
    extractor = AdvancedPDFExtractor(use_smart_chunking=True)
    indexer = Indexer()
    
    try:
        # Шаг 1: Извлечение
        print("📝 Извлекаю текст...")
        document = extractor.extract_document(yc5194_file)
        
        if not document.elements:
            print("❌ Нет элементов для обработки")
            return False
            
        print(f"✅ Извлечено {len(document.elements)} элементов")
        
        # Шаг 2: Умный чанкинг
        print("🧬 Применяю умный чанкинг...")
        chunks = extractor.get_smart_chunks(document)
        
        if not chunks:
            print("❌ Нет чанков")
            return False
        
        chunk_sizes = [len(chunk['content']) for chunk in chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes)
        print(f"✅ Создано {len(chunks)} чанков, ср. размер {avg_size:.0f} символов")
        
        # Шаг 3: Поиск YC5194 в чанках
        yc5194_chunks = []
        for i, chunk in enumerate(chunks):
            if "YC5194" in chunk['content']:
                yc5194_chunks.append(i)
                print(f"🎯 YC5194 найден в чанке {i}: {len(chunk['content'])} символов")
                print(f"   Превью: {chunk['content'][:150]}...")
        
        if not yc5194_chunks:
            print("⚠️ YC5194 не найден в чанках - возможно проблема с извлечением")
            # Покажем первые несколько чанков для диагностики
            for i, chunk in enumerate(chunks[:3]):
                print(f"   Чанк {i}: {chunk['content'][:100]}...")
        else:
            print(f"✅ YC5194 найден в {len(yc5194_chunks)} чанках")
        
        # Шаг 4: Конвертируем в DocumentChunk
        document_chunks = []
        for i, chunk in enumerate(chunks):
            doc_chunk = DocumentChunk(
                chunk_id=f"yc5194_{i}",
                text=chunk['content'],
                chunk_type=chunk['metadata'].get('chunk_type', 'text'),
                metadata=chunk['metadata']
            )
            document_chunks.append(doc_chunk)
        
        # Шаг 5: Индексация
        print(f"💾 Индексирую {len(document_chunks)} чанков...")
        success = indexer.index_chunks(document_chunks)
        
        if not success:
            print("❌ Ошибка индексации")
            return False
            
        print("✅ Индексация завершена")
        
        # Шаг 6: Тест поиска
        print("\n🔍 ТЕСТИРОВАНИЕ ПОИСКА:")
        
        results = indexer.search("Lysobacter capsici YC5194", top_k=3)
        
        if results:
            print(f"✅ Найдено {len(results)} результатов")
            for i, result in enumerate(results):
                rel = result['relevance_score']
                has_yc = "YC5194" in result['text']
                print(f"   {i+1}. Релевантность: {rel:.3f}, YC5194: {'✅' if has_yc else '❌'}")
                if has_yc:
                    print(f"      {result['text'][:100]}...")
        else:
            print("❌ Ничего не найдено")
            return False
        
        # Проверяем общее состояние базы
        stats = indexer.get_collection_stats()
        print(f"\n📊 База данных: {stats.get('total_chunks', 0)} чанков")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_yc5194()
    if success:
        print("\n🎉 YC5194 успешно добавлен в базу!")
    else:
        print("\n💥 Не удалось добавить YC5194")
    exit(0 if success else 1) 