#!/usr/bin/env python3
"""
Детальный анализ извлеченного текста о штамме GW1-59T
"""
import sys
import re
from pathlib import Path
import pdfplumber

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def analyze_gw1_text():
    """Детальный анализ текста о GW1-59T"""
    
    print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ТЕКСТА О ШТАММЕ GW1-59T")
    print("=" * 55)
    
    from config import config
    data_dir = Path(config.DATA_DIR)
    
    # Ищем файл antarcticus
    antarcticus_file = None
    for pdf_file in data_dir.glob("*.pdf"):
        if 'antarcticus' in pdf_file.name.lower():
            antarcticus_file = pdf_file
            break
    
    if not antarcticus_file:
        print("❌ Файл Lysobacter antarcticus не найден!")
        return False
    
    print(f"📄 Анализируем файл: {antarcticus_file.name}")
    
    # Извлекаем весь текст
    all_text_blocks = []
    
    try:
        with pdfplumber.open(antarcticus_file) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    all_text_blocks.append({
                        'page': page_num,
                        'text': text
                    })
                    
                # Также извлекаем таблицы
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table:
                        table_text = "\n".join([
                            " | ".join([str(cell) if cell else "" for cell in row])
                            for row in table if row
                        ])
                        all_text_blocks.append({
                            'page': page_num,
                            'text': f"ТАБЛИЦА {table_idx + 1}:\n{table_text}"
                        })
    except Exception as e:
        print(f"❌ Ошибка извлечения: {e}")
        return False
    
    print(f"📊 Извлечено {len(all_text_blocks)} блоков текста")
    
    # Ищем все варианты упоминания GW1-59T
    gw1_patterns = [
        r'GW1-59T',
        r'GW-\s*59T',
        r'GW\s*1-\s*59\s*T',
        r'GW\s*1-\s*5\s*9\s*T',
        r'strain\s+GW\s*1[-\s]*59\s*T'
    ]
    
    found_blocks = []
    
    print(f"\n🔍 ПОИСК УПОМИНАНИЙ GW1-59T:")
    for pattern in gw1_patterns:
        print(f"\n   Паттерн: {pattern}")
        matches = 0
        
        for block in all_text_blocks:
            if re.search(pattern, block['text'], re.IGNORECASE):
                matches += 1
                if block not in found_blocks:
                    found_blocks.append(block)
                
                # Показываем контекст
                match = re.search(pattern, block['text'], re.IGNORECASE)
                if match:
                    start = max(0, match.start() - 50)
                    end = min(len(block['text']), match.end() + 50)
                    context = block['text'][start:end]
                    print(f"      Страница {block['page']}: ...{context}...")
        
        print(f"      Найдено: {matches} совпадений")
    
    print(f"\n📋 ВСЕГО НАЙДЕНО БЛОКОВ С GW1-59T: {len(found_blocks)}")
    
    # Анализируем ключевые данные в найденных блоках
    if found_blocks:
        print(f"\n🔍 АНАЛИЗ КЛЮЧЕВЫХ ДАННЫХ:")
        
        all_relevant_text = " ".join([block['text'] for block in found_blocks])
        
        # Ищем специфические данные
        data_patterns = {
            'Температура роста': [
                r'temperature.*?(\d+)[-–](\d+).*?°?C',
                r'growth.*?(\d+)[-–](\d+).*?°?C',
                r'(\d+)[-–](\d+)\s*°C',
                r'optimum.*?(\d+)\s*°C'
            ],
            'pH диапазон': [
                r'pH.*?(\d+)[-–](\d+)',
                r'pH.*?range.*?(\d+\.?\d*)[-–](\d+\.?\d*)',
                r'growth.*?pH.*?(\d+)[-–](\d+)'
            ],
            'NaCl толерантность': [
                r'NaCl.*?(\d+)[-–](\d+).*?%',
                r'salt.*?(\d+)[-–](\d+).*?%',
                r'(\d+)[-–](\d+).*?%.*?NaCl'
            ],
            'Размер генома': [
                r'genome.*?(\d+\.?\d*)\s*Mb',
                r'(\d+,\d+,\d+)\s*bp',
                r'size.*?(\d+\.?\d*)\s*Mb'
            ],
            'G+C содержание': [
                r'G.*?C.*?(\d+\.?\d*)\s*%',
                r'(\d+\.?\d*)\s*%.*?G.*?C'
            ],
            'Место выделения': [
                r'Antarctica',
                r'Antarctic',
                r'freshwater lake',
                r'(\d+)\s*m.*?depth',
                r'depth.*?(\d+)\s*m'
            ]
        }
        
        for data_type, patterns in data_patterns.items():
            print(f"\n   📋 {data_type}:")
            found_data = []
            
            for pattern in patterns:
                matches = re.findall(pattern, all_relevant_text, re.IGNORECASE)
                if matches:
                    found_data.extend(matches)
                    for match in matches[:3]:  # Показываем первые 3
                        print(f"      ✅ {match}")
            
            if not found_data:
                print(f"      ❌ Не найдено")
        
        # Ищем таблицы с характеристиками
        print(f"\n📊 ПОИСК ТАБЛИЦ С ХАРАКТЕРИСТИКАМИ:")
        table_blocks = [block for block in found_blocks if 'ТАБЛИЦА' in block['text']]
        
        if table_blocks:
            print(f"   ✅ Найдено {len(table_blocks)} таблиц")
            for i, table in enumerate(table_blocks, 1):
                print(f"\n   Таблица {i} (страница {table['page']}):")
                # Показываем первые строки таблицы
                lines = table['text'].split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"      {line[:80]}...")
        else:
            print(f"   ❌ Таблицы не найдены")
    
    # Проверяем качество извлечения
    print(f"\n🔧 АНАЛИЗ ПРОБЛЕМ КАЧЕСТВА:")
    
    quality_issues = {
        'Разорванные штаммы': 0,
        'Разорванные формулы': 0,
        'Слитные слова': 0,
        'Поврежденные числа': 0
    }
    
    for block in all_text_blocks:
        text = block['text']
        
        # Ищем проблемы
        if re.search(r'GW\s*1[-\s]*5\s*9\s*T', text):
            quality_issues['Разорванные штаммы'] += 1
        
        if re.search(r'C\s+\d+\s*:\s*\d+', text):
            quality_issues['Разорванные формулы'] += 1
        
        # Ищем слова длиннее 50 символов
        long_words = [w for w in text.split() if len(w) > 50]
        if long_words:
            quality_issues['Слитные слова'] += len(long_words)
        
        # Ищем поврежденные числа
        if re.search(r'\d+\s+\.\s+\d+', text):
            quality_issues['Поврежденные числа'] += 1
    
    print(f"   Проблемы найдены:")
    for issue, count in quality_issues.items():
        status = "⚠️" if count > 0 else "✅"
        print(f"      {status} {issue}: {count}")
    
    total_issues = sum(quality_issues.values())
    
    if total_issues == 0:
        print(f"\n✅ КАЧЕСТВО ОТЛИЧНОЕ: Проблем не найдено!")
        return True
    elif total_issues < 5:
        print(f"\n⚠️ КАЧЕСТВО ПРИЕМЛЕМОЕ: {total_issues} проблем")
        return True
    else:
        print(f"\n🚨 ПЛОХОЕ КАЧЕСТВО: {total_issues} проблем")
        return False

if __name__ == "__main__":
    success = analyze_gw1_text()
    
    if not success:
        print("\n💡 НЕОБХОДИМО:")
        print("1. Улучшить регулярные выражения для исправления")
        print("2. Добавить постобработку извлеченного текста")
        print("3. Улучшить обработку таблиц")
    
    sys.exit(0 if success else 1) 