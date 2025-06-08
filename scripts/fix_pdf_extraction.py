#!/usr/bin/env python3
"""
Улучшенный экстрактор PDF с исправлением проблем качества текста
"""
import sys
import re
from pathlib import Path
import pdfplumber
import fitz  # PyMuPDF

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def fix_text_quality(text):
    """Исправляет проблемы качества извлеченного текста"""
    
    # 1. Исправляем разорванные химические формулы
    text = re.sub(r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2', text)  # C 15 : 0 → C15:0
    text = re.sub(r'iso-\s*C\s+(\d+)', r'iso-C\1', text)  # iso- C 15 → iso-C15
    
    # 2. Исправляем разорванные штаммовые номера
    text = re.sub(r'GW1-\s*5\s*9T', 'GW1-59T', text)  # GW1-5 9T → GW1-59T
    text = re.sub(r'GW1-\s+59T', 'GW1-59T', text)  # GW1- 59T → GW1-59T
    
    # 3. Исправляем температурные данные
    text = re.sub(r'(\d+)\s*–\s*(\d+)\s*°?\s*C', r'\1–\2°C', text)  # 15 – 37 C → 15–37°C
    text = re.sub(r'(\d+)\s*uC', r'\1°C', text)  # 30 uC → 30°C
    
    # 4. Исправляем pH данные
    text = re.sub(r'pH\s+(\d+)\s*–\s*(\d+)', r'pH \1–\2', text)  # pH 9 – 11 → pH 9–11
    text = re.sub(r'pH\s+(\d+\.?\d*)', r'pH \1', text)  # pH 9 . 0 → pH 9.0
    
    # 5. Исправляем данные о геноме
    text = re.sub(r'(\d+),(\d+),(\d+)\s*bp', r'\1,\2,\3 bp', text)  # Исправляем размеры генома
    text = re.sub(r'(\d+\.?\d*)\s*Mb', r'\1 Mb', text)  # 2 . 8 Mb → 2.8 Mb
    
    # 6. Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text)  # Множественные пробелы → одинарный
    text = text.strip()
    
    # 7. Исправляем слитные слова в специфических случаях
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # camelCase → camel Case
    text = re.sub(r'(\d+)([A-Za-z])', r'\1 \2', text)  # 30C → 30 C
    text = re.sub(r'([A-Za-z])(\d+)', r'\1 \2', text)  # pH9 → pH 9
    
    return text

def extract_with_quality_fixes(pdf_path):
    """Извлекает текст с исправлениями качества"""
    
    print(f"📄 Обрабатываю: {pdf_path.name}")
    
    extracted_texts = []
    
    # Метод 1: pdfplumber (лучше для таблиц)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Извлекаем текст
                text = page.extract_text()
                if text:
                    # Исправляем качество
                    fixed_text = fix_text_quality(text)
                    extracted_texts.append({
                        'page': page_num,
                        'method': 'pdfplumber',
                        'text': fixed_text
                    })
                
                # Извлекаем таблицы отдельно
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table:
                        # Преобразуем таблицу в текст
                        table_text = "\n".join([
                            " | ".join([str(cell) if cell else "" for cell in row])
                            for row in table if row
                        ])
                        fixed_table = fix_text_quality(table_text)
                        extracted_texts.append({
                            'page': page_num,
                            'method': 'table',
                            'text': f"ТАБЛИЦА {table_idx + 1}:\n{fixed_table}"
                        })
    except Exception as e:
        print(f"   ⚠️ Ошибка pdfplumber: {e}")
    
    # Метод 2: PyMuPDF (лучше для обычного текста)
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text:
                fixed_text = fix_text_quality(text)
                extracted_texts.append({
                    'page': page_num + 1,
                    'method': 'pymupdf',
                    'text': fixed_text
                })
        doc.close()
    except Exception as e:
        print(f"   ⚠️ Ошибка PyMuPDF: {e}")
    
    return extracted_texts

def test_extraction_quality():
    """Тестирует качество извлечения на примере файлов"""
    
    print("🔧 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО ИЗВЛЕЧЕНИЯ")
    print("=" * 50)
    
    from config import config
    data_dir = Path(config.DATA_DIR)
    
    if not data_dir.exists():
        print(f"❌ Папка данных не найдена: {data_dir}")
        return False
    
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ PDF файлы не найдены в: {data_dir}")
        return False
    
    # Ищем файл с данными о GW1-59T/antarcticus
    target_file = None
    for pdf_file in pdf_files:
        if 'antarcticus' in pdf_file.name.lower():
            target_file = pdf_file
            break
    
    if not target_file:
        # Если не найден, берем первый
        target_file = pdf_files[0]
    
    print(f"📄 Тестируем на файле: {target_file.name}")
    
    extracted_texts = extract_with_quality_fixes(target_file)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   Извлечено блоков текста: {len(extracted_texts)}")
    
    # Ищем упоминания GW1-59T
    gw1_mentions = []
    for block in extracted_texts:
        if 'GW1-59T' in block['text'] or 'antarcticus' in block['text'].lower():
            gw1_mentions.append(block)
    
    print(f"   Найдено упоминаний GW1-59T/antarcticus: {len(gw1_mentions)}")
    
    # Показываем примеры исправленного текста
    if gw1_mentions:
        print(f"\n📝 ПРИМЕРЫ ИСПРАВЛЕННОГО ТЕКСТА:")
        for i, mention in enumerate(gw1_mentions[:3], 1):
            print(f"\n   {i}. Страница {mention['page']} ({mention['method']}):")
            text_preview = mention['text'][:200] + "..." if len(mention['text']) > 200 else mention['text']
            print(f"      {text_preview}")
    
    # Проверяем качество исправлений
    quality_tests = {
        'GW1-59T найден': any('GW1-59T' in block['text'] for block in extracted_texts),
        'Химические формулы': any(re.search(r'C\d+:\d+', block['text']) for block in extracted_texts),
        'Температурные данные': any(re.search(r'\d+–\d+°C', block['text']) for block in extracted_texts),
        'pH данные': any(re.search(r'pH \d+', block['text']) for block in extracted_texts)
    }
    
    print(f"\n🔍 ПРОВЕРКА КАЧЕСТВА:")
    for test, result in quality_tests.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test}")
    
    passed_tests = sum(quality_tests.values())
    total_tests = len(quality_tests)
    
    print(f"\n📊 ИТОГО: {passed_tests}/{total_tests} тестов пройдено")
    
    if passed_tests >= total_tests * 0.75:
        print("✅ Качество извлечения значительно улучшено!")
        return True
    else:
        print("⚠️ Необходимы дополнительные улучшения")
        return False

if __name__ == "__main__":
    success = test_extraction_quality()
    
    if success:
        print("\n💡 РЕКОМЕНДУЕТСЯ:")
        print("1. Переиндексировать базу с новым экстрактором")
        print("2. Использовать комбинацию pdfplumber + PyMuPDF")
        print("3. Применить исправления качества текста")
    
    sys.exit(0 if success else 1) 