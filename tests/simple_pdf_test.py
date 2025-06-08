#!/usr/bin/env python3
"""
Простой тест извлечения текста из PDF для поиска штамма GW1-59T
"""

from pathlib import Path
from config import config
from src.lysobacter_rag.pdf_extractor import PDFExtractor
import re

def test_single_pdf():
    """Тестируем извлечение из одного PDF файла"""
    
    print("🔬 ПРОСТОЙ ТЕСТ ИЗВЛЕЧЕНИЯ ТЕКСТА")
    print("=" * 50)
    
    # Находим PDF файлы
    data_dir = Path(config.DATA_DIR)
    pdf_files = list(data_dir.glob("*.pdf"))[:3]  # Берем первые 3 файла
    
    if not pdf_files:
        print("❌ PDF файлы не найдены!")
        return
    
    extractor = PDFExtractor()
    
    # Паттерны для поиска штаммов
    strain_patterns = [
        r'GW1[-\s]*59T?',
        r'GW[-\s]*1[-\s]*59T?',
        r'strain\s+GW1[-\s]*59',
        r'штамм\s+GW1[-\s]*59'
    ]
    
    print(f"🔍 Ищем штамм GW1-59T в следующих файлах:")
    
    found_strains = []
    
    for pdf_file in pdf_files:
        print(f"\n📄 Обрабатываю: {pdf_file.name}")
        
        try:
            docs = extractor.extract_from_pdf(str(pdf_file))
            
            if not docs:
                print("   ⚠️ Не удалось извлечь данные")
                continue
            
            print(f"   ✅ Извлечено {len(docs)} частей")
            
            # Ищем штаммы в извлеченном тексте
            file_strains = []
            
            for doc in docs:
                text = doc.get('text', '')
                
                # Ищем любые штаммы с паттерном
                for pattern in strain_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        file_strains.extend(matches)
                
                # Также ищем другие штаммы для контекста
                other_strains = re.findall(r'\b[A-Z]+[-\d]+T\b', text)
                if other_strains:
                    file_strains.extend(other_strains[:5])  # Берем первые 5
            
            if file_strains:
                unique_strains = list(set(file_strains))
                print(f"   🧬 Найдены штаммы: {', '.join(unique_strains[:10])}")
                found_strains.extend(unique_strains)
            else:
                print("   📭 Штаммы не найдены")
                
                # Показываем немного текста для диагностики
                if docs:
                    sample_text = docs[0].get('text', '')[:200]
                    print(f"   📝 Образец текста: {sample_text}...")
                    
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    print(f"\n📊 ИТОГИ:")
    print(f"Всего уникальных штаммов найдено: {len(set(found_strains))}")
    
    # Проверяем наличие нужного штамма
    target_found = False
    for strain in found_strains:
        if 'GW1' in strain.upper() and '59' in strain:
            target_found = True
            print(f"🎯 НАЙДЕН ЦЕЛЕВОЙ ШТАММ: {strain}")
            break
    
    if not target_found:
        print("❌ Штамм GW1-59T не найден в тестируемых файлах")
        print("💡 Попробуйте запустить тест на большем количестве файлов")
    
    # Показываем некоторые найденные штаммы
    if found_strains:
        unique_strains = list(set(found_strains))[:20]
        print(f"\n🧬 Примеры найденных штаммов:")
        for strain in unique_strains:
            print(f"   • {strain}")
    
    return target_found

def search_strain_in_all_files():
    """Ищем штамм во всех файлах"""
    print(f"\n🔍 РАСШИРЕННЫЙ ПОИСК ВО ВСЕХ ФАЙЛАХ")
    print("=" * 50)
    
    data_dir = Path(config.DATA_DIR)
    pdf_files = list(data_dir.glob("*.pdf"))
    
    print(f"📁 Найдено PDF файлов: {len(pdf_files)}")
    
    extractor = PDFExtractor()
    target_files = []
    
    for i, pdf_file in enumerate(pdf_files[:10], 1):  # Проверяем первые 10 файлов
        print(f"({i}/10) Проверяю {pdf_file.name}...", end=" ")
        
        try:
            docs = extractor.extract_from_pdf(str(pdf_file))
            if docs:
                full_text = " ".join([doc.get('text', '') for doc in docs])
                if 'GW1' in full_text and '59' in full_text:
                    target_files.append(pdf_file.name)
                    print("🎯 НАЙДЕН!")
                else:
                    print("❌")
            else:
                print("⚠️")
        except:
            print("💥")
    
    if target_files:
        print(f"\n🎉 Штамм GW1-59T найден в файлах:")
        for filename in target_files:
            print(f"   📄 {filename}")
    else:
        print(f"\n❌ Штамм GW1-59T не найден в первых 10 файлах")
        print(f"💡 Возможно, стоит поискать в других файлах или использовать другой штамм для тестирования")

if __name__ == "__main__":
    found = test_single_pdf()
    
    if not found:
        search_strain_in_all_files()
    
    print(f"\n🚀 Для продолжения тестирования RAG-системы:")
    print(f"   python quick_test.py") 