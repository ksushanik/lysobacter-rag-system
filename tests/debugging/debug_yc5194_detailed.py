#!/usr/bin/env python3
"""
Детальная диагностика извлечения YC5194
"""

import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor

def debug_yc5194_detailed():
    """Детальная диагностика YC5194"""
    
    print("🔬 ДЕТАЛЬНАЯ ДИАГНОСТИКА YC5194")
    print("=" * 50)
    
    # Файл с YC5194
    yc5194_file = Path("data/Lysobacter capsici_sp_nov_with_antimicro.pdf")
    
    if not yc5194_file.exists():
        print(f"❌ Файл не найден: {yc5194_file}")
        return False
    
    print(f"📖 Анализируем: {yc5194_file.name}")
    
    # Создаем экстрактор БЕЗ умного чанкинга
    extractor = AdvancedPDFExtractor(use_smart_chunking=False)
    
    try:
        # Извлекаем документ
        print(f"\n📝 Извлекаем документ...")
        document = extractor.extract_document(yc5194_file)
        
        print(f"✅ Получили {len(document.elements)} элементов")
        
        # Анализируем первые 3 элемента детально
        for i, element in enumerate(document.elements[:3]):
            print(f"\n🔍 ЭЛЕМЕНТ {i}:")
            print(f"   Тип: {type(element)}")
            print(f"   Атрибуты: {dir(element)}")
            
            # Проверяем разные способы получения текста
            text_methods = ['text', 'content', 'get_text', 'to_text']
            found_text = False
            
            for method in text_methods:
                if hasattr(element, method):
                    try:
                        if callable(getattr(element, method)):
                            text = getattr(element, method)()
                        else:
                            text = getattr(element, method)
                        
                        if text:
                            print(f"   ✅ {method}: {len(text)} символов")
                            print(f"      Начало: {text[:100]}...")
                            found_text = True
                            
                            # Ищем YC5194
                            if "YC5194" in text:
                                print(f"      🎯 YC5194 НАЙДЕН!")
                            break
                        else:
                            print(f"   ❌ {method}: пустой")
                    except Exception as e:
                        print(f"   ⚠️ {method}: ошибка - {e}")
            
            if not found_text:
                print(f"   ❌ Текст не найден ни одним способом")
                # Показываем все атрибуты
                print(f"   🔍 Все атрибуты:")
                for attr in dir(element):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(element, attr)
                            if not callable(value):
                                print(f"      {attr}: {type(value)} = {str(value)[:50]}...")
                        except:
                            pass
        
        return True
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_yc5194_detailed() 