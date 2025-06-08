#!/usr/bin/env python3
"""
Быстрый тест RAG-системы для поиска информации о штамме GW1-59T
"""

import os
from pathlib import Path
from config import config
from src.lysobacter_rag.pdf_extractor import PDFExtractor
from src.lysobacter_rag.data_processor import DataProcessor
from src.lysobacter_rag.indexer import Indexer
from src.lysobacter_rag.rag_pipeline import RAGPipeline

def quick_test_strain_gw1_59t():
    """Быстрый тест поиска информации о штамме GW1-59T"""
    
    print("🔬 БЫСТРЫЙ ТЕСТ RAG-СИСТЕМЫ")
    print("🎯 Поиск информации о штамме GW1-59T")
    print("=" * 60)
    
    # Проверяем наличие PDF файлов
    data_dir = Path(config.DATA_DIR)
    pdf_files = list(data_dir.glob("*.pdf"))
    print(f"📁 Найдено PDF файлов: {len(pdf_files)}")
    
    if len(pdf_files) == 0:
        print("❌ PDF файлы не найдены!")
        return False
    
    # Берем только первые 5 файлов для быстрого теста
    test_files = pdf_files[:5]
    print(f"🧪 Тестируем на {len(test_files)} файлах:")
    for pdf in test_files:
        print(f"   • {pdf.name}")
    
    try:
        # Шаг 1: Извлечение текста
        print(f"\n📤 Шаг 1: Извлечение текста из PDF...")
        extractor = PDFExtractor()
        
        all_docs = []
        for pdf_file in test_files:
            print(f"   Обрабатываю {pdf_file.name}...")
            docs = extractor.extract_from_pdf(str(pdf_file))
            if docs:
                all_docs.extend(docs)
                print(f"   ✅ Извлечено {len(docs)} элементов")
            else:
                print(f"   ⚠️ Ничего не извлечено")
        
        print(f"📊 Всего извлечено документов: {len(all_docs)}")
        
        if len(all_docs) == 0:
            print("❌ Не удалось извлечь данные из PDF")
            return False
        
        # Проверяем, есть ли упоминания штамма GW1-59T
        mentions = []
        for doc in all_docs:
            text = doc.get('text', '').lower()
            if 'gw1-59t' in text or 'gw1-59' in text or 'gw159' in text:
                mentions.append(doc)
        
        print(f"🔍 Найдено упоминаний штамма GW1-59T: {len(mentions)}")
        
        # Шаг 2: Обработка данных
        print(f"\n📤 Шаг 2: Обработка данных...")
        processor = DataProcessor()
        chunks = processor.process_documents(all_docs)
        print(f"📊 Создано чанков: {len(chunks)}")
        
        # Шаг 3: Создание индекса (только если есть чанки)
        if len(chunks) > 0:
            print(f"\n📤 Шаг 3: Создание векторного индекса...")
            indexer = Indexer()
            
            # Удаляем старую коллекцию если есть
            try:
                indexer.delete_collection()
            except:
                pass
            
            indexer.index_chunks(chunks)
            print(f"✅ Индекс создан")
            
            # Шаг 4: Тест поиска
            print(f"\n📤 Шаг 4: Тестовый поиск...")
            
            test_queries = [
                "GW1-59T",
                "штамм GW1-59T", 
                "штамм GW1-59",
                "strain GW1-59T",
                "GW1 59 strain"
            ]
            
            for query in test_queries:
                print(f"🔍 Поиск: '{query}'")
                results = indexer.search(query, top_k=3)
                print(f"   Найдено результатов: {len(results)}")
                
                for i, result in enumerate(results, 1):
                    relevance = result.get('relevance_score', 0)
                    source = result.get('metadata', {}).get('source_pdf', 'Unknown')
                    text_preview = result.get('text', '')[:100] + '...'
                    print(f"   {i}. Релевантность: {relevance:.3f}")
                    print(f"      Источник: {source}")
                    print(f"      Текст: {text_preview}")
                print()
            
            # Шаг 5: Тест RAG-пайплайна
            print(f"\n📤 Шаг 5: Тест RAG-пайплайна...")
            
            try:
                rag = RAGPipeline()
                
                question = "Расскажи о штамме GW1-59T"
                print(f"❓ Вопрос: {question}")
                
                response = rag.ask_question(question)
                
                print(f"💬 Ответ:")
                print(f"   {response['answer']}")
                print(f"📊 Источников использовано: {response['num_sources_used']}")
                print(f"⭐ Уверенность: {response['confidence']:.2f}")
                
                if response['sources']:
                    print(f"📚 Источники:")
                    for source in response['sources']:
                        print(f"   • {source}")
                
                return True
                
            except Exception as e:
                print(f"❌ Ошибка RAG-пайплайна: {e}")
                return False
        
        else:
            print("❌ Нет данных для индексации")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в процессе: {e}")
        return False

if __name__ == "__main__":
    success = quick_test_strain_gw1_59t()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ТЕСТ ПРОЙДЕН! RAG-система работает!")
        print("💡 Теперь можно задавать вопросы о штамме GW1-59T")
    else:
        print("❌ Тест не пройден. Требуется диагностика проблем.")
        
    print("\n🚀 Для полного запуска используйте:")
    print("   python main.py")
    print("   streamlit run streamlit_app.py") 