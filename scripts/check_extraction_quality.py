#!/usr/bin/env python3
"""
Скрипт для проверки качества извлечения текста из PDF документов
"""
import sys
from pathlib import Path

# Добавляем пути
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from lysobacter_rag.indexer.indexer import Indexer

def check_extraction_quality():
    """Проверяет качество извлеченного текста"""
    
    print("🔍 ПРОВЕРКА КАЧЕСТВА ИЗВЛЕЧЕНИЯ ТЕКСТА")
    print("=" * 50)
    
    try:
        # Инициализируем индексер
        indexer = Indexer()
        
        # Получаем статистику
        stats = indexer.get_collection_stats()
        print(f"📊 Всего документов: {stats.get('total_chunks', 0)}")
        
        # Ищем примеры с проблемами
        test_queries = [
            "GW1-59T",
            "temperature",
            "characteristics", 
            "analysis"
        ]
        
        print("\n🔍 ПРОВЕРКА КАЧЕСТВА ТЕКСТА:")
        print("-" * 40)
        
        for query in test_queries:
            print(f"\n📝 Поиск по запросу: '{query}'")
            
            results = indexer.search(query, top_k=3)
            
            for i, result in enumerate(results[:2], 1):
                content = result.get('text', '')
                
                print(f"\n   📄 Результат {i}:")
                print(f"   📋 Длина: {len(content)} символов")
                
                # Проверяем на слитный текст
                words = content.split()
                long_words = [word for word in words if len(word) > 20]
                
                if long_words:
                    print(f"   ⚠️ Найдены подозрительно длинные слова ({len(long_words)}):")
                    for word in long_words[:3]:
                        print(f"      • {word[:50]}...")
                
                # Проверяем на отсутствие пробелов
                no_space_sequences = []
                for i, char in enumerate(content):
                    if i > 0 and char.isupper() and content[i-1].islower():
                        # Возможное место пропуска пробела
                        start = max(0, i-10)
                        end = min(len(content), i+10)
                        no_space_sequences.append(content[start:end])
                
                if no_space_sequences:
                    print(f"   ⚠️ Возможные пропуски пробелов ({len(no_space_sequences[:3])}):")
                    for seq in no_space_sequences[:3]:
                        print(f"      • ...{seq}...")
                
                # Показываем образец текста
                print(f"   📝 Образец (первые 200 символов):")
                print(f"      {content[:200]}...")
                
                if i == 1:
                    print()
        
        print(f"\n{'='*50}")
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("\n💡 Рекомендации:")
        print("   • Если видите слитный текст - включите USE_ENHANCED_EXTRACTOR=True в config.py")
        print("   • Длинные слова могут указывать на проблемы с разбиением")
        print("   • Пропуски пробелов - типичная проблема простых PDF экстракторов")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_extraction_quality() 