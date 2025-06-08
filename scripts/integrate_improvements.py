#!/usr/bin/env python3
"""
Интеграция всех улучшений в основную RAG систему
Проверяет и применяет все нововведения
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_integration_status():
    """Проверяет статус интеграции всех улучшений"""
    
    print("🔍 ПРОВЕРКА ИНТЕГРАЦИИ УЛУЧШЕНИЙ")
    print("=" * 50)
    
    integration_status = {}
    
    # 1. Проверка конфигурации
    print("📁 1. Конфигурация...")
    try:
        from config import config
        has_enhanced_setting = hasattr(config, 'USE_ENHANCED_EXTRACTOR')
        integration_status['config'] = {
            'available': True,
            'enhanced_extractor_setting': has_enhanced_setting,
            'value': getattr(config, 'USE_ENHANCED_EXTRACTOR', False)
        }
        print(f"   ✅ Конфигурация: {config.USE_ENHANCED_EXTRACTOR}")
    except Exception as e:
        integration_status['config'] = {'available': False, 'error': str(e)}
        print(f"   ❌ Ошибка конфигурации: {e}")
    
    # 2. Проверка продвинутого экстрактора
    print("🚀 2. Продвинутый PDF экстрактор...")
    try:
        from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
        extractor = AdvancedPDFExtractor()
        integration_status['advanced_extractor'] = {'available': True}
        print("   ✅ Продвинутый экстрактор: доступен")
    except ImportError as e:
        integration_status['advanced_extractor'] = {'available': False, 'error': str(e)}
        print(f"   ❌ Ошибка импорта экстрактора: {e}")
    except Exception as e:
        integration_status['advanced_extractor'] = {'available': False, 'error': str(e)}
        print(f"   ❌ Ошибка инициализации экстрактора: {e}")
    
    # 3. Проверка улучшений качества текста
    print("📝 3. Улучшения качества текста...")
    try:
        from lysobacter_rag.pdf_extractor.text_quality_improver import text_quality_improver
        test_text = "growthofstrain PB-6250"
        improved = text_quality_improver.improve_text_quality(test_text)
        integration_status['text_improver'] = {
            'available': True,
            'test_input': test_text,
            'test_output': improved
        }
        print(f"   ✅ Улучшения качества: {test_text} → {improved}")
    except Exception as e:
        integration_status['text_improver'] = {'available': False, 'error': str(e)}
        print(f"   ❌ Ошибка улучшений качества: {e}")
    
    # 4. Проверка интеграции в main.py
    print("🔧 4. Интеграция в основную систему...")
    try:
        main_py = Path(__file__).parent / "main.py"
        if main_py.exists():
            content = main_py.read_text(encoding='utf-8')
            has_advanced_import = 'advanced_pdf_extractor' in content
            has_enhanced_logic = 'USE_ENHANCED_EXTRACTOR' in content
            integration_status['main_integration'] = {
                'file_exists': True,
                'has_advanced_import': has_advanced_import,
                'has_enhanced_logic': has_enhanced_logic
            }
            print(f"   ✅ Интеграция в main.py: {has_advanced_import and has_enhanced_logic}")
        else:
            integration_status['main_integration'] = {'file_exists': False}
            print("   ❌ Файл main.py не найден")
    except Exception as e:
        integration_status['main_integration'] = {'available': False, 'error': str(e)}
        print(f"   ❌ Ошибка проверки main.py: {e}")
    
    # 5. Проверка RAG пайплайна
    print("🧠 5. RAG пайплайн...")
    try:
        from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
        # Проверяем, что пайплайн может работать с табличными данными
        pipeline_content = Path(__file__).parent.parent / "src" / "lysobacter_rag" / "rag_pipeline" / "rag_pipeline.py"
        if pipeline_content.exists():
            content = pipeline_content.read_text(encoding='utf-8')
            has_table_support = 'table' in content.lower() and 'chunk_type' in content
            integration_status['rag_pipeline'] = {
                'available': True,
                'has_table_support': has_table_support
            }
            print(f"   ✅ RAG пайплайн: поддержка таблиц - {has_table_support}")
        else:
            integration_status['rag_pipeline'] = {'available': False}
            print("   ❌ RAG пайплайн не найден")
    except Exception as e:
        integration_status['rag_pipeline'] = {'available': False, 'error': str(e)}
        print(f"   ❌ Ошибка RAG пайплайна: {e}")
    
    # 6. Проверка веб-интерфейса
    print("🌐 6. Веб-интерфейс...")
    try:
        web_app = Path(__file__).parent.parent / "examples" / "streamlit_app.py"
        if web_app.exists():
            content = web_app.read_text(encoding='utf-8')
            has_enhanced_rag = 'enhanced_rag' in content.lower()
            integration_status['web_interface'] = {
                'available': True,
                'has_enhanced_rag': has_enhanced_rag
            }
            print(f"   ✅ Веб-интерфейс: поддержка enhanced RAG - {has_enhanced_rag}")
        else:
            integration_status['web_interface'] = {'available': False}
            print("   ❌ Веб-интерфейс не найден")
    except Exception as e:
        integration_status['web_interface'] = {'available': False, 'error': str(e)}
        print(f"   ❌ Ошибка веб-интерфейса: {e}")
    
    # 7. Проверка зависимостей
    print("📦 7. Новые зависимости...")
    dependencies = ['pymupdf4llm', 'pdfplumber', 'tabula']
    missing_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}: установлен")
        except ImportError:
            missing_deps.append(dep)
            print(f"   ❌ {dep}: не установлен")
    
    integration_status['dependencies'] = {
        'required': dependencies,
        'missing': missing_deps,
        'all_installed': len(missing_deps) == 0
    }
    
    return integration_status

def run_integration_test():
    """Запускает тест интеграции всех компонентов"""
    
    print("\n🧪 ТЕСТ ИНТЕГРАЦИИ")
    print("=" * 30)
    
    try:
        # Тест 1: Продвинутый экстрактор
        print("1. Тестирую продвинутый экстрактор...")
        from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
        extractor = AdvancedPDFExtractor()
        print("   ✅ Экстрактор инициализирован")
        
        # Тест 2: Основная система с конфигурацией
        print("2. Тестирую основную систему...")
        from config import config
        if config.USE_ENHANCED_EXTRACTOR:
            print("   ✅ Продвинутый экстрактор включен в конфигурации")
        else:
            print("   ⚠️ Продвинутый экстрактор отключен в конфигурации")
        
        # Тест 3: RAG пайплайн
        print("3. Тестирую RAG пайплайн...")
        from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
        print("   ✅ RAG пайплайн доступен")
        
        # Тест 4: Индексер
        print("4. Тестирую индексер...")
        from lysobacter_rag.indexer.indexer import Indexer
        indexer = Indexer()
        stats = indexer.get_collection_stats()
        print(f"   ✅ Индексер: {stats.get('total_chunks', 0)} чанков")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка интеграции: {e}")
        return False

def generate_integration_report(status):
    """Генерирует отчет об интеграции"""
    
    print("\n📊 ОТЧЕТ ОБ ИНТЕГРАЦИИ")
    print("=" * 40)
    
    # Подсчитываем успешные интеграции
    total_components = len(status)
    successful_components = 0
    
    for component, info in status.items():
        if isinstance(info, dict) and info.get('available', False):
            successful_components += 1
    
    success_rate = (successful_components / total_components) * 100
    
    print(f"📈 Готовность системы: {success_rate:.1f}% ({successful_components}/{total_components})")
    print()
    
    # Детальный анализ
    for component, info in status.items():
        component_name = {
            'config': '⚙️ Конфигурация',
            'advanced_extractor': '🚀 Продвинутый экстрактор',
            'text_improver': '📝 Улучшения качества',
            'main_integration': '🔧 Интеграция в main.py',
            'rag_pipeline': '🧠 RAG пайплайн',
            'web_interface': '🌐 Веб-интерфейс',
            'dependencies': '📦 Зависимости'
        }.get(component, component)
        
        if isinstance(info, dict):
            if info.get('available', False):
                print(f"✅ {component_name}: Готов")
                if component == 'config' and 'value' in info:
                    print(f"   └─ Продвинутый экстрактор: {'включен' if info['value'] else 'отключен'}")
                elif component == 'text_improver' and 'test_output' in info:
                    print(f"   └─ Тест: {info['test_input']} → {info['test_output']}")
                elif component == 'dependencies' and 'missing' in info:
                    if info['missing']:
                        print(f"   └─ Отсутствуют: {', '.join(info['missing'])}")
                    else:
                        print(f"   └─ Все зависимости установлены")
            else:
                print(f"❌ {component_name}: Проблемы")
                if 'error' in info:
                    print(f"   └─ Ошибка: {info['error']}")
        else:
            print(f"⚠️ {component_name}: Неизвестный статус")
    
    print()
    
    # Рекомендации
    print("🎯 РЕКОМЕНДАЦИИ:")
    
    if success_rate >= 90:
        print("🎉 Система полностью готова к работе!")
        print("   • Все компоненты интегрированы")
        print("   • Можно использовать продвинутые возможности")
        print("   • Рекомендуется протестировать с реальными данными")
    elif success_rate >= 70:
        print("✅ Система в основном готова")
        print("   • Основные компоненты работают")
        print("   • Есть незначительные проблемы")
        print("   • Рекомендуется устранить оставшиеся проблемы")
    else:
        print("⚠️ Система требует доработки")
        print("   • Много критических проблем")
        print("   • Необходимо устранить ошибки")
        print("   • Не рекомендуется использовать в продакшене")
    
    return success_rate

def main():
    """Главная функция проверки интеграции"""
    
    print("🔧 ПРОВЕРКА ИНТЕГРАЦИИ ВСЕХ УЛУЧШЕНИЙ")
    print("=" * 70)
    print("🚀 Продвинутый PDF экстрактор (pymupdf4llm + pdfplumber + tabula)")
    print("📊 Поддержка таблиц")
    print("🎯 Улучшения качества текста")
    print("🧠 Интеграция в RAG пайплайн")
    print("🌐 Поддержка в веб-интерфейсе")
    print()
    
    # Проверяем интеграцию
    status = check_integration_status()
    
    # Запускаем тест
    test_success = run_integration_test()
    
    # Генерируем отчет
    success_rate = generate_integration_report(status)
    
    # Итоговый результат
    print("\n🏁 ИТОГИ:")
    print("=" * 20)
    
    if test_success and success_rate >= 90:
        print("🎉 ВСЕ УЛУЧШЕНИЯ УСПЕШНО ИНТЕГРИРОВАНЫ!")
        print("✅ Система готова к продвинутой работе")
        return True
    elif test_success and success_rate >= 70:
        print("✅ Основные улучшения интегрированы")
        print("⚠️ Есть незначительные проблемы")
        return True
    else:
        print("❌ Интеграция не завершена")
        print("🔧 Требуется дополнительная работа")
        return False

if __name__ == "__main__":
    main() 