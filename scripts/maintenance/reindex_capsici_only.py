#!/usr/bin/env python3
"""
КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Переиндексация статьи о Lysobacter capsici
"""

import sys
import os
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
from lysobacter_rag.indexer.indexer import Indexer

# Простая функция улучшения текста
def improve_text_quality(text):
    import re
    # Основные правила улучшения
    text = re.sub(r'(\w+)\s*-\s*(\d+)\s+T', r'\1-\2T', text)  # Штаммы
    text = re.sub(r'(\d+)\s*[-–]\s*(\d+)\s*°?\s*C', r'\1–\2°C', text)  # Температура
    text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)  # Числа
    return text

print("🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ПЕРЕИНДЕКСАЦИЯ CAPSICI")
print("=" * 60)

# Инициализация
indexer = Indexer()
pdf_extractor = AdvancedPDFExtractor()

# Путь к статье
capsici_file = "data/Lysobacter capsici_sp_nov_with_antimicro.pdf"

if not os.path.exists(capsici_file):
    print(f"❌ Файл не найден: {capsici_file}")
    exit(1)

print(f"📄 Обрабатываю: {capsici_file}")

# Удаляем старые чанки из этого файла
print("🗑️ Удаляю старые чанки...")
try:
    collection = indexer.chroma_client.get_collection(name=config.CHROMA_COLLECTION_NAME)
    
    # Получаем все чанки из файла
    old_chunks = collection.get(where={"source_pdf": "Lysobacter capsici_sp_nov_with_antimicro.pdf"})
    
    if old_chunks['ids']:
        collection.delete(ids=old_chunks['ids'])
        print(f"✅ Удалено {len(old_chunks['ids'])} старых чанков")
    else:
        print("⚠️ Старые чанки не найдены")
        
except Exception as e:
    print(f"❌ Ошибка удаления: {e}")

# Извлекаем текст всеми методами
print("\n📖 ИЗВЛЕЧЕНИЕ ТЕКСТА:")
print("-" * 30)

try:
    # Метод 1: PyMuPDF4LLM (лучше для научных текстов)
    print("1️⃣ PyMuPDF4LLM...")
    content_pymupdf = pdf_extractor.extract_with_pymupdf4llm(capsici_file)
    print(f"   Извлечено: {len(content_pymupdf)} символов")
    
    # Метод 2: pdfplumber (таблицы)
    print("2️⃣ PDFplumber...")
    content_plumber = pdf_extractor.extract_with_pdfplumber(capsici_file)
    print(f"   Извлечено: {len(content_plumber)} символов")
    
    # Метод 3: tabula (таблицы)
    print("3️⃣ Tabula...")
    content_tabula = pdf_extractor.extract_with_tabula(capsici_file)
    print(f"   Извлечено: {len(content_tabula)} символов")
    
    # Объединяем все содержимое
    all_content = f"{content_pymupdf}\n\n{content_plumber}\n\n{content_tabula}"
    
    print(f"\n📊 Всего извлечено: {len(all_content)} символов")
    
    # Улучшаем качество текста
    print("✨ Улучшение качества текста...")
    improved_content = improve_text_quality(all_content)
    
    # Показываем превью
    print(f"\n📝 ПРЕВЬЮ СОДЕРЖАНИЯ:")
    print("-" * 40)
    preview = improved_content[:500]
    print(preview)
    print("...")
    
    # Проверяем наличие ключевых характеристик
    print(f"\n🔍 ПРОВЕРКА КЛЮЧЕВЫХ ХАРАКТЕРИСТИК:")
    print("-" * 40)
    
    keywords = [
        "rhizosphere", "pepper", "Capsicum",
        "YC5194", "type strain",
        "15-37", "temperature", 
        "0.3-0.5", "cell size",
        "65.4", "G+C",
        "catalase", "positive",
        "chitinase"
    ]
    
    found_keywords = []
    for keyword in keywords:
        if keyword.lower() in improved_content.lower():
            found_keywords.append(keyword)
            print(f"✅ {keyword}")
        else:
            print(f"❌ {keyword}")
    
    print(f"\n🎯 Найдено ключевых слов: {len(found_keywords)}/{len(keywords)}")
    
    if len(found_keywords) < 5:
        print("⚠️ ВНИМАНИЕ: Мало ключевых характеристик найдено!")
        print("📋 Показываю первые 1000 символов для анализа:")
        print("-" * 50)
        print(improved_content[:1000])
        print("-" * 50)
    
    # Индексируем
    print(f"\n📚 ИНДЕКСАЦИЯ...")
    print("-" * 20)
    
    success = indexer.add_document(
        content=improved_content,
        source_file=capsici_file
    )
    
    if success:
        print(f"✅ Статья успешно переиндексирована!")
        
        # Проверяем результат
        print(f"\n🧪 ТЕСТ ПОИСКА:")
        print("-" * 20)
        
        test_queries = [
            "YC5194 characteristics",
            "rhizosphere pepper",
            "temperature 15-37",
            "cell size 0.3",
            "G+C content 65.4"
        ]
        
        for query in test_queries:
            results = indexer.search(query, top_k=3)
            
            found_capsici = any('capsici' in r['metadata'].get('source_pdf', '').lower() for r in results)
            
            if found_capsici:
                print(f"✅ '{query}' -> найдено в capsici")
            else:
                print(f"❌ '{query}' -> НЕ найдено в capsici")
        
    else:
        print(f"❌ Ошибка индексации!")

except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎉 ПЕРЕИНДЕКСАЦИЯ ЗАВЕРШЕНА!") 