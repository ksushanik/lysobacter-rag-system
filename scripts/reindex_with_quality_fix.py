#!/usr/bin/env python3
"""
Переиндексация базы данных с улучшенным экстрактором качества
"""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def reindex_with_quality_fixes():
    """Переиндексирует базу с исправлениями качества"""
    
    print("🔧 ПЕРЕИНДЕКСАЦИЯ С УЛУЧШЕННЫМ КАЧЕСТВОМ")
    print("=" * 50)
    
    try:
        from config import config
        from lysobacter_rag.pdf_extractor.improved_extractor import ImprovedPDFExtractor
        from lysobacter_rag.data_processor import DataProcessor
        from lysobacter_rag.indexer.indexer import Indexer
        
        # Инициализируем компоненты
        print("📚 Инициализация компонентов...")
        extractor = ImprovedPDFExtractor()
        processor = DataProcessor()
        indexer = Indexer()
        
        # Получаем статистику старой базы
        old_stats = indexer.get_collection_stats()
        print(f"📊 Старая база: {old_stats.get('total_chunks', 0)} чанков")
        
        # Извлекаем данные с улучшенным качеством
        print("📄 Извлечение PDF с исправлениями качества...")
        data_dir = Path(config.DATA_DIR)
        pdf_files = list(data_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ PDF файлы не найдены в {data_dir}")
            return False
        
        print(f"   Найдено {len(pdf_files)} PDF файлов")
        
        # Сначала тестируем на файле с GW1-59T
        antarcticus_file = None
        for pdf_file in pdf_files:
            if 'antarcticus' in pdf_file.name.lower():
                antarcticus_file = pdf_file
                break
        
        if antarcticus_file:
            print(f"\n🔍 ТЕСТИРОВАНИЕ на файле: {antarcticus_file.name}")
            test_doc = extractor.extract_with_quality_control(antarcticus_file)
            
            # Проверяем качество исправлений
            quality_metrics = test_doc.metadata.get('quality_metrics', {})
            print(f"   ✅ Исправлено проблем: {quality_metrics.get('fixed_issues', 0)}")
            print(f"   📄 Извлечено страниц: {quality_metrics.get('pages_extracted', 0)}")
            print(f"   📊 Найдено таблиц: {quality_metrics.get('tables_found', 0)}")
            
            # Проверяем наличие ключевых данных
            content = test_doc.content
            key_checks = {
                'GW1-59T найден': 'GW1-59T' in content,
                'Температура 15-37°C': '15–37°C' in content,
                'pH 9.0-11.0': 'pH 9.0–11.0' in content or 'pH 9–11' in content,
                'NaCl 0-4%': '0–4%' in content and 'NaCl' in content,
                'Размер генома 2.8 Mb': '2.8 Mb' in content or '2.8Mb' in content
            }
            
            print(f"\n🔍 ПРОВЕРКА КЛЮЧЕВЫХ ДАННЫХ:")
            for check, found in key_checks.items():
                status = "✅" if found else "❌"
                print(f"   {status} {check}")
            
            found_count = sum(key_checks.values())
            total_count = len(key_checks)
            quality_percent = (found_count / total_count) * 100
            
            print(f"\n📊 КАЧЕСТВО ДАННЫХ: {found_count}/{total_count} ({quality_percent:.0f}%)")
            
            if quality_percent < 80:
                print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Качество данных все еще низкое")
                print("   Рекомендуется дополнительная настройка экстрактора")
            else:
                print("✅ КАЧЕСТВО ПРИЕМЛЕМОЕ: Можно продолжать полную переиндексацию")
        
        # Спрашиваем подтверждение на полную переиндексацию
        print(f"\n❓ ПОДТВЕРЖДЕНИЕ:")
        print(f"   Это удалит существующую базу ({old_stats.get('total_chunks', 0)} чанков)")
        print(f"   И создаст новую с улучшенным качеством")
        
        response = input("   Продолжить? (y/N): ").strip().lower()
        
        if response != 'y':
            print("❌ Переиндексация отменена пользователем")
            return False
        
        # Полная переиндексация
        print(f"\n🚀 НАЧИНАЮ ПОЛНУЮ ПЕРЕИНДЕКСАЦИЮ...")
        
        # Извлекаем все документы
        all_documents = []
        for pdf_file in pdf_files:
            try:
                print(f"   📄 Обрабатываю: {pdf_file.name}")
                doc = extractor.extract_with_quality_control(pdf_file)
                all_documents.append(doc)
            except Exception as e:
                print(f"   ⚠️ Ошибка в {pdf_file.name}: {e}")
        
        print(f"✅ Извлечено {len(all_documents)} документов")
        
        # Обрабатываем в чанки
        print(f"🔄 Обработка в чанки...")
        all_chunks = processor.process_documents(all_documents)
        print(f"✅ Создано {len(all_chunks)} чанков")
        
        # Пересоздаем индекс
        print(f"🗂️ Пересоздание индекса...")
        success = indexer.rebuild_index(all_chunks)
        
        if success:
            # Получаем новую статистику
            new_stats = indexer.get_collection_stats()
            print(f"\n🎉 ПЕРЕИНДЕКСАЦИЯ ЗАВЕРШЕНА!")
            print(f"   📊 Новая база: {new_stats.get('total_chunks', 0)} чанков")
            print(f"   📈 Изменение: {new_stats.get('total_chunks', 0) - old_stats.get('total_chunks', 0)}")
            
            # Тестируем поиск по GW1-59T
            print(f"\n🔍 ТЕСТ ПОИСКА ПО GW1-59T:")
            results = indexer.search("GW1-59T Lysobacter antarcticus", top_k=5)
            
            if results:
                print(f"   ✅ Найдено {len(results)} результатов")
                
                # Проверяем качество первого результата
                first_result = results[0]
                text = first_result['text']
                
                quality_indicators = {
                    'Штамм правильный': 'GW1-59T' in text and 'GW1-5 9T' not in text,
                    'Данные о температуре': any(x in text for x in ['15–37°C', '30°C', 'temperature']),
                    'Данные о pH': any(x in text for x in ['pH 9', 'pH 11', '9.0–11.0']),
                    'Без разорванных формул': not any(x in text for x in ['C 15', ': 0 16']),
                    'Релевантность': first_result.get('relevance_score', 0) > 0.7
                }
                
                for indicator, status in quality_indicators.items():
                    symbol = "✅" if status else "❌"
                    print(f"      {symbol} {indicator}")
                
                quality_score = sum(quality_indicators.values()) / len(quality_indicators) * 100
                print(f"   📊 Общее качество: {quality_score:.0f}%")
                
                if quality_score >= 80:
                    print("   🎉 ОТЛИЧНОЕ КАЧЕСТВО! Переиндексация успешна!")
                    return True
                else:
                    print("   ⚠️ Качество можно улучшить")
                    return True
            else:
                print(f"   ❌ Данные о GW1-59T не найдены после переиндексации!")
                return False
        else:
            print(f"❌ Ошибка при переиндексации")
            return False
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = reindex_with_quality_fixes()
    
    if success:
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print(f"1. Протестируйте RAG-систему с вопросом о GW1-59T")
        print(f"2. Сравните качество ответов с предыдущей версией")  
        print(f"3. При необходимости доработайте регулярные выражения")
    else:
        print(f"\n💡 СЛЕДУЮЩИЕ ШАГИ:")
        print(f"1. Проверьте логи на предмет ошибок")
        print(f"2. Убедитесь в доступности PDF файлов")
        print(f"3. При необходимости доработайте экстрактор")
    
    sys.exit(0 if success else 1) 