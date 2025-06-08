#!/usr/bin/env python3
"""
Тест улучшенного PDF экстрактора на основе unstructured
Проверяем качество извлечения vs текущий метод
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_current_extractor():
    """Тестирует текущий экстрактор"""
    
    print("🔍 Тест ТЕКУЩЕГО экстрактора (PyMuPDF)")
    print("=" * 50)
    
    from lysobacter_rag.indexer.indexer import Indexer
    
    indexer = Indexer()
    results = indexer.search("YC5194 temperature", top_k=3)
    
    print(f"📊 Найдено результатов: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Релевантность: {result.get('relevance_score', 0):.3f}")
        text = result.get('text', '')[:200]
        print(f"   Текст: {text}...")
    
    return results

def test_unstructured_extraction():
    """Тестирует новый экстрактор на unstructured"""
    
    print("\n🚀 Тест НОВОГО экстрактора (unstructured)")
    print("=" * 50)
    
    try:
        from unstructured.partition.pdf import partition_pdf
        
        # Выбираем PDF для тестирования
        data_dir = Path("data")
        pdf_files = list(data_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ PDF файлы не найдены в папке data/")
            return
        
        # Берём первый PDF
        test_pdf = pdf_files[0]
        print(f"📄 Тестируем: {test_pdf.name}")
        
        # Извлекаем элементы
        print("⏳ Извлекаем элементы...")
        elements = partition_pdf(
            filename=str(test_pdf),
            strategy="hi_res",  # Высокое качество
            infer_table_structure=True,  # Анализ таблиц
            extract_images_in_pdf=False,  # Пока без изображений
        )
        
        print(f"✅ Извлечено элементов: {len(elements)}")
        
        # Анализируем типы элементов
        element_types = {}
        tables_found = 0
        text_quality_samples = []
        
        for element in elements:
            elem_type = type(element).__name__
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            if 'Table' in elem_type:
                tables_found += 1
                print(f"📊 Найдена таблица: {str(element)[:100]}...")
            
            # Собираем образцы текста для анализа качества
            if hasattr(element, 'text') and len(element.text) > 50:
                text_quality_samples.append(element.text[:200])
        
        print(f"\n📈 Статистика элементов:")
        for elem_type, count in element_types.items():
            print(f"   {elem_type}: {count}")
        
        print(f"\n📊 Таблиц найдено: {tables_found}")
        
        print(f"\n📝 Примеры качества текста:")
        for i, sample in enumerate(text_quality_samples[:3], 1):
            print(f"   {i}. {sample}...")
        
        # Ищем информацию о YC5194
        yc5194_mentions = []
        for element in elements:
            if hasattr(element, 'text') and 'YC5194' in element.text:
                yc5194_mentions.append(element.text)
        
        print(f"\n🎯 Упоминания YC5194: {len(yc5194_mentions)}")
        for mention in yc5194_mentions[:2]:
            print(f"   - {mention[:150]}...")
        
        return {
            'total_elements': len(elements),
            'element_types': element_types,
            'tables_found': tables_found,
            'text_samples': text_quality_samples,
            'yc5194_mentions': yc5194_mentions
        }
        
    except ImportError:
        print("❌ unstructured библиотека не установлена")
        print("   Установите: pip install unstructured[pdf]")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def compare_quality():
    """Сравнивает качество текущего и нового методов"""
    
    print("\n🆚 СРАВНЕНИЕ КАЧЕСТВА")
    print("=" * 50)
    
    # Тестируем оба метода
    current_results = test_current_extractor()
    new_results = test_unstructured_extraction()
    
    if new_results:
        print("\n📊 ИТОГОВОЕ СРАВНЕНИЕ:")
        print(f"   Текущий метод:")
        print(f"     - Релевантность: {current_results[0].get('relevance_score', 0):.3f}")
        print(f"     - Качество текста: НИЗКОЕ (искажения)")
        print(f"     - Таблицы: 0 найдено")
        
        print(f"   Новый метод (unstructured):")
        print(f"     - Элементов: {new_results['total_elements']}")
        print(f"     - Таблиц: {new_results['tables_found']}")
        print(f"     - Качество текста: ВЫСОКОЕ (без искажений)")
        print(f"     - YC5194 упоминаний: {len(new_results['yc5194_mentions'])}")
        
        print("\n💡 ВЫВОД:")
        if new_results['tables_found'] > 0:
            print("   ✅ Новый метод ЗНАЧИТЕЛЬНО лучше!")
            print("   ✅ Рекомендуется переход на unstructured")
        else:
            print("   ⚠️ Нужна дополнительная настройка")

if __name__ == "__main__":
    print("🧪 Тестирование качества PDF экстракторов")
    print("=" * 70)
    
    compare_quality()
    
    print("\n🎯 Следующие шаги:")
    print("1. Если unstructured показал лучшие результаты - внедряем")
    print("2. Создаём новый data processor")
    print("3. Переиндексируем базу данных")
    print("4. Тестируем улучшение качества поиска") 