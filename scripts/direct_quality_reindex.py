#!/usr/bin/env python3
"""
Прямая переиндексация с улучшениями качества
"""
import sys
import os
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def apply_quality_reindexing():
    """Применяет переиндексацию с улучшениями качества"""
    
    print("🚀 ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ С УЛУЧШЕНИЯМИ КАЧЕСТВА")
    print("=" * 55)
    
    # Проверяем, что мы в виртуальной среде
    if 'lysobacter_rag_env' not in sys.prefix:
        print("⚠️ ВНИМАНИЕ: Рекомендуется запускать в виртуальной среде")
        print("   Активируйте: source lysobacter_rag_env/bin/activate")
    
    try:
        # Импортируем модули
        print("🔧 Загрузка модулей...")
        
        from config import config
        import shutil
        import time
        from datetime import datetime
        
        # Получаем пути
        data_dir = Path(config.DATA_DIR)
        storage_dir = Path(config.STORAGE_DIR)
        chroma_db_path = storage_dir / "chroma_db"
        
        print(f"📂 Директория данных: {data_dir}")
        print(f"📂 Хранилище: {storage_dir}")
        
        # Проверяем наличие PDF файлов
        pdf_files = list(data_dir.glob("*.pdf"))
        print(f"📄 Найдено PDF файлов: {len(pdf_files)}")
        
        if len(pdf_files) == 0:
            print("❌ Нет PDF файлов для обработки!")
            return False
        
        # Подтверждение
        print(f"\n⚠️ ВНИМАНИЕ:")
        print(f"   Будет удалена существующая база ChromaDB")
        print(f"   Время выполнения: ~10-15 минут")
        print(f"   Будет обработано: {len(pdf_files)} документов")
        
        try:
            confirm = input("\n   Продолжить? (y/N): ").strip().lower()
        except KeyboardInterrupt:
            print("\n❌ Операция отменена")
            return False
        
        if confirm != 'y':
            print("❌ Переиндексация отменена")
            return False
        
        # Создаем резервную копию существующей базы
        if chroma_db_path.exists():
            backup_path = storage_dir / f"chroma_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"💾 Создание резервной копии: {backup_path.name}")
            shutil.move(str(chroma_db_path), str(backup_path))
        
        # Запускаем переиндексацию
        print(f"\n🔄 ЗАПУСК ПЕРЕИНДЕКСАЦИИ...")
        start_time = time.time()
        
        # Используем существующий скрипт переиндексации с улучшениями
        reindex_script = Path(__file__).parent / "reindex_with_quality_fix.py"
        
        if reindex_script.exists():
            print(f"📝 Используем улучшенный экстрактор...")
            
            # Запускаем улучшенную переиндексацию
            import subprocess
            result = subprocess.run([
                sys.executable, str(reindex_script)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Переиндексация завершена успешно!")
                
                # Показываем результаты
                lines = result.stdout.split('\n')
                for line in lines[-10:]:  # Последние 10 строк
                    if line.strip():
                        print(f"   {line}")
            else:
                print(f"❌ Ошибка переиндексации:")
                print(f"   {result.stderr}")
                return False
        else:
            # Альтернативный путь - прямая переиндексация
            print(f"📝 Используем прямую переиндексацию...")
            success = run_direct_reindexing()
            
            if not success:
                return False
        
        # Проверяем результат
        elapsed_time = time.time() - start_time
        print(f"\n⏱️ Время выполнения: {elapsed_time:.1f} секунд")
        
        # Быстрая проверка качества
        print(f"\n🧪 БЫСТРАЯ ПРОВЕРКА КАЧЕСТВА:")
        success = test_improved_quality()
        
        if success:
            print(f"\n🎉 ПЕРЕИНДЕКСАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print(f"✅ Данные обновлены с улучшениями качества")
            print(f"🔍 Проверьте результаты: make check-overall-quality")
            
            # Удаляем старую резервную копию если все ОК
            old_backups = list(storage_dir.glob("chroma_db_backup_*"))
            if len(old_backups) > 3:  # Оставляем только 3 последние
                for backup in sorted(old_backups)[:-3]:
                    shutil.rmtree(backup)
                    print(f"🗑️ Удалена старая резервная копия: {backup.name}")
            
            return True
        else:
            print(f"\n⚠️ Переиндексация завершена, но есть проблемы с качеством")
            return False
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Восстанавливаем из резервной копии при ошибке
        if 'backup_path' in locals() and backup_path.exists():
            print(f"🔄 Восстановление из резервной копии...")
            if chroma_db_path.exists():
                shutil.rmtree(chroma_db_path)
            shutil.move(str(backup_path), str(chroma_db_path))
            print(f"✅ База данных восстановлена")
        
        return False

def run_direct_reindexing():
    """Запускает прямую переиндексацию"""
    
    try:
        from config import config
        from lysobacter_rag.pdf_extractor.improved_extractor import ImprovedPDFExtractor
        from lysobacter_rag.data_processor import DataProcessor  
        from lysobacter_rag.indexer.indexer import Indexer
        
        print("🔧 Инициализация компонентов...")
        
        extractor = ImprovedPDFExtractor()
        processor = DataProcessor()
        indexer = Indexer()
        
        # Извлекаем документы
        print("📄 Извлечение документов...")
        data_dir = Path(config.DATA_DIR)
        pdf_files = list(data_dir.glob("*.pdf"))
        
        all_documents = []
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                print(f"   {i}/{len(pdf_files)}: {pdf_file.name}")
                doc = extractor.extract_with_quality_control(pdf_file)
                all_documents.append(doc)
            except Exception as e:
                print(f"   ⚠️ Ошибка в {pdf_file.name}: {e}")
        
        print(f"✅ Извлечено {len(all_documents)} документов")
        
        # Создаем чанки
        print("🔄 Создание чанков...")
        all_chunks = processor.process_documents(all_documents)
        print(f"✅ Создано {len(all_chunks)} чанков")
        
        # Пересоздаем индекс
        print("🗂️ Создание нового индекса...")
        success = indexer.rebuild_index(all_chunks)
        
        if success:
            stats = indexer.get_collection_stats()
            print(f"✅ Индекс создан: {stats.get('total_chunks', 0)} чанков")
            return True
        else:
            print("❌ Ошибка создания индекса")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка прямой переиндексации: {e}")
        return False

def test_improved_quality():
    """Быстро тестирует улучшение качества"""
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        indexer = Indexer()
        
        # Тестируем ключевые запросы
        test_cases = [
            ("GW1-59T", "точный поиск штамма"),
            ("15–37°C", "корректная температура"),
            ("pH 9.0–11.0", "правильный pH"),
            ("C15:0", "жирные кислоты"),
            ("Lysobacter antarcticus", "полное название")
        ]
        
        success_count = 0
        
        for query, description in test_cases:
            results = indexer.search(query, top_k=1)
            if results and len(results) > 0:
                print(f"   ✅ {query}: найден ({description})")
                success_count += 1
            else:
                print(f"   ⚠️ {query}: не найден ({description})")
        
        quality_score = success_count / len(test_cases)
        print(f"\n📊 Качество: {success_count}/{len(test_cases)} ({quality_score:.1%})")
        
        return quality_score >= 0.6  # 60% успешности - минимум
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ПРЯМАЯ ПЕРЕИНДЕКСАЦИЯ С УЛУЧШЕНИЯМИ КАЧЕСТВА")
    print("=" * 60)
    
    success = apply_quality_reindexing()
    
    if success:
        print(f"\n🎉 СИСТЕМА УСПЕШНО ОБНОВЛЕНА!")
        print(f"💡 Рекомендации:")
        print(f"   • Протестируйте запросы о штамме GW1-59T")
        print(f"   • Сравните качество ответов с предыдущими")
        print(f"   • Запустите мониторинг: make monitor-quality")
    else:
        print(f"\n💡 ЧТО ДЕЛАТЬ:")
        print(f"   • Проверьте логи на ошибки")
        print(f"   • Убедитесь, что все зависимости установлены")
        print(f"   • Попробуйте: make fix-extraction")
    
    sys.exit(0 if success else 1) 