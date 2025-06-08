#!/usr/bin/env python3
"""
ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ ВСЕХ PDF (88 файлов)
Включает YC5194 и все остальные штаммы
"""

import sys
import os
from pathlib import Path
import time
from tqdm import tqdm
import json

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.indexer.indexer import Indexer
from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
from lysobacter_rag.data_processor import DocumentChunk
from config import config

def full_reindex_all():
    """Полная переиндексация всех PDF файлов"""
    
    print("🧬 ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ ВСЕХ PDF ФАЙЛОВ")
    print("=" * 60)
    print("🎯 ЦЕЛЬ: Включить ВСЕ 88 файлов, включая YC5194")
    print()
    
    # Проверяем данные
    data_dir = Path("data")
    pdf_files = sorted(list(data_dir.glob("*.pdf")))
    
    print(f"📚 Найдено {len(pdf_files)} PDF файлов")
    
    # Проверяем, что YC5194 файл есть
    yc5194_file = data_dir / "Lysobacter capsici_sp_nov_with_antimicro.pdf"
    if yc5194_file.exists():
        print(f"✅ YC5194 файл найден: {yc5194_file.name}")
    else:
        print(f"❌ YC5194 файл НЕ НАЙДЕН!")
        return False
    
    # Инициализация
    print(f"\n🚀 Инициализация...")
    
    # Создаем экстрактор с умным чанкингом
    extractor = AdvancedPDFExtractor(use_smart_chunking=True)
    
    # Создаем индексер
    indexer = Indexer()
    
    # КРИТИЧНО: Полностью очищаем коллекцию
    print(f"\n🗑️ ПОЛНАЯ ОЧИСТКА старых данных...")
    try:
        indexer.delete_collection()
        print("✅ Старая коллекция удалена")
        
        # Пересоздаем коллекцию
        indexer = Indexer()  # Инициализируем заново
        print("✅ Новая коллекция создана")
        
    except Exception as e:
        print(f"⚠️ Предупреждение при очистке: {e}")
    
    # Статистика
    total_chunks = 0
    successful_files = 0
    failed_files = []
    processing_stats = {
        'total_files': len(pdf_files),
        'successful_files': 0,
        'failed_files': 0,
        'total_chunks': 0,
        'yc5194_processed': False,
        'chunk_sizes': [],
        'files_processed': []
    }
    
    # Обрабатываем файлы батчами по 10
    print(f"\n📄 Обработка {len(pdf_files)} файлов:")
    
    batch_size = 10
    all_document_chunks = []
    
    for batch_start in range(0, len(pdf_files), batch_size):
        batch_end = min(batch_start + batch_size, len(pdf_files))
        batch_files = pdf_files[batch_start:batch_end]
        
        print(f"\n📦 БАТЧ {batch_start//batch_size + 1}: файлы {batch_start+1}-{batch_end}")
        
        batch_chunks = []
        
        for i, pdf_file in enumerate(batch_files, batch_start + 1):
            try:
                print(f"\n{i:2d}/{len(pdf_files)} 📖 {pdf_file.name}")
                
                # Специальная отметка для YC5194
                if "capsici" in pdf_file.name.lower():
                    print(f"   🎯 ВАЖНО: Обрабатываем файл с YC5194!")
                
                # Шаг 1: Извлечение
                document = extractor.extract_document(pdf_file)
                
                if not document.elements:
                    print(f"   ⚠️ Пропускаем: нет элементов")
                    failed_files.append(pdf_file.name)
                    continue
                    
                print(f"   ✅ Извлечено {len(document.elements)} элементов")
                
                # Шаг 2: Умный чанкинг
                chunks = extractor.get_smart_chunks(document)
                
                if not chunks:
                    print(f"   ⚠️ Пропускаем: нет чанков")
                    failed_files.append(pdf_file.name)
                    continue
                
                # Анализируем размеры чанков
                chunk_sizes = [len(chunk['content']) for chunk in chunks]
                avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
                
                print(f"   🧬 Создано {len(chunks)} чанков, ср. размер {avg_size:.0f} символов")
                
                # Специальная проверка для YC5194
                if "capsici" in pdf_file.name.lower():
                    yc5194_found = False
                    for chunk in chunks:
                        if "YC5194" in chunk['content']:
                            yc5194_found = True
                            print(f"   🎯 YC5194 НАЙДЕН в чанке! Размер: {len(chunk['content'])} символов")
                            break
                    
                    if yc5194_found:
                        processing_stats['yc5194_processed'] = True
                        print(f"   ✅ YC5194 успешно включен в базу!")
                    else:
                        print(f"   ⚠️ YC5194 не найден в чанках - проверим содержимое")
                
                # Шаг 3: Конвертируем в DocumentChunk
                for j, chunk in enumerate(chunks):
                    doc_chunk = DocumentChunk(
                        chunk_id=f"{pdf_file.stem}_{j}",
                        text=chunk['content'],
                        chunk_type=chunk['metadata'].get('chunk_type', 'text'),
                        metadata=chunk['metadata']
                    )
                    batch_chunks.append(doc_chunk)
                
                # Статистика
                processing_stats['chunk_sizes'].extend(chunk_sizes)
                processing_stats['files_processed'].append({
                    'filename': pdf_file.name,
                    'chunks': len(chunks),
                    'avg_size': avg_size
                })
                
                successful_files += 1
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                failed_files.append(pdf_file.name)
                continue
        
        # Индексируем батч
        if batch_chunks:
            print(f"\n💾 Индексация батча: {len(batch_chunks)} чанков...")
            try:
                success = indexer.index_chunks(batch_chunks)
                if success:
                    total_chunks += len(batch_chunks)
                    all_document_chunks.extend(batch_chunks)
                    print(f"   ✅ Батч проиндексирован: {len(batch_chunks)} чанков")
                else:
                    print(f"   ❌ Ошибка индексации батча")
            except Exception as e:
                print(f"   ❌ Критическая ошибка батча: {e}")
    
    # Финальная статистика
    processing_stats['successful_files'] = successful_files
    processing_stats['failed_files'] = len(failed_files)
    processing_stats['total_chunks'] = total_chunks
    
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   ✅ Успешно обработано: {successful_files}/{len(pdf_files)} файлов")
    print(f"   💾 Всего чанков: {total_chunks}")
    print(f"   🎯 YC5194 обработан: {'✅ ДА' if processing_stats['yc5194_processed'] else '❌ НЕТ'}")
    
    if processing_stats['chunk_sizes']:
        avg_chunk_size = sum(processing_stats['chunk_sizes']) / len(processing_stats['chunk_sizes'])
        print(f"   📏 Средний размер чанка: {avg_chunk_size:.0f} символов")
    
    if failed_files:
        print(f"   ⚠️ Проблемные файлы: {len(failed_files)}")
        for file in failed_files[:5]:  # Показываем первые 5
            print(f"      - {file}")
    
    # Проверка результата
    print(f"\n🔍 ФИНАЛЬНАЯ ПРОВЕРКА:")
    
    stats = indexer.get_collection_stats()
    final_chunks = stats.get('total_chunks', 0)
    print(f"   📦 Чанков в базе: {final_chunks}")
    
    # Критический тест на YC5194
    print(f"\n🧪 КРИТИЧЕСКИЙ ТЕСТ НА YC5194:")
    try:
        yc_results = indexer.search("Lysobacter capsici YC5194", top_k=5)
        if yc_results:
            best_relevance = yc_results[0]['relevance_score']
            print(f"   ✅ YC5194 НАЙДЕН! Релевантность: {best_relevance:.3f}")
            print(f"   📝 Первые 100 символов: {yc_results[0]['text'][:100]}...")
            
            # Проверяем несколько результатов
            for i, result in enumerate(yc_results[:3]):
                if "YC5194" in result['text']:
                    print(f"   🎯 Результат {i+1}: СОДЕРЖИТ YC5194 (релевантность {result['relevance_score']:.3f})")
                else:
                    print(f"   ⚠️ Результат {i+1}: НЕ содержит YC5194 (релевантность {result['relevance_score']:.3f})")
            
            success = True
        else:
            print(f"   ❌ YC5194 НЕ НАЙДЕН В БАЗЕ!")
            success = False
            
    except Exception as e:
        print(f"   ❌ Ошибка поиска YC5194: {e}")
        success = False
    
    # Сохраняем отчет
    report_file = "full_reindex_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(processing_stats, f, ensure_ascii=False, indent=2)
    print(f"\n📋 Отчет сохранен: {report_file}")
    
    return success

if __name__ == "__main__":
    try:
        print("🚀 НАЧИНАЮ ПОЛНУЮ ПЕРЕИНДЕКСАЦИЮ ВСЕХ PDF...")
        success = full_reindex_all()
        
        if success:
            print(f"\n🎉 УСПЕХ: Полная переиндексация завершена!")
            print(f"   YC5194 теперь должен быть найден в системе")
        else:
            print(f"\n⚠️ ПРОБЛЕМЫ: Требуется дополнительная диагностика")
        
        exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1) 