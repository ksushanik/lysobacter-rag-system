#!/usr/bin/env python3
"""
Скрипт для переиндексации базы данных с улучшенным качеством текста
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lysobacter_rag.indexer.indexer import Indexer
from lysobacter_rag.pdf_extractor.text_quality_improver import text_quality_improver
from lysobacter_rag.data_processor import DocumentChunk
from loguru import logger
import chromadb
from tqdm import tqdm


def analyze_current_quality():
    """Анализирует текущее качество данных в базе"""
    
    print("🔍 АНАЛИЗ ТЕКУЩЕГО КАЧЕСТВА")
    print("=" * 40)
    
    indexer = Indexer()
    
    # Получаем образцы данных
    test_queries = [
        "YC5194 temperature",
        "Lysobacter capsici",
        "growth conditions",
        "pH temperature range"
    ]
    
    total_quality = 0
    total_samples = 0
    
    for query in test_queries:
        results = indexer.search(query, top_k=3)
        
        print(f"\n📝 Запрос: '{query}'")
        print(f"   Результатов: {len(results)}")
        
        for i, result in enumerate(results, 1):
            text = result.get('text', '')
            if text:
                quality = text_quality_improver.analyze_text_quality(text)
                total_quality += quality['quality_score']
                total_samples += 1
                
                print(f"   {i}. Качество: {quality['quality_score']}%")
                print(f"      Релевантность: {result.get('relevance_score', 0):.3f}")
                print(f"      Проблемы: {quality.get('issues', [])}")
                print(f"      Текст: {text[:100]}...")
    
    avg_quality = total_quality / total_samples if total_samples > 0 else 0
    print(f"\n📊 СРЕДНИЙ ПОКАЗАТЕЛЬ КАЧЕСТВА: {avg_quality:.1f}%")
    
    return avg_quality

def get_all_documents_from_chroma():
    """Получает все документы из ChromaDB для переобработки"""
    
    print("\n📥 ИЗВЛЕЧЕНИЕ ДАННЫХ ИЗ БАЗЫ")
    print("=" * 40)
    
    indexer = Indexer()
    
    try:
        # Получаем все документы
        result = indexer.collection.get(
            include=["documents", "metadatas", "ids"]
        )
        
        print(f"✅ Извлечено документов: {len(result['ids'])}")
        
        # Преобразуем в формат DocumentChunk
        improved_chunks = []
        
        for i, (doc_id, text, metadata) in enumerate(zip(
            result['ids'], 
            result['documents'], 
            result['metadatas']
        )):
            # Улучшаем качество текста
            improved_text = text_quality_improver.improve_text_quality(text)
            
            # Создаём улучшенный чанк
            chunk = DocumentChunk(
                chunk_id=metadata.get('chunk_id', doc_id),
                text=improved_text,
                chunk_type=metadata.get('chunk_type', 'text'),
                metadata=metadata or {}
            )
            
            improved_chunks.append(chunk)
            
            if (i + 1) % 1000 == 0:
                print(f"   Обработано: {i + 1}/{len(result['ids'])}")
        
        print(f"✅ Улучшено чанков: {len(improved_chunks)}")
        return improved_chunks
        
    except Exception as e:
        logger.error(f"Ошибка при извлечении данных: {e}")
        return []

def reindex_with_improvements():
    """Переиндексирует базу с улучшениями качества"""
    
    print("\n🚀 ПЕРЕИНДЕКСАЦИЯ С УЛУЧШЕНИЯМИ")
    print("=" * 40)
    
    # 1. Получаем текущие данные
    improved_chunks = get_all_documents_from_chroma()
    
    if not improved_chunks:
        print("❌ Не удалось получить данные для переиндексации")
        return False
    
    # 2. Создаём новый индексер
    indexer = Indexer()
    
    # 3. Очищаем старую коллекцию
    print("🗑️ Очистка старой коллекцию...")
    indexer.delete_collection()
    
    # 4. Создаём новую коллекцию
    indexer = Indexer()  # Переинициализируем
    
    # 5. Индексируем улучшенные данные
    print("📤 Индексация улучшенных данных...")
    success = indexer.index_chunks(improved_chunks, batch_size=50)
    
    if success:
        print("✅ Переиндексация завершена успешно!")
        return True
    else:
        print("❌ Ошибка при переиндексации")
        return False

def test_improved_quality():
    """Тестирует качество после улучшений"""
    
    print("\n🧪 ТЕСТ УЛУЧШЕННОГО КАЧЕСТВА")
    print("=" * 40)
    
    indexer = Indexer()
    
    # Тестовые запросы
    test_queries = [
        "YC5194 temperature growth",
        "Lysobacter capsici characteristics",
        "strain morphology"
    ]
    
    for query in test_queries:
        print(f"\n📝 Запрос: '{query}'")
        results = indexer.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            text = result.get('text', '')
            quality = text_quality_improver.analyze_text_quality(text)
            
            print(f"   {i}. Релевантность: {result.get('relevance_score', 0):.3f}")
            print(f"      Качество: {quality['quality_score']}%")
            print(f"      Текст: {text[:150]}...")

def main():
    """Главная функция"""
    
    print("🔧 УЛУЧШЕНИЕ КАЧЕСТВА RAG СИСТЕМЫ")
    print("=" * 70)
    
    # 1. Анализируем текущее качество
    quality_before = analyze_current_quality()
    
    # 2. Спрашиваем подтверждение
    if quality_before < 70:
        print(f"\n⚠️ Качество данных низкое ({quality_before:.1f}%)")
        print("🔄 Рекомендуется переиндексация с улучшениями")
        
        confirm = input("\nПродолжить переиндексацию? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Операция отменена")
            return
    else:
        print(f"\n✅ Качество данных приемлемое ({quality_before:.1f}%)")
        confirm = input("Всё равно улучшить? (y/N): ")
        if confirm.lower() != 'y':
            print("✅ Улучшение не требуется")
            return
    
    # 3. Выполняем переиндексацию
    success = reindex_with_improvements()
    
    if success:
        # 4. Тестируем результат
        test_improved_quality()
        
        print("\n🎉 УЛУЧШЕНИЕ ЗАВЕРШЕНО!")
        print("✅ База данных переиндексирована с улучшенным качеством")
        print("✅ Проверьте качество поиска в веб-интерфейсе")
    else:
        print("\n❌ ОШИБКА ПРИ УЛУЧШЕНИИ")
        print("🔧 Проверьте логи для диагностики")

if __name__ == "__main__":
    main() 