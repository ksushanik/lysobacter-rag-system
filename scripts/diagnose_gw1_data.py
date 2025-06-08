#!/usr/bin/env python3
"""
Диагностика качества данных о штамме GW1-59T в векторной базе
"""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def diagnose_gw1_data():
    """Детальная диагностика данных о GW1-59T"""
    
    print("🔍 ДИАГНОСТИКА ДАННЫХ О ШТАММЕ GW1-59T")
    print("=" * 55)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        # Инициализируем индексер
        indexer = Indexer()
        
        # Ищем все упоминания GW1-59T
        search_terms = [
            "GW1-59T",
            "Lysobacter antarcticus",
            "antarcticus", 
            "Antarctica",
            "temperature 30",
            "pH 9-11",
            "NaCl 0-4",
            "gelatin hydrolysis",
            "genome 2.8 Mb"
        ]
        
        print("🔍 Поиск по разным терминам:")
        print("-" * 40)
        
        all_chunks = {}
        
        for term in search_terms:
            print(f"\n📝 Поиск: '{term}'")
            results = indexer.search(term, top_k=5)
            
            if results:
                print(f"   ✅ Найдено {len(results)} результатов")
                
                for i, result in enumerate(results, 1):
                    chunk_id = f"{term}_{i}"
                    all_chunks[chunk_id] = result
                    
                                                              # Проверяем качество текста
                     text = result['text']
                    
                    # Ищем проблемы
                    problems = []
                    
                    # Проверяем пробелы в химических формулах
                    if 'C 15' in text or 'C 16' in text or ': 0' in text:
                        problems.append("Разорванные химические формулы")
                    
                    # Проверяем слитные слова
                    long_words = [word for word in text.split() if len(word) > 50]
                    if long_words:
                        problems.append(f"Слитные слова ({len(long_words)})")
                    
                    # Проверяем разорванные числа
                    if '5 9T' in text or 'GW1-5' in text:
                        problems.append("Разорванные штаммовые номера")
                    
                    # Проверяем наличие ключевых данных
                    key_data = {
                        'температура': any(x in text.lower() for x in ['30°c', '15-37', 'temperature']),
                        'pH': any(x in text.lower() for x in ['ph 9', 'ph 11', 'ph range']),
                        'соленость': any(x in text.lower() for x in ['nacl', '0-4%', 'salt']),
                        'геном': any(x in text.lower() for x in ['2.8 mb', 'genome', '2,784']),
                        'антарктида': any(x in text.lower() for x in ['antarctica', 'antarctic', 'polar'])
                    }
                    
                    print(f"      Результат {i}: Длина {len(text)} символов")
                    if problems:
                        print(f"      ⚠️  Проблемы: {', '.join(problems)}")
                    
                    # Показываем наличие ключевых данных
                    found_data = [k for k, v in key_data.items() if v]
                    if found_data:
                        print(f"      ✅ Найдены данные: {', '.join(found_data)}")
                    else:
                        print(f"      ❌ Ключевые данные не найдены")
                    
                    # Показываем образец
                    if len(text) > 100:
                        print(f"      📄 Образец: {text[:100]}...")
                    else:
                        print(f"      📄 Полный текст: {text}")
            else:
                print(f"   ❌ Результатов не найдено")
        
        # Анализируем лучшие чанки
        print("\n" + "=" * 55)
        print("📊 АНАЛИЗ КАЧЕСТВА ДАННЫХ")
        print("=" * 55)
        
        # Ищем наиболее информативные чанки о GW1-59T
        best_results = indexer.search("GW1-59T Lysobacter antarcticus characteristics temperature pH genome", top_k=10)
        
        if best_results:
            print(f"✅ Найдено {len(best_results)} наиболее релевантных чанков")
            
            # Объединяем все найденные данные
            all_text = " ".join([r['content'] for r in best_results])
            
            # Ищем конкретные данные
            data_found = {
                'Штамм GW1-59T': 'GW1-59T' in all_text or 'GW1-5 9T' in all_text,
                'Вид antarcticus': 'antarcticus' in all_text.lower(),
                'Температура 15-37°C': any(x in all_text for x in ['15-37', '15–37', '30°C', '30 °C']),
                'pH 9-11': any(x in all_text for x in ['pH 9', 'pH 11', '9-11', '9–11']),
                'NaCl 0-4%': any(x in all_text for x in ['0-4%', '0–4%', 'NaCl']),
                'Размер генома': any(x in all_text for x in ['2.8 Mb', '2,784', '2784373']),
                'Антарктида': any(x in all_text.lower() for x in ['antarctica', 'antarctic']),
                'Глубина 95м': '95' in all_text,
                'pH оптимум': any(x in all_text for x in ['pH 9', 'pH 10', 'pH 11']),
                'Желатин': any(x in all_text.lower() for x in ['gelatin', 'желатин']),
                'Q-8 хинон': 'Q-8' in all_text,
                'Оксидаза +': any(x in all_text.lower() for x in ['oxidase', 'оксидаза'])
            }
            
            print("\n📋 ПРОВЕРКА КЛЮЧЕВЫХ ДАННЫХ:")
            for key, found in data_found.items():
                status = "✅" if found else "❌"
                print(f"   {status} {key}")
            
            found_count = sum(data_found.values())
            total_count = len(data_found)
            completeness = (found_count / total_count) * 100
            
            print(f"\n📊 ПОЛНОТА ДАННЫХ: {found_count}/{total_count} ({completeness:.1f}%)")
            
            if completeness < 50:
                print("🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Большая часть данных отсутствует!")
            elif completeness < 75:
                print("⚠️  ПРОБЛЕМА: Значительная часть данных отсутствует")
            else:
                print("✅ Данные в целом присутствуют")
                
            # Показываем где какие данные найдены
            print("\n📍 ДЕТАЛЬНЫЙ АНАЛИЗ ПО ЧАНКАМ:")
            for i, result in enumerate(best_results[:5], 1):
                text = result['content']
                found_in_chunk = [k for k, v in data_found.items() if v and any(term.lower() in text.lower() for term in k.split())]
                print(f"   Чанк {i}: {len(found_in_chunk)} типов данных")
                if found_in_chunk:
                    print(f"      Содержит: {', '.join(found_in_chunk[:3])}{'...' if len(found_in_chunk) > 3 else ''}")
        
        else:
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: Данные о GW1-59T вообще не найдены!")
            
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def suggest_improvements():
    """Предлагает улучшения для индексации"""
    
    print("\n" + "=" * 55)
    print("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ")
    print("=" * 55)
    
    recommendations = [
        "1. 🔧 ПЕРЕИНДЕКСАЦИЯ с улучшенной обработкой PDF:",
        "   • Использовать более продвинутые библиотеки (pdfplumber, pymupdf)",
        "   • Специальная обработка таблиц", 
        "   • Восстановление химических формул (C 15:0 → C15:0)",
        "",
        "2. 📊 УЛУЧШЕНИЕ СЕГМЕНТАЦИИ:",
        "   • Сохранение контекста таблиц",
        "   • Объединение связанных абзацев",
        "   • Специальная обработка числовых данных",
        "",
        "3. 🎯 ОПТИМИЗАЦИЯ ПОИСКА:",
        "   • Добавление синонимов (GW1-59T, antarcticus)",
        "   • Улучшение эмбеддингов для научных терминов",
        "   • Создание специальных индексов для штаммов",
        "",
        "4. ✅ ВАЛИДАЦИЯ ДАННЫХ:",
        "   • Автоматическая проверка извлеченных фактов",
        "   • Сравнение с эталонными источниками",
        "   • Мониторинг качества индексации"
    ]
    
    for rec in recommendations:
        print(rec)

if __name__ == "__main__":
    success = diagnose_gw1_data()
    suggest_improvements()
    
    if not success:
        sys.exit(1) 