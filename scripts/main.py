#!/usr/bin/env python3
"""
Главный файл для запуска RAG-системы обработки PDF лизобактов
"""

import os
import sys
from pathlib import Path
from loguru import logger

# Добавляем src в путь для импортов
sys.path.append(str(Path(__file__).parent / "src"))

from config import config
from src.lysobacter_rag.pdf_extractor import PDFExtractor
from src.lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
from src.lysobacter_rag.data_processor import DataProcessor  
from src.lysobacter_rag.indexer import Indexer


def setup_logging():
    """Настройка логирования"""
    logger.remove()  # Удаляем стандартный обработчик
    logger.add(
        config.LOG_FILE,
        rotation="10 MB",
        retention="1 week",
        level=config.LOG_LEVEL
    )
    logger.add(
        sys.stdout,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )


def extract_and_process_data():
    """Извлекает и обрабатывает данные из PDF файлов"""
    logger.info("🔄 Начинаю извлечение данных из PDF файлов...")
    
    # Выбираем экстрактор в зависимости от конфигурации
    if config.USE_ENHANCED_EXTRACTOR:
        logger.info("🚀 Используем продвинутый PDF экстрактор (pymupdf4llm + pdfplumber + tabula)")
        extractor = AdvancedPDFExtractor()
        
        # Обрабатываем PDF файлы с продвинутым экстрактором
        pdf_files = list(config.DATA_DIR.glob("*.pdf"))
        docs = []
        
        for pdf_file in pdf_files:
            try:
                document = extractor.extract_document(pdf_file)
                docs.append(document)
                logger.info(f"✅ Обработан {pdf_file.name}: {len(document.elements)} элементов")
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке {pdf_file.name}: {e}")
                continue
        
        logger.info(f"✅ Продвинутый экстрактор обработал {len(docs)} документов")
        
    else:
        logger.info("📄 Используем базовый PDF экстрактор")
        extractor = PDFExtractor()
        docs = extractor.extract_all_pdfs(str(config.DATA_DIR))
    
    if not docs:
        logger.error("❌ Не удалось извлечь данные из PDF файлов")
        return None
    
    logger.info(f"✅ Извлечено {len(docs)} документов")
    
    # Шаг 2: Обработка и чанкинг
    logger.info("🔄 Обрабатываю и разбиваю данные на чанки...")
    processor = DataProcessor()
    
    if config.USE_ENHANCED_EXTRACTOR:
        # Конвертируем продвинутые документы в чанки
        chunks = convert_advanced_documents_to_chunks(docs)
    else:
        chunks = processor.process_documents(docs)
    
    if not chunks:
        logger.error("❌ Не удалось обработать документы")
        return None
    
    # Показываем статистику
    if hasattr(processor, 'get_statistics'):
        stats = processor.get_statistics(chunks)
        logger.info("📊 Статистика обработки:")
        for key, value in stats.items():
            if key != 'sources':  # Не показываем длинный список источников
                logger.info(f"   {key}: {value}")
    else:
        # Простая статистика для продвинутого экстрактора
        text_chunks = [c for c in chunks if c.chunk_type == 'text']
        table_chunks = [c for c in chunks if c.chunk_type == 'table']
        logger.info("📊 Статистика обработки:")
        logger.info(f"   Всего чанков: {len(chunks)}")
        logger.info(f"   Текстовых: {len(text_chunks)}")
        logger.info(f"   Табличных: {len(table_chunks)}")
    
    return chunks


def convert_advanced_documents_to_chunks(advanced_docs):
    """Конвертирует продвинутые документы в чанки для индексации"""
    from src.lysobacter_rag.data_processor import DocumentChunk
    
    chunks = []
    chunk_id = 0
    
    for doc in advanced_docs:
        for element in doc.elements:
            chunk = DocumentChunk(
                chunk_id=f"{Path(doc.file_path).stem}_{element.element_type}_{chunk_id}",
                text=element.content,
                chunk_type=element.element_type,
                metadata={
                    'source_pdf': Path(doc.file_path).name,
                    'page_number': element.page_number,
                    'confidence': element.confidence,
                    'extraction_method': element.metadata.get('extraction_method', 'advanced'),
                    'table_shape': element.metadata.get('table_shape', ''),
                    'relevance_score': element.confidence,
                    'advanced_extractor': True
                }
            )
            chunks.append(chunk)
            chunk_id += 1
    
    return chunks


