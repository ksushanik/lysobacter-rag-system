#!/usr/bin/env python3
"""
Диагностика качества извлечения PDF с анализом потери символов
"""

import sys
import os
from pathlib import Path
import re
from collections import defaultdict

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor

def diagnose_extraction_quality():
    """Диагностирует качество извлечения PDF"""
    
    print("🔬 ДИАГНОСТИКА КАЧЕСТВА ИЗВЛЕЧЕНИЯ PDF")
    print("=" * 60)
    print("🎯 ЦЕЛЬ: Выявить потери научных символов и данных")
    print()
    
    # Список критичных символов для научных текстов
    critical_symbols = {
        "°C": "градусы Цельсия",
        "μm": "микрометры", 
        "μg": "микрограммы",
        "μl": "микролитры",
        "%": "проценты",
        "±": "плюс-минус",
        "α": "альфа",
        "β": "бета", 
        "γ": "гамма",
        "≥": "больше равно",
        "≤": "меньше равно",
        "–": "тире (не дефис)",
        "×": "умножение",
        "²": "в квадрате",
        "³": "в кубе"
    }
    
    # Паттерны для поиска научных данных
    scientific_patterns = {
        "temperature": r"(\d+)\s*[°]?[Cc]",
        "ph_values": r"pH\s*(\d+\.?\d*)",
        "concentration": r"(\d+\.?\d*)\s*[%]",
        "size_microns": r"(\d+\.?\d*)\s*[μ]?m",
        "time_hours": r"(\d+)\s*h",
        "molecular_weight": r"(\d+\.?\d*)\s*kDa"
    }
    
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ Директория данных не найдена: {data_dir}")
        return False
    
    # Тестируем несколько PDF файлов
    test_files = [
        "Lysobacter capsici_sp_nov_with_antimicro.pdf",  # YC5194
        "Lysobacter agri.pdf",
        "Lysobacter alkalisoli.pdf",
        "Lysobacter antibioticus.pdf",
        "Lysobacter brunescens.pdf"
    ]
    
    extractor = AdvancedPDFExtractor(use_smart_chunking=False)
    
    total_files = 0
    problem_files = 0
    symbol_losses = defaultdict(int)
    data_patterns_found = defaultdict(int)
    
    for file_name in test_files:
        file_path = data_dir / file_name
        if not file_path.exists():
            print(f"⚠️ Файл не найден: {file_name}")
            continue
            
        total_files += 1
        print(f"\n📖 Тестируем: {file_name}")
        
        try:
            # Извлекаем документ
            document = extractor.extract_document(file_path)
            
            if not document.elements:
                print(f"   ❌ Нет элементов")
                problem_files += 1
                continue
            
            # Объединяем весь текст
            full_text = ""
            for element in document.elements:
                if hasattr(element, 'content') and element.content:
                    full_text += element.content + " "
                elif hasattr(element, 'text') and element.text:
                    full_text += element.text + " "
            
            print(f"   📄 Извлечено текста: {len(full_text)} символов")
            
            if len(full_text) < 1000:
                print(f"   ⚠️ Подозрительно мало текста!")
                problem_files += 1
            
            # Проверяем критичные символы
            missing_symbols = []
            found_symbols = []
            
            for symbol, description in critical_symbols.items():
                if symbol in full_text:
                    found_symbols.append(symbol)
                else:
                    # Проверяем, есть ли контекст для этого символа
                    context_words = {
                        "°C": ["temperature", "temp", "celsius", "degree"],
                        "μm": ["microm", "size", "diameter", "length", "width"],
                        "%": ["percent", "concentration", "content"],
                        "±": ["plus", "minus", "error", "deviation"],
                        "pH": ["ph", "acid", "alkaline"]
                    }
                    
                    if symbol in context_words:
                        for word in context_words[symbol]:
                            if word.lower() in full_text.lower():
                                missing_symbols.append(f"{symbol} ({description})")
                                symbol_losses[symbol] += 1
                                break
            
            if missing_symbols:
                print(f"   ❌ Потеряны символы: {', '.join(missing_symbols)}")
                problem_files += 1
            else:
                print(f"   ✅ Символы сохранены: {', '.join(found_symbols)}")
            
            # Проверяем научные паттерны
            patterns_found = 0
            for pattern_name, pattern in scientific_patterns.items():
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    patterns_found += 1
                    data_patterns_found[pattern_name] += len(matches)
                    print(f"   📊 {pattern_name}: найдено {len(matches)} значений")
            
            if patterns_found == 0:
                print(f"   ⚠️ Научные данные не найдены!")
                problem_files += 1
                
        except Exception as e:
            print(f"   ❌ Ошибка извлечения: {e}")
            problem_files += 1
    
    # Итоговая статистика
    print(f"\n" + "=" * 60)
    print(f"📊 ИТОГОВАЯ ДИАГНОСТИКА:")
    print(f"   Протестировано файлов: {total_files}")
    print(f"   Проблемных файлов: {problem_files} ({problem_files/total_files*100:.1f}%)")
    
    if symbol_losses:
        print(f"\n⚠️ ПОТЕРИ СИМВОЛОВ:")
        for symbol, count in symbol_losses.items():
            print(f"   {symbol}: потерян в {count} файлах")
    
    if data_patterns_found:
        print(f"\n✅ НАЙДЕННЫЕ НАУЧНЫЕ ДАННЫЕ:")
        for pattern, count in data_patterns_found.items():
            print(f"   {pattern}: {count} значений")
    
    # Рекомендации
    print(f"\n🚀 РЕКОМЕНДАЦИИ:")
    
    if problem_files > total_files * 0.3:  # Более 30% проблемных
        print(f"   🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: {problem_files/total_files*100:.1f}% файлов с проблемами")
        print(f"   💡 Необходимо:")
        print(f"      1. Установить дополнительные шрифты")
        print(f"      2. Настроить Unicode mapping")
        print(f"      3. Использовать альтернативные экстракторы")
    elif symbol_losses:
        print(f"   ⚠️ УМЕРЕННЫЕ ПРОБЛЕМЫ: Потери символов")
        print(f"   💡 Рекомендуется:")
        print(f"      1. Проверить настройки шрифтов")
        print(f"      2. Добавить постобработку текста")
    else:
        print(f"   ✅ КАЧЕСТВО ПРИЕМЛЕМОЕ")
        print(f"   💡 Можно продолжать с текущими настройками")
    
    return problem_files < total_files * 0.5  # Успех если менее 50% проблемных

if __name__ == "__main__":
    success = diagnose_extraction_quality()
    exit(0 if success else 1)
 