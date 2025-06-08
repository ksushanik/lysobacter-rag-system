#!/usr/bin/env python3
"""
РЕВОЛЮЦИОННАЯ ПЕРЕИНДЕКСАЦИЯ: Умный чанкинг для всех PDF
Эта переиндексация решит проблему качества ответов RAG
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
from config import config

def reindex_with_smart_chunking():
    """Полная переиндексация с умным чанкингом"""
    
    print("🧬 РЕВОЛЮЦИОННАЯ ПЕРЕИНДЕКСАЦИЯ С УМНЫМ ЧАНКИНГОМ")
    print("=" * 70)
    print("💡 Цель: Создать качественные чанки для улучшения ответов RAG")
    print()
    
    # Проверяем данные
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Папка data/ не найдена!")
        return False
    
    pdf_files = sorted(list(data_dir.glob("*.pdf")))
    if not pdf_files:
        print("❌ PDF файлы не найдены в папке data/!")
        return False
    
    print(f"📚 Найдено {len(pdf_files)} PDF файлов для переиндексации")
    
    # Инициализация
    print("\n🚀 Инициализация системы...")
    
    # Создаем продвинутый экстрактор с умным чанкингом
    extractor = AdvancedPDFExtractor(use_smart_chunking=True)
    print("✅ Продвинутый экстрактор с умным чанкингом готов")
    
    # Создаем индексер
    indexer = Indexer()
    print("✅ Индексер готов")
    
    # Очищаем старую коллекцию
    print("\n🗑️ Очистка старых данных...")
    try:
        indexer.clear_collection()
        print("✅ Старые данные очищены")
    except Exception as e:
        print(f"⚠️ Предупреждение при очистке: {e}")
    
    # Статистика
    total_chunks = 0
    total_documents = 0
    total_errors = 0
    processing_stats = {
        'successful_files': [],
        'failed_files': [],
        'chunking_stats': {
            'total_elements': 0,
            'total_chunks': 0,
            'avg_chunk_size': 0,
            'critical_chunks': 0,
            'high_importance_chunks': 0
        }
    }
    
    start_time = time.time()
    
    # Обрабатываем файлы
    print(f"\n📄 Обработка PDF файлов:")
    print("-" * 50)
    
    for i, pdf_file in enumerate(tqdm(pdf_files, desc="Переиндексация"), 1):
        try:
            print(f"\n{i:2d}/{len(pdf_files)} 📖 {pdf_file.name}")
            
            # Шаг 1: Извлечение с продвинутым экстрактором
            document = extractor.extract_document(pdf_file)
            
            if not document.elements:
                print(f"   ⚠️ Не удалось извлечь элементы")
                processing_stats['failed_files'].append({
                    'file': pdf_file.name,
                    'reason': 'no_elements_extracted'
                })
                continue
            
            print(f"   ✅ Извлечено {len(document.elements)} элементов")
            processing_stats['chunking_stats']['total_elements'] += len(document.elements)
            
            # Шаг 2: Применение умного чанкинга
            chunks = extractor.get_smart_chunks(document)
            
            if not chunks:
                print(f"   ⚠️ Не удалось создать чанки")
                processing_stats['failed_files'].append({
                    'file': pdf_file.name,
                    'reason': 'no_chunks_created'
                })
                continue
            
            print(f"   🧬 Создано {len(chunks)} умных чанков")
            
            # Анализируем чанки
            chunk_sizes = [len(chunk['content']) for chunk in chunks]
            avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
            
            importance_counts = {}
            for chunk in chunks:
                importance = chunk['metadata'].get('scientific_importance', 'unknown')
                importance_counts[importance] = importance_counts.get(importance, 0) + 1
            
            print(f"   📊 Средний размер чанка: {avg_chunk_size:.0f} символов")
            print(f"   🎯 Важность: {importance_counts}")
            
            # Обновляем статистику
            processing_stats['chunking_stats']['total_chunks'] += len(chunks)
            processing_stats['chunking_stats']['critical_chunks'] += importance_counts.get('critical', 0)
            processing_stats['chunking_stats']['high_importance_chunks'] += importance_counts.get('high', 0)
            
            # Шаг 3: Конвертируем в DocumentChunk для индексации
            from lysobacter_rag.data_processor import DocumentChunk
            
            document_chunks = []
            for i, chunk in enumerate(chunks):
                doc_chunk = DocumentChunk(
                    chunk_id=f"{pdf_file.stem}_{i}",
                    text=chunk['content'],
                    chunk_type=chunk['metadata'].get('chunk_type', 'text'),
                    metadata=chunk['metadata']
                )
                document_chunks.append(doc_chunk)
            
            # Индексируем все чанки батчем
            try:
                success = indexer.index_chunks(document_chunks)
                if success:
                    successful_chunks = len(document_chunks)
                    print(f"   💾 Успешно проиндексировано {successful_chunks} чанков")
                else:
                    successful_chunks = 0
                    print(f"   ❌ Ошибка индексации батча")
            except Exception as e:
                successful_chunks = 0
                print(f"   ❌ Критическая ошибка индексации: {e}")
            
            total_chunks += successful_chunks
            total_documents += 1
            processing_stats['successful_files'].append({
                'file': pdf_file.name,
                'elements': len(document.elements),
                'chunks': len(chunks),
                'indexed_chunks': successful_chunks,
                'avg_chunk_size': avg_chunk_size,
                'importance_distribution': importance_counts
            })
            
        except Exception as e:
            print(f"   ❌ Критическая ошибка: {e}")
            total_errors += 1
            processing_stats['failed_files'].append({
                'file': pdf_file.name,
                'reason': f'critical_error: {str(e)}'
            })
            continue
    
    # Финальная статистика
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n🎉 ПЕРЕИНДЕКСАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 50)
    
    print(f"⏱️ Время обработки: {processing_time:.1f} секунд")
    print(f"📚 Обработано документов: {total_documents}/{len(pdf_files)}")
    print(f"📦 Всего создано чанков: {total_chunks}")
    print(f"❌ Ошибок: {total_errors}")
    
    if total_chunks > 0:
        avg_system_chunk_size = processing_stats['chunking_stats']['total_chunks']
        if avg_system_chunk_size > 0:
            avg_system_chunk_size = processing_stats['chunking_stats']['total_elements'] / avg_system_chunk_size
        
        print(f"\n📊 СТАТИСТИКА УМНОГО ЧАНКИНГА:")
        print(f"   📈 Всего элементов извлечено: {processing_stats['chunking_stats']['total_elements']}")
        print(f"   🧬 Всего чанков создано: {processing_stats['chunking_stats']['total_chunks']}")
        print(f"   📏 Коэффициент чанкинга: {processing_stats['chunking_stats']['total_chunks'] / processing_stats['chunking_stats']['total_elements']:.1f}x")
        print(f"   🎯 Критически важных чанков: {processing_stats['chunking_stats']['critical_chunks']}")
        print(f"   ⭐ Высокой важности: {processing_stats['chunking_stats']['high_importance_chunks']}")
        
        important_ratio = (processing_stats['chunking_stats']['critical_chunks'] + 
                          processing_stats['chunking_stats']['high_importance_chunks']) / processing_stats['chunking_stats']['total_chunks']
        print(f"   💡 Доля важных чанков: {important_ratio:.1%}")
    
    # Проверяем результат
    print(f"\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА:")
    
    final_stats = indexer.get_collection_stats()
    print(f"   💾 Чанков в базе: {final_stats.get('total_chunks', 0)}")
    
    # Тест поиска
    test_queries = [
        "Lysobacter capsici YC5194",
        "temperature range growth",
        "G+C content DNA",
        "type strain isolated"
    ]
    
    print(f"   🔍 Тестирование поиска:")
    search_quality_scores = []
    
    for query in test_queries:
        try:
            results = indexer.search(query, top_k=3)
            if results:
                avg_relevance = sum(r['relevance_score'] for r in results) / len(results)
                search_quality_scores.append(avg_relevance)
                status = "✅" if avg_relevance > 0.4 else "⚠️" if avg_relevance > 0.2 else "❌"
                print(f"      {status} '{query}': {avg_relevance:.3f}")
            else:
                print(f"      ❌ '{query}': НЕ НАЙДЕН")
                search_quality_scores.append(0.0)
        except Exception as e:
            print(f"      ❌ '{query}': ОШИБКА {e}")
            search_quality_scores.append(0.0)
    
    avg_search_quality = sum(search_quality_scores) / len(search_quality_scores) if search_quality_scores else 0
    
    # Финальная оценка
    print(f"\n🏆 ИТОГОВАЯ ОЦЕНКА:")
    print(f"   📊 Средняя релевантность поиска: {avg_search_quality:.3f}")
    print(f"   📚 Успешность обработки: {total_documents/len(pdf_files):.1%}")
    print(f"   💾 Всего чанков в системе: {final_stats.get('total_chunks', 0)}")
    
    if avg_search_quality >= 0.4 and total_documents >= len(pdf_files) * 0.8:
        print(f"   🎉 УСПЕХ: Система готова к работе!")
        success = True
    elif avg_search_quality >= 0.3 and total_documents >= len(pdf_files) * 0.6:
        print(f"   ✅ ХОРОШО: Система работает приемлемо")
        success = True
    else:
        print(f"   ⚠️ ПРОБЛЕМЫ: Требуется дополнительная настройка")
        success = False
    
    # Сохраняем подробную статистику
    print(f"\n💾 Сохранение отчёта...")
    
    report = {
        'timestamp': time.time(),
        'processing_time': processing_time,
        'total_files': len(pdf_files),
        'successful_files': total_documents,
        'failed_files': total_errors,
        'total_chunks': total_chunks,
        'avg_search_quality': avg_search_quality,
        'chunking_stats': processing_stats['chunking_stats'],
        'successful_files_details': processing_stats['successful_files'],
        'failed_files_details': processing_stats['failed_files']
    }
    
    import json
    with open('smart_chunking_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Отчёт сохранён: smart_chunking_report.json")
    
    return success

if __name__ == "__main__":
    try:
        success = reindex_with_smart_chunking()
        if success:
            print(f"\n🚀 ГОТОВО: Система переиндексирована с умным чанкингом!")
            print(f"   Теперь можно тестировать улучшенное качество ответов")
        else:
            print(f"\n⚠️ ВНИМАНИЕ: Переиндексация завершена с проблемами")
            print(f"   Рекомендуется проверить логи и повторить процесс")
        
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Переиндексация прервана пользователем")
        exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1) 