#!/usr/bin/env python3
"""
Тест продвинутого PDF экстрактора
"""

import sys
from pathlib import Path
sys.path.insert(0, 'src')

def test_advanced_extractor():
    """Тестирует продвинутый PDF экстрактор"""
    
    print('🧪 ТЕСТ ПРОДВИНУТОГО PDF ЭКСТРАКТОРА')
    print('=' * 50)
    
    try:
        from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
        
        # Ищем PDF файлы
        data_dir = Path('data')
        pdfs = list(data_dir.glob('*capsici*.pdf'))
        if not pdfs:
            pdfs = list(data_dir.glob('*.pdf'))[:1]
        
        if pdfs:
            test_pdf = pdfs[0]
            print(f'📄 Тестируем: {test_pdf.name}')
            
            # Создаём экстрактор
            extractor = AdvancedPDFExtractor()
            
            # Извлекаем документ
            print('⏳ Извлекаю данные...')
            document = extractor.extract_document(test_pdf)
            
            print(f'✅ РЕЗУЛЬТАТЫ:')
            print(f'   📝 Текстовых элементов: {document.extraction_stats["text_elements"]}')
            print(f'   📊 Табличных элементов: {document.extraction_stats["table_elements"]}')
            print(f'   📈 Качество: {document.extraction_stats["quality_score"]:.1f}%')
            print(f'   📄 Страниц: {document.extraction_stats["total_pages"]}')
            print(f'   🔧 Методы: {document.extraction_stats["methods_used"]}')
            
            # Показываем примеры
            print()
            print('📝 ПРИМЕРЫ ИЗВЛЕЧЁННОГО КОНТЕНТА:')
            
            text_elements = [e for e in document.elements if e.element_type == 'text'][:2]
            table_elements = [e for e in document.elements if e.element_type == 'table'][:2]
            
            for i, element in enumerate(text_elements, 1):
                print(f'   Текст {i}: {element.content[:100]}...')
            
            for i, element in enumerate(table_elements, 1):
                print(f'   Таблица {i}: {element.content[:100]}...')
            
            # Ищем YC5194
            yc5194_elements = [e for e in document.elements if 'YC5194' in e.content]
            print(f'🎯 Элементов с YC5194: {len(yc5194_elements)}')
            
            if yc5194_elements:
                print(f'   Пример: {yc5194_elements[0].content[:150]}...')
                
            return document
        else:
            print('❌ PDF файлы не найдены в папке data/')
            return None
            
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_advanced_extractor() 