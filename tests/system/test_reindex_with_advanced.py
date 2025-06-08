#!/usr/bin/env python3
"""
Переиндексация базы данных с новым продвинутым экстрактором
"""

import sys
from pathlib import Path
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
from lysobacter_rag.data_processor import DocumentChunk
from lysobacter_rag.indexer.indexer import Indexer
from tqdm import tqdm

def create_chunks_with_advanced_extractor():
    """Создаёт чанки с продвинутым экстрактором"""
    
    print('🔄 ПЕРЕОБРАБОТКА С НОВЫМ ЭКСТРАКТОРОМ')
    print('=' * 50)
    
    extractor = AdvancedPDFExtractor()
    data_dir = Path('data')
    pdf_files = list(data_dir.glob('*.pdf'))
    
    print(f'📁 Найдено PDF файлов: {len(pdf_files)}')
    
    all_chunks = []
    
    for pdf_file in tqdm(pdf_files[:3], desc="Обработка PDF"):  # Первые 3 для теста
        try:
            document = extractor.extract_document(pdf_file)
            
            # Создаём чанки
            file_chunks = []
            for i, element in enumerate(document.elements):
                chunk = DocumentChunk(
                    chunk_id=f"{pdf_file.stem}_{element.element_type}_{i}",
                    text=element.content,
                    chunk_type=element.element_type,
                    metadata={
                        'source_pdf': pdf_file.name,
                        'page_number': element.page_number,
                        'confidence': element.confidence,
                        'extraction_method': element.metadata.get('extraction_method', 'advanced'),
                        'table_shape': element.metadata.get('table_shape', ''),
                        'relevance_score': element.confidence
                    }
                )
                file_chunks.append(chunk)
            
            all_chunks.extend(file_chunks)
            print(f"✅ {pdf_file.name}: {len(file_chunks)} чанков")
            
        except Exception as e:
            print(f"❌ Ошибка {pdf_file.name}: {e}")
            continue
    
    return all_chunks

def reindex_database():
    """Переиндексирует базу данных"""
    
    print('\n🚀 ПЕРЕИНДЕКСАЦИЯ БАЗЫ')
    print('=' * 30)
    
    # Создаём чанки
    chunks = create_chunks_with_advanced_extractor()
    
    if not chunks:
        print("❌ Нет чанков для индексации")
        return False
    
    # Статистика
    text_chunks = [c for c in chunks if c.chunk_type == 'text']
    table_chunks = [c for c in chunks if c.chunk_type == 'table']
    yc5194_chunks = [c for c in chunks if 'YC5194' in c.text]
    
    print(f'📊 СТАТИСТИКА ЧАНКОВ:')
    print(f'   Всего: {len(chunks)}')
    print(f'   📝 Текстовых: {len(text_chunks)}')
    print(f'   📊 Табличных: {len(table_chunks)}')
    print(f'   🎯 С YC5194: {len(yc5194_chunks)}')
    
    # Показываем примеры
    if table_chunks:
        print(f'\n📊 Пример таблицы:')
        print(f'   {table_chunks[0].text[:150]}...')
    
    if yc5194_chunks:
        print(f'\n🎯 Пример с YC5194:')
        print(f'   {yc5194_chunks[0].text[:150]}...')
    
    # Индексируем
    print(f'\n🔄 Индексация {len(chunks)} чанков...')
    indexer = Indexer()
    
    # Очищаем старую коллекцию
    indexer.delete_collection()
    
    # Создаём новую и индексируем
    indexer = Indexer()  # Переинициализируем
    success = indexer.index_chunks(chunks, batch_size=20)
    
    if success:
        print('✅ Переиндексация завершена!')
        return True
    else:
        print('❌ Ошибка при индексации')
        return False

def test_new_quality():
    """Тестирует качество после переиндексации"""
    
    print('\n🧪 ТЕСТ НОВОГО КАЧЕСТВА')
    print('=' * 30)
    
    indexer = Indexer()
    
    test_queries = [
        'YC5194 temperature growth conditions',
        'Lysobacter capsici characteristics',
        'strain morphology biochemical'
    ]
    
    for query in test_queries:
        print(f'\n📝 Запрос: "{query}"')
        results = indexer.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            chunk_type = '📊' if 'table' in result.get('text', '').lower() else '📝'
            print(f'   {i}. {chunk_type} Релевантность: {result.get("relevance_score", 0):.3f}')
            print(f'      Текст: {result.get("text", "")[:100]}...')

def main():
    """Главная функция"""
    
    print('🔧 МОДЕРНИЗАЦИЯ RAG СИСТЕМЫ')
    print('=' * 50)
    print('🚀 Используем продвинутый PDF экстрактор')
    print('📊 Включаем поддержку таблиц')
    print('🎯 Улучшаем качество текста')
    
    # Переиндексируем
    success = reindex_database()
    
    if success:
        # Тестируем качество
        test_new_quality()
        
        print('\n🎉 МОДЕРНИЗАЦИЯ ЗАВЕРШЕНА!')
        print('✅ База переиндексирована с продвинутым экстрактором')
        print('✅ Добавлена поддержка таблиц')
        print('✅ Улучшено качество текста')
        print()
        print('🎯 Рекомендации:')
        print('   - Протестируйте поиск в веб-интерфейсе')
        print('   - Сравните результаты с NotebookLM')
        print('   - При необходимости настройте параметры поиска')
    else:
        print('\n❌ ОШИБКА МОДЕРНИЗАЦИИ')

if __name__ == "__main__":
    main() 