#!/usr/bin/env python3
"""
Проверка правильных данных о штамме GW1-59T из исходного PDF
"""
import sys
import re
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def validate_antarcticus_data():
    """Проверяет данные об antarcticus в исходном PDF"""
    
    print("🔍 ПРОВЕРКА ДАННЫХ О LYSOBACTER ANTARCTICUS GW1-59T")
    print("=" * 60)
    
    try:
        from lysobacter_rag.pdf_extractor.pdf_extractor import PDFExtractor
        
        # Путь к файлу
        pdf_path = Path("data/Lysobacter antarcticus .pdf")
        
        if not pdf_path.exists():
            print(f"❌ Файл не найден: {pdf_path}")
            return False
        
        print(f"📄 Анализирую файл: {pdf_path}")
        
        # Извлекаем текст
        extractor = PDFExtractor()
        document = extractor.extract_pdf(pdf_path)
        
        if not document:
            print("❌ Не удалось извлечь данные из PDF")
            return False
        
        # Объединяем весь текст
        full_text = ""
        for page in document.pages:
            full_text += page.text + "\n"
        
        print(f"📊 Извлечено {len(full_text)} символов из {len(document.pages)} страниц")
        
        # Поиск ключевых данных
        print(f"\n🔍 ПОИСК КЛЮЧЕВЫХ ДАННЫХ:")
        
        # 1. Номер штамма
        strain_patterns = [
            r'GW1-?59T',
            r'GW1-?\s*5\s*9T?',
            r'strain\s+GW1[^\w]*59T?'
        ]
        
        strain_found = False
        for pattern in strain_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                print(f"   ✅ Штамм найден: {matches} (паттерн: {pattern})")
                strain_found = True
        
        if not strain_found:
            print(f"   ❌ Штамм GW1-59T не найден")
        
        # 2. Температура роста
        temp_patterns = [
            r'(\d+)[-–]\s*(\d+)\s*°?C',
            r'temperature[s]?\s+[\w\s]*?(\d+)[-–]\s*(\d+)',
            r'grow[s]?\s+[\w\s]*?(\d+)[-–]\s*(\d+)\s*°?C'
        ]
        
        temp_found = False
        for pattern in temp_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    temp_range = f"{match[0]}–{match[1]}°C"
                    print(f"   ✅ Температура: {temp_range}")
                    temp_found = True
        
        if not temp_found:
            print(f"   ❌ Температурный диапазон не найден")
        
        # 3. pH диапазон
        ph_patterns = [
            r'pH\s*(\d+\.?\d*)[-–]\s*(\d+\.?\d*)',
            r'pH\s+range[s]?\s+[\w\s]*?(\d+\.?\d*)[-–]\s*(\d+\.?\d*)',
            r'grow[s]?\s+[\w\s]*?pH\s*(\d+\.?\d*)[-–]\s*(\d+\.?\d*)'
        ]
        
        ph_found = False
        for pattern in ph_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    ph_range = f"pH {match[0]}–{match[1]}"
                    print(f"   ✅ pH диапазон: {ph_range}")
                    ph_found = True
        
        if not ph_found:
            print(f"   ❌ pH диапазон не найден")
        
        # 4. Жирные кислоты
        fatty_patterns = [
            r'C\s*(\d+)\s*:\s*(\d+)',
            r'fatty\s+acid[s]?\s+[\w\s]*?C\s*(\d+)\s*:\s*(\d+)',
            r'iso[-\s]*C\s*(\d+)\s*:\s*(\d+)'
        ]
        
        fatty_acids = set()
        for pattern in fatty_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches:
                fatty_acids.add(f"C{match[0]}:{match[1]}")
        
        if fatty_acids:
            print(f"   ✅ Жирные кислоты: {', '.join(sorted(fatty_acids))}")
        else:
            print(f"   ❌ Жирные кислоты не найдены")
        
        # 5. Размер генома
        genome_patterns = [
            r'(\d+\.?\d*)\s*(Mb|megabas)',
            r'genome\s+size[s]?\s+[\w\s]*?(\d+\.?\d*)\s*(Mb|megabas)',
            r'(\d+\.?\d*)\s*million\s+base'
        ]
        
        genome_found = False
        for pattern in genome_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    genome_size = f"{match[0]} {match[1]}"
                    print(f"   ✅ Размер генома: {genome_size}")
                    genome_found = True
        
        if not genome_found:
            print(f"   ❌ Размер генома не найден")
        
        # 6. Место находки
        location_patterns = [
            r'Untersee',
            r'Lake\s+Untersee',
            r'Antarctica[n]?\s+lake',
            r'freshwater\s+lake.*Antarctica'
        ]
        
        location_found = False
        for pattern in location_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                print(f"   ✅ Место находки: найдено упоминание '{pattern}'")
                location_found = True
                break
        
        if not location_found:
            print(f"   ❌ Место находки (Lake Untersee) не найдено")
        
        # Поиск конкретных проблемных фрагментов
        print(f"\n🔍 ПОИСК ПРОБЛЕМНЫХ ФРАГМЕНТОВ:")
        
        # Разорванные номера штаммов
        broken_strains = re.findall(r'GW1-?\s*\d+\s+\d+T?', full_text)
        if broken_strains:
            print(f"   ⚠️ Разорванные штаммы: {broken_strains}")
        
        # Разорванные химические формулы
        broken_chem = re.findall(r'C\s+\d+\s*:\s*\d+', full_text)
        if broken_chem:
            print(f"   ⚠️ Разорванные формулы: {broken_chem}")
        
        # Разорванные числа
        broken_numbers = re.findall(r'\d+\s*\.\s*\d+', full_text)
        if broken_numbers:
            print(f"   ⚠️ Разорванные числа: {broken_numbers[:5]}...")
        
        # Ищем эталонные данные
        print(f"\n🎯 ПОИСК ЭТАЛОННЫХ ДАННЫХ:")
        
        reference_data = {
            "pH 9.0–11.0": [r'pH\s*9\.0[^0-9]*11\.0', r'pH.*9[^0-9]*11'],
            "15–37°C": [r'15[^0-9]*37.*°?C', r'15.*37.*temperature'],
            "Untersee": [r'Untersee'],
            "2.8 Mb": [r'2\.8.*Mb', r'2\.8.*megabas'],
            "C15:0": [r'C\s*15\s*:\s*0'],
            "Antarctica": [r'Antarctica[n]?']
        }
        
        found_references = 0
        for ref_name, patterns in reference_data.items():
            found = False
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    print(f"   ✅ {ref_name}: найдено")
                    found = True
                    found_references += 1
                    break
            
            if not found:
                print(f"   ❌ {ref_name}: НЕ найдено")
        
        coverage = int((found_references / len(reference_data)) * 100)
        
        print(f"\n📊 ИТОГОВЫЙ АНАЛИЗ:")
        print(f"   Покрытие эталонных данных: {coverage}% ({found_references}/{len(reference_data)})")
        print(f"   Размер документа: {len(full_text)} символов")
        print(f"   Количество страниц: {len(document.pages)}")
        
        # Показываем фрагмент с GW1-59T
        print(f"\n📋 ФРАГМЕНТ С УПОМИНАНИЕМ ШТАММА:")
        strain_context = find_strain_context(full_text)
        if strain_context:
            print(f"   {strain_context[:200]}...")
        else:
            print(f"   ❌ Контекст не найден")
        
        return coverage >= 50
        
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def find_strain_context(text):
    """Находит контекст вокруг упоминания штамма"""
    
    patterns = [
        r'GW1-?59T',
        r'GW1-?\s*5\s*9T?',
        r'strain\s+GW1[^\w]*59T?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            return text[start:end]
    
    return None

def demonstrate_quality_fixes():
    """Демонстрирует применение улучшений качества"""
    
    print(f"\n🔧 ДЕМОНСТРАЦИЯ УЛУЧШЕНИЙ КАЧЕСТВА:")
    
    # Примеры проблемных текстов
    problem_texts = [
        "strain GW1-5 9T was isolated from Lake",
        "Growth occurs at pH 9 . 0 – 11 . 0 and",
        "temperature range of 15 – 37 °C",
        "fatty acids include C 15 : 0 and iso- C 11 : 0",
        "genome size of 2 . 8 Mb contains 2487 genes"
    ]
    
    # Правила исправления
    quality_rules = [
        (r'GW\s*1-\s*5\s*9\s*T', 'GW1-59T'),
        (r'pH\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'pH \1–\2'),
        (r'(\d+)\s*[-–]\s*(\d+)\s*°?\s*C', r'\1–\2°C'),
        (r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2'),
        (r'iso-\s*C\s+(\d+)', r'iso-C\1'),
        (r'(\d+)\s*\.\s*(\d+)', r'\1.\2'),
    ]
    
    for text in problem_texts:
        fixed_text = text
        for pattern, replacement in quality_rules:
            fixed_text = re.sub(pattern, replacement, fixed_text)
        
        if fixed_text != text:
            print(f"   ✅ '{text}' → '{fixed_text}'")
        else:
            print(f"   ⚪ '{text}' (без изменений)")

if __name__ == "__main__":
    print("🎯 ПРОВЕРКА ДАННЫХ О LYSOBACTER ANTARCTICUS")
    print("=" * 70)
    
    success = validate_antarcticus_data()
    
    # Демонстрируем улучшения
    demonstrate_quality_fixes()
    
    if success:
        print(f"\n✅ ЭТАЛОННЫЕ ДАННЫЕ НАЙДЕНЫ В PDF!")
        print(f"💡 Следующие шаги:")
        print(f"   • Применить правила улучшения качества")
        print(f"   • Переиндексировать с исправленным экстрактором")
        print(f"   • Протестировать улучшенные ответы")
    else:
        print(f"\n⚠️ НЕКОТОРЫЕ ДАННЫЕ ОТСУТСТВУЮТ")
        print(f"💡 Возможные причины:")
        print(f"   • Данные в таблицах или изображениях")
        print(f"   • Проблемы с извлечением из PDF")
        print(f"   • Данные в другом формате")
    
    sys.exit(0 if success else 1) 