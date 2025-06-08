#!/usr/bin/env python3
"""
Полная переиндексация всех PDF файлов с продвинутым экстрактором
"""

import sys
from pathlib import Path
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

def reindex_all_pdfs_with_advanced_extractor():
    """Переиндексирует все PDF файлы с продвинутым экстрактором"""
    
    print("🔄 ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ ВСЕХ PDF С ПРОДВИНУТЫМ ЭКСТРАКТОРОМ")
    print("=" * 70)
    print("🎯 Цель: Создать полную базу со всеми штаммами (включая YC5194)")
    print("🚀 Метод: Продвинутый экстрактор (pymupdf4llm + pdfplumber + tabula)")
    print()
    
    try:
        from config import config
        from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
        from lysobacter_rag.indexer.indexer import Indexer
        from lysobacter_rag.data_processor import DocumentChunk
        from tqdm import tqdm
        
        # Инициализируем компоненты
        extractor = AdvancedPDFExtractor()
        indexer = Indexer()
        
        # Получаем все PDF файлы
        data_dir = Path(config.DATA_DIR)
        pdf_files = list(data_dir.glob("*.pdf"))
        
        print(f"📁 Найдено PDF файлов: {len(pdf_files)}")
        
        if len(pdf_files) == 0:
            print("❌ PDF файлы не найдены!")
            return False
        
        # Очищаем существующую коллекцию
        print("🗑️ Очищаю существующую базу данных...")
        try:
            # Получаем все ID и удаляем их
            all_data = indexer.collection.get()
            if all_data['ids']:
                indexer.collection.delete(ids=all_data['ids'])
                print(f"   ✅ Удалено {len(all_data['ids'])} записей")
            else:
                print("   ✅ База уже пуста")
        except Exception as e:
            print(f"   ⚠️ Ошибка очистки: {e}")
            print("   📝 Создаю новую коллекцию...")
            # Если не удалось очистить, создаём новую коллекцию
            try:
                indexer.chroma_client.delete_collection(config.CHROMA_COLLECTION_NAME)
            except:
                pass
            indexer = Indexer()  # Пересоздаём индексер
        
        # Переиндексируем все файлы
        all_chunks = []
        processed_files = 0
        failed_files = 0
        
        print(f"\n🔄 Обрабатываю {len(pdf_files)} PDF файлов...")
        
        for pdf_file in tqdm(pdf_files, desc="Извлечение PDF"):
            try:
                # Извлекаем документ
                document = extractor.extract_document(pdf_file)
                
                # Конвертируем в чанки
                file_chunks = []
                chunk_id = 0
                
                for element in document.elements:
                    chunk = DocumentChunk(
                        chunk_id=f"{pdf_file.stem}_{element.element_type}_{chunk_id}",
                        text=element.content,
                        chunk_type=element.element_type,
                        metadata={
                            'source_pdf': pdf_file.name,
                            'page_number': element.page_number,
                            'confidence': element.confidence,
                            'extraction_method': element.metadata.get('extraction_method', 'advanced'),
                            'table_shape': element.metadata.get('table_shape', ''),
                            'relevance_score': element.confidence,
                            'advanced_extractor': True
                        }
                    )
                    file_chunks.append(chunk)
                    chunk_id += 1
                
                all_chunks.extend(file_chunks)
                processed_files += 1
                
                print(f"✅ {pdf_file.name}: {len(file_chunks)} элементов")
                
            except Exception as e:
                print(f"❌ Ошибка при обработке {pdf_file.name}: {e}")
                failed_files += 1
                continue
        
        print(f"\n📊 СТАТИСТИКА ИЗВЛЕЧЕНИЯ:")
        print(f"   ✅ Обработано файлов: {processed_files}")
        print(f"   ❌ Ошибок: {failed_files}")
        print(f"   📋 Всего чанков: {len(all_chunks)}")
        
        # Анализируем типы чанков
        text_chunks = [c for c in all_chunks if c.chunk_type == 'text']
        table_chunks = [c for c in all_chunks if c.chunk_type == 'table']
        
        print(f"   📝 Текстовых чанков: {len(text_chunks)}")
        print(f"   📊 Табличных чанков: {len(table_chunks)}")
        
        if len(all_chunks) == 0:
            print("❌ Не удалось извлечь чанки!")
            return False
        
        # Индексируем чанки
        print(f"\n🔄 Индексирую {len(all_chunks)} чанков...")
        success = indexer.index_chunks(all_chunks)
        
        if success:
            print("✅ Индексация завершена успешно!")
            
            # Проверяем статистику новой базы
            stats = indexer.get_collection_stats()
            print(f"\n📊 СТАТИСТИКА НОВОЙ БАЗЫ:")
            for key, value in stats.items():
                if key != 'sources':
                    print(f"   {key}: {value}")
            
            # Проверяем наличие YC5194
            print(f"\n🔍 ПРОВЕРКА YC5194:")
            yc5194_results = indexer.search("YC5194", top_k=3)
            if yc5194_results:
                print(f"✅ YC5194 найден! Релевантность: {yc5194_results[0].get('relevance_score', 0):.3f}")
                
                # Показываем детали
                for i, result in enumerate(yc5194_results[:2], 1):
                    metadata = result['metadata']
                    print(f"   {i}. Источник: {metadata.get('source_pdf', 'N/A')}")
                    print(f"      Тип: {metadata.get('chunk_type', 'N/A')}")
                    print(f"      Релевантность: {result.get('relevance_score', 0):.3f}")
            else:
                print("❌ YC5194 всё ещё не найден")
            
            return True
        else:
            print("❌ Ошибка при индексации!")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_yc5194_after_reindex():
    """Тестирует поиск YC5194 после переиндексации"""
    
    print(f"\n🧪 ТЕСТ YC5194 ПОСЛЕ ПЕРЕИНДЕКСАЦИИ")
    print("=" * 40)
    
    try:
        from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
        
        rag = RAGPipeline()
        
        # Тестируем точный запрос
        query = "Какие характеристики штамма Lysobacter capsici YC5194?"
        print(f"📝 Запрос: {query}")
        
        response = rag.ask_question(query)
        
        print(f"\n💬 Ответ:")
        print(f"{response['answer'][:500]}...")
        print(f"\n📊 Метрики:")
        print(f"   Источников: {response['num_sources_used']}")
        print(f"   Уверенность: {response['confidence']:.3f}")
        
        # Проверяем, содержит ли ответ YC5194
        if 'YC5194' in response['answer']:
            print("✅ YC5194 найден в ответе!")
            return True
        else:
            print("⚠️ YC5194 всё ещё не в ответе")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

if __name__ == "__main__":
    print("🚀 НАЧИНАЮ ПОЛНУЮ ПЕРЕИНДЕКСАЦИЮ")
    
    # Переиндексируем все файлы
    success = reindex_all_pdfs_with_advanced_extractor()
    
    if success:
        print("\n" + "="*50)
        # Тестируем YC5194
        test_success = test_yc5194_after_reindex()
        
        if test_success:
            print("\n🎉 УСПЕХ! YC5194 теперь доступен в системе!")
        else:
            print("\n⚠️ YC5194 всё ещё недоступен. Возможно, его нет в PDF файлах.")
    else:
        print("\n❌ Переиндексация не удалась") 