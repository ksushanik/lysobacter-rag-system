#!/usr/bin/env python3
"""
Тест качества извлечения YC5194 с анализом предупреждений
"""

import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor

def test_yc5194_extraction():
    """Тестирует качество извлечения YC5194"""
    
    print("🔍 ТЕСТ КАЧЕСТВА ИЗВЛЕЧЕНИЯ YC5194")
    print("=" * 50)
    
    # Файл с YC5194
    yc5194_file = Path("data/Lysobacter capsici_sp_nov_with_antimicro.pdf")
    
    if not yc5194_file.exists():
        print(f"❌ Файл не найден: {yc5194_file}")
        return False
    
    print(f"📖 Тестируем: {yc5194_file.name}")
    
    # Создаем экстрактор
    extractor = AdvancedPDFExtractor(use_smart_chunking=True)
    
    try:
        # Извлекаем документ
        print("\n📝 Извлекаем документ...")
        document = extractor.extract_document(yc5194_file)
        
        if not document.elements:
            print("❌ Нет элементов")
            return False
            
        print(f"✅ Извлечено {len(document.elements)} элементов")
        
        # Получаем чанки
        print("\n🧬 Применяем умный чанкинг...")
        chunks = extractor.get_smart_chunks(document)
        
        if not chunks:
            print("❌ Нет чанков")
            return False
        
        chunk_sizes = [len(chunk['content']) for chunk in chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes)
        print(f"✅ Создано {len(chunks)} чанков, ср. размер {avg_size:.0f} символов")
        
        # Ищем YC5194 в чанках
        print(f"\n🎯 ПОИСК YC5194 В ЧАНКАХ:")
        yc5194_chunks = []
        
        for i, chunk in enumerate(chunks):
            content = chunk['content']
            if "YC5194" in content:
                yc5194_chunks.append(i)
                print(f"\n📍 Чанк {i} (размер {len(content)} символов):")
                print(f"   {content[:200]}...")
                
                # Проверяем на проблемные символы
                issues = []
                if "°C" not in content and ("temperature" in content.lower() or "temp" in content.lower()):
                    issues.append("Возможна потеря символа °C")
                if "μm" not in content and ("microm" in content.lower() or "size" in content.lower()):
                    issues.append("Возможна потеря символа μm")
                if "%" not in content and ("percent" in content.lower() or "concentration" in content.lower()):
                    issues.append("Возможна потеря символа %")
                
                if issues:
                    print(f"   ⚠️ Потенциальные проблемы:")
                    for issue in issues:
                        print(f"      - {issue}")
                else:
                    print(f"   ✅ Символы сохранены корректно")
        
        if not yc5194_chunks:
            print("❌ YC5194 НЕ НАЙДЕН в чанках!")
            
            # Проверяем исходные элементы
            print(f"\n🔍 Проверяем исходные элементы...")
            yc5194_in_elements = False
            for i, element in enumerate(document.elements):
                if hasattr(element, 'text') and element.text and "YC5194" in element.text:
                    yc5194_in_elements = True
                    print(f"   ✅ YC5194 найден в элементе {i}")
                    print(f"   Тип: {element.element_type}")
                    print(f"   Текст: {element.text[:200]}...")
                    break
            
            if not yc5194_in_elements:
                print(f"   ❌ YC5194 НЕ НАЙДЕН даже в исходных элементах!")
                print(f"   🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА ИЗВЛЕЧЕНИЯ!")
                return False
            else:
                print(f"   ⚠️ YC5194 есть в элементах, но потерян при чанкинге")
                return False
        else:
            print(f"\n✅ YC5194 найден в {len(yc5194_chunks)} чанках")
        
        # Проверяем ключевые термины
        print(f"\n🔑 ПРОВЕРКА КЛЮЧЕВЫХ ТЕРМИНОВ:")
        key_terms = [
            "Lysobacter capsici",
            "YC5194", 
            "temperature",
            "pH",
            "G+C content",
            "antimicrobial",
            "ризосфера",  # может быть на русском
            "rhizosphere"
        ]
        
        found_terms = {}
        for term in key_terms:
            found_terms[term] = 0
            for chunk in chunks:
                if term.lower() in chunk['content'].lower():
                    found_terms[term] += 1
        
        for term, count in found_terms.items():
            if count > 0:
                print(f"   ✅ {term}: найден в {count} чанках")
            else:
                print(f"   ❌ {term}: НЕ НАЙДЕН")
        
        # Итоговая оценка
        total_terms = len(key_terms)
        found_count = sum(1 for count in found_terms.values() if count > 0)
        success_rate = (found_count / total_terms) * 100
        
        print(f"\n📊 ИТОГОВАЯ ОЦЕНКА:")
        print(f"   Найдено терминов: {found_count}/{total_terms} ({success_rate:.1f}%)")
        print(f"   YC5194 чанков: {len(yc5194_chunks)}")
        print(f"   Средний размер чанка: {avg_size:.0f} символов")
        
        if len(yc5194_chunks) > 0 and success_rate >= 70:
            print(f"   🎉 КАЧЕСТВО ИЗВЛЕЧЕНИЯ: ХОРОШЕЕ")
            return True
        elif len(yc5194_chunks) > 0:
            print(f"   ⚠️ КАЧЕСТВО ИЗВЛЕЧЕНИЯ: УДОВЛЕТВОРИТЕЛЬНОЕ")
            return True
        else:
            print(f"   ❌ КАЧЕСТВО ИЗВЛЕЧЕНИЯ: ПЛОХОЕ")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_yc5194_extraction()
    if success:
        print(f"\n✅ YC5194 извлекается корректно")
    else:
        print(f"\n❌ Проблемы с извлечением YC5194")
    exit(0 if success else 1) 