#!/usr/bin/env python3
"""
ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ: Гарантированная очистка + умный чанкинг
"""

import sys
import os
from pathlib import Path
import time
from tqdm import tqdm

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.indexer.indexer import Indexer
from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
from lysobacter_rag.data_processor import DocumentChunk
from config import config

def complete_reindex():
    """Полная переиндексация с гарантированной очисткой"""
    
    print("🧬 ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ С УМНЫМ ЧАНКИНГОМ")
    print("=" * 60)
    print("🎯 ЦЕЛЬ: Чанки по 300-350 символов для качественных ответов")
    print()
    
    # Проверяем данные
    data_dir = Path("data")
    pdf_files = sorted(list(data_dir.glob("*.pdf")))[:10]  # ОГРАНИЧИВАЕМ 10 файлами для теста
    
    print(f"📚 Обрабатываем {len(pdf_files)} PDF файлов (тестовая выборка)")
    
    # Инициализация
    print("\n🚀 Инициализация...")
    
    # Создаем экстрактор с умным чанкингом
    extractor = AdvancedPDFExtractor(use_smart_chunking=True)
    
    # Создаем индексер
    indexer = Indexer()
    
    # КРИТИЧНО: Полностью очищаем коллекцию
    print("\n🗑️ ПОЛНАЯ ОЧИСТКА старых данных...")
    try:
        indexer.delete_collection()
        print("✅ Старая коллекция удалена")
        
        # Пересоздаем коллекцию
        indexer = Indexer()  # Инициализируем заново
        print("✅ Новая коллекция создана")
        
    except Exception as e:
        print(f"⚠️ Предупреждение при очистке: {e}")
    
    # Обрабатываем файлы
    all_document_chunks = []
    successful_files = 0
    
    print(f"\n📄 Обработка файлов:")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            print(f"\n{i:2d}/{len(pdf_files)} 📖 {pdf_file.name}")
            
            # Шаг 1: Извлечение
            document = extractor.extract_document(pdf_file)
            
            if not document.elements:
                print(f"   ⚠️ Пропускаем: нет элементов")
                continue
                
            print(f"   ✅ Извлечено {len(document.elements)} элементов")
            
            # Шаг 2: Умный чанкинг
            chunks = extractor.get_smart_chunks(document)
            
            if not chunks:
                print(f"   ⚠️ Пропускаем: нет чанков")
                continue
            
            # Анализируем размеры чанков
            chunk_sizes = [len(chunk['content']) for chunk in chunks]
            avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
            
            print(f"   🧬 Создано {len(chunks)} чанков, ср. размер {avg_size:.0f} символов")
            
            # Проверяем, что умный чанкинг сработал
            if avg_size > 1000:
                print(f"   ⚠️ ПРЕДУПРЕЖДЕНИЕ: Чанки слишком большие!")
            elif avg_size < 100:
                print(f"   ⚠️ ПРЕДУПРЕЖДЕНИЕ: Чанки слишком маленькие!")
            else:
                print(f"   ✅ Размер чанков оптимальный")
            
            # Шаг 3: Конвертируем в DocumentChunk
            for j, chunk in enumerate(chunks):
                doc_chunk = DocumentChunk(
                    chunk_id=f"{pdf_file.stem}_{j}",
                    text=chunk['content'],
                    chunk_type=chunk['metadata'].get('chunk_type', 'text'),
                    metadata=chunk['metadata']
                )
                all_document_chunks.append(doc_chunk)
            
            successful_files += 1
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
    
    # Финальная индексация
    print(f"\n💾 ФИНАЛЬНАЯ ИНДЕКСАЦИЯ:")
    print(f"   Всего чанков для индексации: {len(all_document_chunks)}")
    
    if all_document_chunks:
        try:
            success = indexer.index_chunks(all_document_chunks)
            
            if success:
                print(f"   ✅ Все чанки успешно проиндексированы!")
            else:
                print(f"   ❌ Ошибка при индексации")
                return False
                
        except Exception as e:
            print(f"   ❌ Критическая ошибка индексации: {e}")
            return False
    
    # Проверка результата
    print(f"\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА:")
    
    stats = indexer.get_collection_stats()
    final_chunks = stats.get('total_chunks', 0)
    print(f"   📦 Чанков в базе: {final_chunks}")
    
    # Анализируем размеры чанков в базе
    try:
        test_results = indexer.search("Lysobacter", top_k=10)
        if test_results:
            sizes = [len(r['text']) for r in test_results]
            avg_db_size = sum(sizes) / len(sizes)
            print(f"   📏 Средний размер чанка в базе: {avg_db_size:.0f} символов")
            
            if 200 <= avg_db_size <= 500:
                print(f"   🎉 ОТЛИЧНО: Размеры чанков оптимальны!")
                size_quality = "excellent"
            elif avg_db_size < 1000:
                print(f"   ✅ ХОРОШО: Размеры чанков приемлемы")
                size_quality = "good"
            else:
                print(f"   ❌ ПЛОХО: Чанки всё ещё слишком большие")
                size_quality = "poor"
        else:
            print(f"   ⚠️ Нет результатов поиска")
            size_quality = "unknown"
            
    except Exception as e:
        print(f"   ❌ Ошибка проверки: {e}")
        size_quality = "error"
    
    # Тест на YC5194
    print(f"\n🧪 ТЕСТ НА YC5194:")
    try:
        yc_results = indexer.search("Lysobacter capsici YC5194", top_k=3)
        if yc_results:
            best_relevance = yc_results[0]['relevance_score']
            print(f"   ✅ YC5194 найден! Релевантность: {best_relevance:.3f}")
            
            if best_relevance > 0.5:
                print(f"   🎉 ОТЛИЧНАЯ релевантность!")
                yc_quality = "excellent"
            elif best_relevance > 0.3:
                print(f"   ✅ Хорошая релевантность")
                yc_quality = "good"
            else:
                print(f"   ⚠️ Низкая релевантность")
                yc_quality = "poor"
        else:
            print(f"   ❌ YC5194 НЕ НАЙДЕН")
            yc_quality = "not_found"
            
    except Exception as e:
        print(f"   ❌ Ошибка поиска YC5194: {e}")
        yc_quality = "error"
    
    # Итоговая оценка
    print(f"\n🏆 ИТОГОВАЯ ОЦЕНКА:")
    
    if size_quality == "excellent" and yc_quality == "excellent":
        print(f"   🎉 ИДЕАЛЬНО: Система готова!")
        return True
    elif size_quality in ["excellent", "good"] and yc_quality in ["excellent", "good"]:
        print(f"   ✅ ХОРОШО: Значительные улучшения")
        return True
    else:
        print(f"   ⚠️ ТРЕБУЕТСЯ ДОРАБОТКА")
        print(f"      Размеры чанков: {size_quality}")
        print(f"      Поиск YC5194: {yc_quality}")
        return False

if __name__ == "__main__":
    try:
        success = complete_reindex()
        if success:
            print(f"\n🚀 ГОТОВО: Переиндексация успешна!")
        else:
            print(f"\n⚠️ ВНИМАНИЕ: Требуются дополнительные исправления")
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1) 