def index_data(chunks):
    """Индексирует чанки в векторную базу данных"""
    logger.info("🔄 Индексирую данные в векторную базу...")
    
    indexer = Indexer()
    success = indexer.index_chunks(chunks)
    
    if success:
        stats = indexer.get_collection_stats()
        logger.info("✅ Индексация завершена успешно")
        logger.info("📊 Статистика индексации:")
        for key, value in stats.items():
            if key != 'sources':
                logger.info(f"   {key}: {value}")
        return indexer
    else:
        logger.error("❌ Ошибка при индексации")
        return None


def console_interface(indexer):
    """Простой консольный интерфейс для вопросов"""
    print("\n" + "="*80)
    print("🤖 RAG-система для работы с базой знаний о лизобактериях")
    print("💡 Задавайте вопросы на русском языке")
    print("🛑 Для выхода введите 'exit' или 'quit'")
    print("="*80 + "\n")
    
    # Поскольку у нас нет полного RAG-пайплайна, сделаем простой поиск
    while True:
        try:
            query = input("❓ Ваш вопрос: ").strip()
            
            if query.lower() in ['exit', 'quit', 'выход']:
                print("👋 До свидания!")
                break
            
            if not query:
                continue
            
            # Простой поиск
            results = indexer.search(query, top_k=3)
            
            if not results:
                print("😔 Не найдено релевантной информации для вашего вопроса.\n")
                continue
            
            print(f"\n💬 Найдено {len(results)} релевантных результатов:\n")
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                text = result['text']
                score = result['relevance_score']
                
                print(f"📄 Результат {i} (релевантность: {score:.3f})")
                print(f"📋 Источник: {metadata.get('source_pdf', 'Неизвестен')}")
                print(f"📖 Страница: {metadata.get('page_number', 'Неизвестна')}")
                print(f"📝 Тип: {metadata.get('chunk_type', 'text')}")
                
                if metadata.get('chunk_type') == 'table' and metadata.get('original_table_title'):
                    print(f"🗂️  Таблица: {metadata['original_table_title']}")
                
                # Показываем первые 300 символов текста
                preview = text[:300] + "..." if len(text) > 300 else text
                print(f"📃 Содержание: {preview}")
                print("-" * 60)
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            logger.error(f"Ошибка в интерфейсе: {e}")
            print(f"❌ Произошла ошибка: {e}\n")


def main():
    """Главная функция"""
    setup_logging()
    
    logger.info("🚀 Запускаю RAG-систему обработки PDF лизобактов")
    
    # Проверяем наличие директории с данными
    if not config.DATA_DIR.exists():
        logger.error(f"❌ Директория с данными не найдена: {config.DATA_DIR}")
        return
    
    pdf_files = list(config.DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"❌ PDF файлы не найдены в {config.DATA_DIR}")
        return
    
    logger.info(f"📚 Найдено {len(pdf_files)} PDF файлов для обработки")
    
    try:
        # Проверяем, есть ли уже индексированные данные
        indexer = Indexer()
        stats = indexer.get_collection_stats()
        
        if stats.get('total_chunks', 0) > 0:
            logger.info(f"✅ Найдена существующая база данных с {stats['total_chunks']} чанками")
            user_input = input("🤔 Использовать существующие данные? (y/n): ").strip().lower()
            
            if user_input in ['n', 'no', 'нет']:
                logger.info("🔄 Пересоздаю базу данных...")
                chunks = extract_and_process_data()
                if chunks:
                    indexer = index_data(chunks)
                else:
                    return
            # Иначе используем существующий индексер
        else:
            # Нет данных, создаем с нуля
            chunks = extract_and_process_data()
            if not chunks:
                return
            
            indexer = index_data(chunks)
            if not indexer:
                return
        
        # Запускаем консольный интерфейс
        console_interface(indexer)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Работа прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    main() 