#!/usr/bin/env python3
"""
ТЕСТ: Интеграция умного чанкинга с продвинутым экстрактором
"""

import sys
import os
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor

def test_smart_chunking():
    """Тестирует умный чанкинг на реальном PDF"""
    
    print("🧬 ТЕСТ УМНОГО ЧАНКИНГА")
    print("=" * 60)
    
    # Инициализируем экстрактор с умным чанкингом
    extractor = AdvancedPDFExtractor(use_smart_chunking=True)
    
    # Находим тестовый PDF
    data_dir = Path("data")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Не найдены PDF файлы в папке data/")
        return
    
    # Берем первый PDF для теста
    test_pdf = pdf_files[0]
    print(f"📄 Тестируем на файле: {test_pdf.name}")
    
    # Извлекаем документ
    print("\n🚀 Шаг 1: Извлечение с продвинутым экстрактором")
    document = extractor.extract_document(test_pdf)
    
    print(f"   ✅ Извлечено {len(document.elements)} элементов")
    print(f"   📊 Статистика:")
    print(f"      - Страниц: {document.total_pages}")
    print(f"      - Текстовых элементов: {document.extraction_stats.get('text_elements', 0)}")
    print(f"      - Табличных элементов: {document.extraction_stats.get('table_elements', 0)}")
    print(f"      - Качество: {document.extraction_stats.get('quality_score', 0):.1f}%")
    
    # Применяем умный чанкинг
    print("\n🧬 Шаг 2: Применение умного чанкинга")
    smart_chunks = extractor.get_smart_chunks(document)
    
    print(f"   ✅ Создано {len(smart_chunks)} умных чанков")
    
    # Анализируем результаты
    print("\n📊 Шаг 3: Анализ результатов умного чанкинга")
    
    total_length = sum(len(chunk['content']) for chunk in smart_chunks)
    avg_length = total_length / len(smart_chunks) if smart_chunks else 0
    
    print(f"   📈 Общая длина текста: {total_length:,} символов")
    print(f"   📏 Средняя длина чанка: {avg_length:.0f} символов")
    
    # Группируем по типам
    chunk_types = {}
    importance_levels = {}
    
    for chunk in smart_chunks:
        chunk_type = chunk['metadata'].get('chunk_type', 'unknown')
        importance = chunk['metadata'].get('scientific_importance', 'unknown')
        
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        importance_levels[importance] = importance_levels.get(importance, 0) + 1
    
    print(f"\n   📋 Распределение по типам:")
    for chunk_type, count in chunk_types.items():
        print(f"      - {chunk_type}: {count}")
    
    print(f"\n   🎯 Распределение по важности:")
    for importance, count in importance_levels.items():
        print(f"      - {importance}: {count}")
    
    # Показываем примеры чанков
    print("\n🔍 Шаг 4: Примеры умных чанков")
    
    # Находим самые важные чанки
    important_chunks = [c for c in smart_chunks 
                       if c['metadata'].get('scientific_importance') in ['critical', 'high']]
    
    if important_chunks:
        print(f"\n   🎯 Важные чанки ({len(important_chunks)} из {len(smart_chunks)}):")
        
        for i, chunk in enumerate(important_chunks[:3], 1):
            importance = chunk['metadata'].get('scientific_importance', 'unknown')
            key_terms = chunk['metadata'].get('key_terms', [])
            chunk_type = chunk['metadata'].get('chunk_type', 'unknown')
            
            print(f"\n   🔸 Чанк {i} ({chunk_type}, {importance}):")
            print(f"      Ключевые термины: {', '.join(key_terms[:5]) if key_terms else 'нет'}")
            print(f"      Длина: {len(chunk['content'])} символов")
            print(f"      Текст: {chunk['content'][:150]}...")
    
    # Сравнение с простым чанкингом
    print("\n⚖️ Шаг 5: Сравнение с простым чанкингом")
    
    # Создаем простой экстрактор для сравнения
    simple_extractor = AdvancedPDFExtractor(use_smart_chunking=False)
    simple_document = simple_extractor.extract_document(test_pdf)
    simple_chunks = simple_extractor.get_smart_chunks(simple_document)
    
    simple_avg_length = sum(len(c['content']) for c in simple_chunks) / len(simple_chunks) if simple_chunks else 0
    
    print(f"   📊 Сравнение:")
    print(f"      Умный чанкинг:    {len(smart_chunks)} чанков, ср. длина {avg_length:.0f}")
    print(f"      Простой чанкинг:  {len(simple_chunks)} чанков, ср. длина {simple_avg_length:.0f}")
    
    improvement_factor = len(simple_chunks) / len(smart_chunks) if smart_chunks else 1
    print(f"      Сжатие в {improvement_factor:.1f}x раз")
    
    # Проверяем качество извлечения ключевых терминов
    print("\n🔬 Шаг 6: Анализ извлечения ключевых терминов")
    
    all_key_terms = []
    for chunk in smart_chunks:
        terms = chunk['metadata'].get('key_terms', [])
        all_key_terms.extend(terms)
    
    unique_terms = list(set(all_key_terms))
    scientific_terms = [term for term in unique_terms 
                       if any(sci_word in term.lower() 
                             for sci_word in ['lysobacter', 'strain', 'ph', '°c', 'rna', 'catalase'])]
    
    print(f"   🧬 Всего ключевых терминов: {len(all_key_terms)}")
    print(f"   🎯 Уникальных терминов: {len(unique_terms)}")
    print(f"   🔬 Научных терминов: {len(scientific_terms)}")
    
    if scientific_terms:
        print(f"   📝 Примеры научных терминов: {', '.join(scientific_terms[:10])}")
    
    # Финальная оценка
    print(f"\n✅ ИТОГ: Умный чанкинг успешно применён!")
    print(f"   - Создано {len(smart_chunks)} оптимизированных чанков")
    print(f"   - Средний размер: {avg_length:.0f} символов (цель: 350)")
    print(f"   - Извлечено {len(scientific_terms)} научных терминов")
    
    # Оценка качества
    size_score = max(0, 100 - abs(avg_length - 350) / 350 * 100)
    term_score = min(100, len(scientific_terms) * 10)
    overall_score = (size_score + term_score) / 2
    
    print(f"   📊 Оценка качества: {overall_score:.1f}%")
    
    if overall_score >= 80:
        print("   🏆 ОТЛИЧНОЕ качество чанкинга!")
    elif overall_score >= 60:
        print("   ✅ ХОРОШЕЕ качество чанкинга")
    else:
        print("   ⚠️ Требуется улучшение")

if __name__ == "__main__":
    test_smart_chunking() 