#!/usr/bin/env python3
"""
Быстрая проверка состояния базы данных
"""

import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lysobacter_rag.indexer.indexer import Indexer

def check_database():
    print("📊 ПРОВЕРКА СОСТОЯНИЯ БАЗЫ ДАННЫХ")
    print("=" * 40)
    
    try:
        indexer = Indexer()
        stats = indexer.get_collection_stats()
        
        print(f"✅ База подключена успешно")
        print(f"📦 Всего чанков: {stats.get('total_chunks', 0)}")
        
        if stats.get('total_chunks', 0) > 0:
            print(f"🔍 Тестируем поиск...")
            results = indexer.search("Lysobacter", top_k=3)
            print(f"   Найдено результатов: {len(results)}")
            
            if results:
                print(f"   Лучший результат: релевантность {results[0]['relevance_score']:.3f}")
                print(f"   Источник: {results[0]['metadata'].get('source_pdf', 'N/A')}")
                print(f"   Текст: {results[0]['text'][:100]}...")
        else:
            print("⚠️ База данных пуста!")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к базе: {e}")

if __name__ == "__main__":
    check_database() 