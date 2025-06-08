#!/usr/bin/env python3
"""
Быстрая проверка данных о штамме GW1-59T
"""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def quick_check_gw1():
    """Быстрая проверка данных о GW1-59T"""
    
    print("🔍 БЫСТРАЯ ПРОВЕРКА ДАННЫХ О ШТАММЕ GW1-59T")
    print("=" * 50)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        # Инициализируем индексер
        indexer = Indexer()
        
        # Ищем данные о GW1-59T
        search_queries = [
            "GW1-59T",
            "Lysobacter antarcticus",
            "temperature 30 growth",
            "pH 9 11 optimum",
            "genome 2.8 Mb"
        ]
        
        total_problems = 0
        total_found = 0
        
        for query in search_queries:
            print(f"\n📝 Поиск: '{query}'")
            results = indexer.search(query, top_k=3)
            
            if results:
                print(f"   ✅ Найдено {len(results)} результатов")
                total_found += len(results)
                
                for i, result in enumerate(results, 1):
                    text = result['text']
                    
                    # Быстрая проверка проблем
                    problems = []
                    if ': 0' in text:
                        problems.append("Разорванные формулы")
                    if 'GW1-5 9T' in text:
                        problems.append("Разорванный штамм")
                    if len([w for w in text.split() if len(w) > 50]) > 0:
                        problems.append("Слитные слова")
                    
                    total_problems += len(problems)
                    
                    # Показываем образец
                    print(f"      {i}. Длина: {len(text)} символов")
                    if problems:
                        print(f"         ⚠️ Проблемы: {', '.join(problems)}")
                    print(f"         📄 {text[:80]}...")
            else:
                print(f"   ❌ Результатов не найдено")
        
        # Общий анализ
        print(f"\n📊 ИТОГО:")
        print(f"   Найдено результатов: {total_found}")
        print(f"   Выявлено проблем: {total_problems}")
        
        if total_problems > 5:
            print("🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Много ошибок извлечения!")
        elif total_problems > 0:
            print("⚠️ Есть проблемы с качеством данных")
        else:
            print("✅ Качество данных приемлемое")
        
        # Проверим конкретные данные о GW1-59T
        print(f"\n🔍 ПРОВЕРКА КЛЮЧЕВЫХ ДАННЫХ:")
        gw1_results = indexer.search("GW1-59T Lysobacter antarcticus", top_k=10)
        
        if gw1_results:
            all_text = " ".join([r['text'] for r in gw1_results])
            
            key_data = {
                'Штамм GW1-59T': 'GW1-59T' in all_text,
                'Вид antarcticus': 'antarcticus' in all_text.lower(),
                'Температура': any(x in all_text for x in ['15-37', '30°C', 'temperature']),
                'pH': any(x in all_text for x in ['pH 9', 'pH 11']),
                'Геном': any(x in all_text for x in ['2.8', 'genome', 'Mb']),
                'Оксидаза': 'oxidase' in all_text.lower() or 'оксидаза' in all_text.lower()
            }
            
            for key, found in key_data.items():
                status = "✅" if found else "❌"
                print(f"   {status} {key}")
            
            found_count = sum(key_data.values())
            completeness = (found_count / len(key_data)) * 100
            
            print(f"\n📊 ПОЛНОТА: {found_count}/{len(key_data)} ({completeness:.0f}%)")
            
            if completeness < 50:
                print("🚨 КРИТИЧНО: Большинство данных отсутствует!")
                return False
            elif completeness < 80:
                print("⚠️ ПРОБЛЕМА: Много данных отсутствует")
                return False
            else:
                print("✅ Данные в основном присутствуют")
                return True
        else:
            print("❌ КРИТИЧНО: Данные о GW1-59T не найдены!")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_check_gw1()
    
    if not success:
        print("\n💡 РЕКОМЕНДУЕТСЯ:")
        print("1. Переиндексация с улучшенной обработкой PDF")
        print("2. Исправление проблем извлечения текста")
        print("3. Специальная обработка научных данных")
    
    sys.exit(0 if success else 1) 