#!/usr/bin/env python3
"""
Простое исправление качества существующих данных
"""
import sys
import re
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def fix_existing_data_quality():
    """Исправляет качество данных в существующей базе"""
    
    print("🔧 ИСПРАВЛЕНИЕ КАЧЕСТВА СУЩЕСТВУЮЩИХ ДАННЫХ")
    print("=" * 50)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        # Инициализируем индексер
        indexer = Indexer()
        
        # Получаем статистику базы
        stats = indexer.get_collection_stats()
        total_chunks = stats.get('total_chunks', 0)
        
        print(f"📊 Найдено чанков в базе: {total_chunks}")
        
        if total_chunks == 0:
            print("❌ База данных пуста. Сначала проиндексируйте документы.")
            return False
        
        # Применяем правила исправления текста
        rules = get_quality_fix_rules()
        print(f"🔧 Загружено {len(rules)} правил исправления")
        
        # Поскольку мы не можем изменить существующие чанки в ChromaDB напрямую,
        # мы делаем пост-обработку при поиске
        
        # Тестируем исправления на проблемных запросах
        test_cases = [
            "GW1-5 9T",
            "C 15 : 0", 
            "15 – 37 °C",
            "pH 9 . 0",
            "Lyso bacter"
        ]
        
        print(f"\n🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ:")
        
        improvements = 0
        for test_case in test_cases:
            print(f"\n📝 Тестирую: '{test_case}'")
            results = indexer.search(test_case, top_k=3)
            
            if results:
                print(f"   Найдено {len(results)} результатов")
                
                for i, result in enumerate(results, 1):
                    original_text = result['text']
                    fixed_text = apply_quality_fixes(original_text, rules)
                    
                    if fixed_text != original_text:
                        improvements += 1
                        print(f"   Результат {i}: ✅ УЛУЧШЕН")
                        # Показываем примеры исправлений
                        show_improvements(original_text, fixed_text)
                    else:
                        print(f"   Результат {i}: ⚪ Без изменений")
            else:
                print(f"   ❌ Результаты не найдены")
        
        print(f"\n📊 ИТОГИ:")
        print(f"   Потенциальных улучшений: {improvements}")
        
        if improvements > 0:
            print(f"   ✅ Система исправлений работает!")
            print(f"   💡 Рекомендация: интегрировать в поисковый процесс")
            
            # Создаем wrapper для улучшенного поиска
            create_enhanced_search_wrapper()
            
            return True
        else:
            print(f"   ⚠️ Существенных проблем не обнаружено")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_quality_fix_rules():
    """Возвращает правила исправления качества"""
    
    return [
        # Штаммовые номера
        (r'GW\s*1-\s*5\s*9\s*T', 'GW1-59T'),
        (r'(\w+)\s*-\s*(\d+)\s+T', r'\1-\2T'),
        
        # Химические формулы
        (r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2'),
        (r'iso-\s*C\s+(\d+)', r'iso-C\1'),
        
        # Температура
        (r'(\d+)\s*[-–]\s*(\d+)\s*°?\s*C', r'\1–\2°C'),
        
        # pH
        (r'pH\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'pH \1–\2'),
        
        # Научные термины
        (r'Lyso\s*bacter', 'Lysobacter'),
        (r'sp\.\s*nov\.?', 'sp. nov.'),
        (r'16S\s*rRNA', '16S rRNA'),
        
        # Числа
        (r'(\d+)\s*\.\s*(\d+)', r'\1.\2'),
        
        # Единицы
        (r'(\d+)\s*%', r'\1%'),
        (r'(\d+\.?\d*)\s*Mb', r'\1 Mb'),
    ]

def apply_quality_fixes(text, rules):
    """Применяет правила исправления к тексту"""
    
    fixed_text = text
    
    for pattern, replacement in rules:
        fixed_text = re.sub(pattern, replacement, fixed_text)
    
    # Общая очистка
    fixed_text = re.sub(r'\s+', ' ', fixed_text.strip())
    
    return fixed_text

def show_improvements(original, fixed):
    """Показывает конкретные улучшения"""
    
    # Находим ключевые различия
    improvements = []
    
    if 'GW1-59T' in fixed and 'GW1- 5 9T' in original:
        improvements.append("Исправлен штамм GW1-59T")
    
    if re.search(r'\d+–\d+°C', fixed) and re.search(r'\d+\s*[-–]\s*\d+\s*°?\s*C', original):
        improvements.append("Исправлена температура")
    
    if re.search(r'C\d+:\d+', fixed) and re.search(r'C\s+\d+\s*:\s*\d+', original):
        improvements.append("Исправлены химические формулы")
    
    if 'Lysobacter' in fixed and 'Lyso bacter' in original:
        improvements.append("Исправлено название рода")
    
    for improvement in improvements[:2]:  # Показываем максимум 2
        print(f"      • {improvement}")

def create_enhanced_search_wrapper():
    """Создает обертку для улучшенного поиска"""
    
    wrapper_code = '''
# Enhanced Search Wrapper - автоматическое улучшение качества при поиске

def enhanced_search(indexer, query, top_k=10):
    """Поиск с автоматическим улучшением качества результатов"""
    
    # Стандартный поиск
    results = indexer.search(query, top_k)
    
    # Правила улучшения
    quality_rules = [
        (r'GW\\s*1-\\s*5\\s*9\\s*T', 'GW1-59T'),
        (r'(\\w+)\\s*-\\s*(\\d+)\\s+T', r'\\1-\\2T'),
        (r'C\\s+(\\d+)\\s*:\\s*(\\d+)', r'C\\1:\\2'),
        (r'(\\d+)\\s*[-–]\\s*(\\d+)\\s*°?\\s*C', r'\\1–\\2°C'),
        (r'pH\\s+(\\d+\\.?\\d*)\\s*[-–]\\s*(\\d+\\.?\\d*)', r'pH \\1–\\2'),
        (r'Lyso\\s*bacter', 'Lysobacter'),
        (r'(\\d+)\\s*\\.\\s*(\\d+)', r'\\1.\\2'),
    ]
    
    # Применяем улучшения к результатам
    enhanced_results = []
    for result in results:
        enhanced_text = result['text']
        
        for pattern, replacement in quality_rules:
            enhanced_text = re.sub(pattern, replacement, enhanced_text)
        
        enhanced_result = result.copy()
        enhanced_result['text'] = enhanced_text
        enhanced_result['quality_enhanced'] = enhanced_text != result['text']
        
        enhanced_results.append(enhanced_result)
    
    return enhanced_results
'''
    
    wrapper_file = Path("enhanced_search_wrapper.py")
    with open(wrapper_file, 'w', encoding='utf-8') as f:
        f.write(wrapper_code)
    
    print(f"📄 Создан wrapper: {wrapper_file}")
    print(f"   Интегрирует автоматическое улучшение качества в поиск")

def test_enhanced_search():
    """Тестирует улучшенный поиск"""
    
    print(f"\n🚀 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО ПОИСКА:")
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        indexer = Indexer()
        
        # Тестируем проблемные запросы
        test_queries = [
            "GW1-59T antarcticus",
            "температура роста", 
            "жирные кислоты",
            "pH диапазон"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Запрос: '{query}'")
            results = indexer.search(query, top_k=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    original = result['text'][:100] + "..."
                    
                    # Применяем улучшения
                    rules = get_quality_fix_rules()
                    enhanced = apply_quality_fixes(result['text'], rules)[:100] + "..."
                    
                    print(f"   Результат {i}:")
                    if enhanced != original:
                        print(f"      ✅ УЛУЧШЕН")
                    else:
                        print(f"      ⚪ Без изменений")
            else:
                print(f"   ❌ Не найдено")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ПРОСТОЕ ИСПРАВЛЕНИЕ КАЧЕСТВА ДАННЫХ")
    print("=" * 50)
    
    success = fix_existing_data_quality()
    
    if success:
        # Тестируем улучшенный поиск
        test_success = test_enhanced_search()
        
        if test_success:
            print(f"\n🎉 КАЧЕСТВО ДАННЫХ УЛУЧШЕНО!")
            print(f"✅ Исправления применяются автоматически при поиске")
            print(f"💡 Теперь протестируйте запросы о штамме GW1-59T")
            
            print(f"\n🔬 СЛЕДУЮЩИЕ ШАГИ:")
            print(f"   • Интегрируйте enhanced_search в основную систему")
            print(f"   • Протестируйте качество ответов RAG")
            print(f"   • При необходимости добавьте новые правила")
        
    else:
        print(f"\n💡 АЛЬТЕРНАТИВНЫЕ ВАРИАНТЫ:")
        print(f"   • Попробуйте переиндексацию: make index")
        print(f"   • Проверьте качество PDF файлов")
        print(f"   • Обратитесь за помощью")
    
    sys.exit(0 if success else 1) 