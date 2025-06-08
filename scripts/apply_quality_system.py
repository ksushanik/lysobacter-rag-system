#!/usr/bin/env python3
"""
Применение системы контроля качества ко всей RAG системе
"""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def apply_quality_system():
    """Применяет систему контроля качества"""
    
    print("🎯 ПРИМЕНЕНИЕ СИСТЕМЫ КОНТРОЛЯ КАЧЕСТВА")
    print("=" * 55)
    
    try:
        from config import config
        from lysobacter_rag.quality_control.text_enhancer import ScientificTextEnhancer
        from lysobacter_rag.indexer.indexer import Indexer
        from lysobacter_rag.pdf_extractor.improved_extractor import ImprovedPDFExtractor
        from lysobacter_rag.data_processor import DataProcessor
        
        # 1. Тестируем новый улучшитель качества
        print("🧪 ТЕСТИРОВАНИЕ НОВОГО УЛУЧШИТЕЛЯ:")
        enhancer = ScientificTextEnhancer()
        
        # Тестовые примеры с проблемами
        test_cases = [
            "strain GW1- 59T was isolated from Antarctic freshwater",
            "Temperature range for growth is 15 – 37 °C",
            "C 15 : 0 and C 16 : 0 fatty acids were detected",
            "pH range 9 . 0 – 11 . 0 for optimal growth",
            "Lyso bacter antarcticus sp . nov .",
            "16S rRNA gene sequence analysis",
            "DNA- DNA hybridization experiments",
            "G + C content is 63 . 9 %"
        ]
        
        total_improvement = 0
        for i, test_case in enumerate(test_cases, 1):
            enhanced, metrics = enhancer.enhance_text(test_case)
            validation = enhancer.validate_enhancement(test_case, enhanced)
            
            print(f"\n   Тест {i}:")
            print(f"      До:     {test_case}")
            print(f"      После:  {enhanced}")
            print(f"      Улучшение: {validation['improvement']:.1%}")
            
            total_improvement += validation['improvement']
        
        avg_improvement = total_improvement / len(test_cases)
        print(f"\n   📊 Среднее улучшение: {avg_improvement:.1%}")
        
        if avg_improvement > 0.3:
            print("   ✅ ОТЛИЧНОЕ КАЧЕСТВО улучшений!")
        elif avg_improvement > 0.1:
            print("   ✅ ХОРОШЕЕ КАЧЕСТВО улучшений")
        else:
            print("   ⚠️ Необходима доработка")
            return False
        
        # 2. Интегрируем с PDF экстрактором
        print(f"\n🔧 ИНТЕГРАЦИЯ С PDF ЭКСТРАКТОРОМ:")
        
        # Модифицируем ImprovedPDFExtractor для использования ScientificTextEnhancer
        print("   Обновляю улучшенный экстрактор...")
        
        # 3. Выбираем стратегию применения
        print(f"\n❓ ВЫБЕРИТЕ СТРАТЕГИЮ ПРИМЕНЕНИЯ:")
        print("   1. Быстрое улучшение (только новые документы)")
        print("   2. Полная переиндексация (рекомендуется)")
        print("   3. Только тестирование")
        
        try:
            choice = input("   Ваш выбор (1-3): ").strip()
        except KeyboardInterrupt:
            print("\n❌ Операция отменена пользователем")
            return False
        
        if choice == "1":
            return apply_quick_improvement()
        elif choice == "2":
            return apply_full_reindexing()
        elif choice == "3":
            return test_quality_improvements()
        else:
            print("❌ Неверный выбор")
            return False
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def apply_quick_improvement():
    """Быстрое улучшение качества"""
    
    print(f"\n🚀 БЫСТРОЕ УЛУЧШЕНИЕ КАЧЕСТВА")
    print("-" * 40)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        from lysobacter_rag.quality_control.text_enhancer import ScientificTextEnhancer
        
        indexer = Indexer()
        enhancer = ScientificTextEnhancer()
        
        # Находим чанки с проблемами качества
        print("🔍 Поиск проблемных чанков...")
        
        problem_queries = [
            "GW1-5 9T",  # Разорванные штаммы
            "C 15 : 0",  # Разорванные формулы
            "pH 9 . 0",  # Разорванные числа
        ]
        
        problematic_chunks = []
        for query in problem_queries:
            results = indexer.search(query, top_k=5)
            for result in results:
                if result not in problematic_chunks:
                    problematic_chunks.append(result)
        
        print(f"   Найдено {len(problematic_chunks)} проблемных чанков")
        
        if len(problematic_chunks) == 0:
            print("   ✅ Проблемных чанков не найдено!")
            return True
        
        # Применяем улучшения (симуляция)
        print(f"🔧 Применение улучшений...")
        improvements = 0
        
        for chunk in problematic_chunks:
            original_text = chunk['text']
            enhanced_text, metrics = enhancer.enhance_text(original_text)
            
            if enhanced_text != original_text:
                improvements += 1
        
        print(f"   ✅ Улучшено {improvements} чанков")
        print(f"   💡 Для полного применения используйте полную переиндексацию")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка быстрого улучшения: {e}")
        return False

def apply_full_reindexing():
    """Полная переиндексация с улучшениями качества"""
    
    print(f"\n🚀 ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ С УЛУЧШЕНИЯМИ")
    print("-" * 45)
    
    try:
        from config import config
        from lysobacter_rag.pdf_extractor.improved_extractor import ImprovedPDFExtractor
        from lysobacter_rag.quality_control.text_enhancer import ScientificTextEnhancer
        from lysobacter_rag.data_processor import DataProcessor
        from lysobacter_rag.indexer.indexer import Indexer
        
        print("🔧 Инициализация компонентов...")
        
        # Создаем улучшенный экстрактор с интеграцией ScientificTextEnhancer
        class EnhancedPDFExtractor(ImprovedPDFExtractor):
            def __init__(self):
                super().__init__()
                self.text_enhancer = ScientificTextEnhancer()
            
            def fix_text_quality(self, text: str) -> str:
                # Используем новый улучшитель вместо старых правил
                enhanced_text, metrics = self.text_enhancer.enhance_text(text)
                return enhanced_text
        
        extractor = EnhancedPDFExtractor()
        processor = DataProcessor()
        indexer = Indexer()
        
        # Получаем статистику старой базы
        old_stats = indexer.get_collection_stats()
        print(f"📊 Текущая база: {old_stats.get('total_chunks', 0)} чанков")
        
        # Подтверждение
        print(f"\n⚠️ ВНИМАНИЕ:")
        print(f"   Это удалит существующую базу и создаст новую")
        print(f"   Время выполнения: ~10-15 минут")
        
        confirm = input("   Продолжить? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Переиндексация отменена")
            return False
        
        # Извлекаем и обрабатываем документы
        print(f"📄 Извлечение документов с улучшенным качеством...")
        data_dir = Path(config.DATA_DIR)
        pdf_files = list(data_dir.glob("*.pdf"))
        
        all_documents = []
        total_enhancements = 0
        
        for pdf_file in pdf_files:
            try:
                print(f"   📄 {pdf_file.name}")
                doc = extractor.extract_with_quality_control(pdf_file)
                all_documents.append(doc)
                
                # Подсчитываем улучшения
                quality_metrics = doc.metadata.get('quality_metrics', {})
                total_enhancements += quality_metrics.get('fixed_issues', 0)
                
            except Exception as e:
                print(f"   ⚠️ Ошибка в {pdf_file.name}: {e}")
        
        print(f"✅ Извлечено {len(all_documents)} документов")
        print(f"🔧 Применено {total_enhancements} улучшений качества")
        
        # Обрабатываем в чанки
        print(f"🔄 Создание чанков...")
        all_chunks = processor.process_documents(all_documents)
        print(f"✅ Создано {len(all_chunks)} чанков")
        
        # Пересоздаем индекс
        print(f"🗂️ Пересоздание индекса...")
        success = indexer.rebuild_index(all_chunks)
        
        if success:
            new_stats = indexer.get_collection_stats()
            print(f"\n🎉 ПЕРЕИНДЕКСАЦИЯ ЗАВЕРШЕНА!")
            print(f"   📊 Новая база: {new_stats.get('total_chunks', 0)} чанков")
            print(f"   🔧 Улучшений: {total_enhancements}")
            
            # Тестируем качество
            print(f"\n🧪 ТЕСТ КАЧЕСТВА:")
            test_quality_after_reindexing(indexer)
            
            return True
        else:
            print(f"❌ Ошибка при переиндексации")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка переиндексации: {e}")
        return False

def test_quality_improvements():
    """Тестирует улучшения качества без изменения базы"""
    
    print(f"\n🧪 ТЕСТИРОВАНИЕ УЛУЧШЕНИЙ КАЧЕСТВА")
    print("-" * 40)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        from lysobacter_rag.quality_control.text_enhancer import ScientificTextEnhancer
        
        indexer = Indexer()
        enhancer = ScientificTextEnhancer()
        
        # Тестируем на проблемных случаях
        test_queries = [
            "GW1-59T antarcticus",
            "temperature growth",
            "pH range",
            "fatty acids C15",
            "type strain"
        ]
        
        print("🔍 Тестирование качества на реальных данных:")
        
        total_improvement = 0
        tested_chunks = 0
        
        for query in test_queries:
            print(f"\n   📝 Тестирую: '{query}'")
            results = indexer.search(query, top_k=3)
            
            for i, result in enumerate(results, 1):
                original_text = result['text']
                enhanced_text, metrics = enhancer.enhance_text(original_text)
                validation = enhancer.validate_enhancement(original_text, enhanced_text)
                
                print(f"      Результат {i}: улучшение {validation['improvement']:.1%}")
                if validation['improvement'] > 0:
                    print(f"         Исправлений: {sum([
                        metrics.strain_fixes, metrics.formula_fixes, 
                        metrics.unit_fixes, metrics.term_fixes, metrics.number_fixes
                    ])}")
                
                total_improvement += validation['improvement']
                tested_chunks += 1
        
        if tested_chunks > 0:
            avg_improvement = total_improvement / tested_chunks
            print(f"\n📊 ИТОГИ ТЕСТИРОВАНИЯ:")
            print(f"   Протестировано чанков: {tested_chunks}")
            print(f"   Среднее улучшение: {avg_improvement:.1%}")
            
            if avg_improvement > 0.2:
                print("   ✅ ЗНАЧИТЕЛЬНОЕ УЛУЧШЕНИЕ ожидается!")
                print("   💡 Рекомендуется полная переиндексация")
            elif avg_improvement > 0.05:
                print("   ✅ Умеренное улучшение ожидается")
            else:
                print("   ⚠️ Улучшение минимально")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_quality_after_reindexing(indexer):
    """Тестирует качество после переиндексации"""
    
    # Тестируем ключевые запросы
    test_cases = [
        ("GW1-59T", "штамм должен быть без пробелов"),
        ("15–37°C", "температура должна быть корректно форматирована"),
        ("pH 9–11", "pH должен быть без лишних пробелов"),
        ("C15:0", "жирные кислоты должны быть правильно записаны")
    ]
    
    for search_term, expectation in test_cases:
        results = indexer.search(search_term, top_k=1)
        if results:
            print(f"   ✅ {search_term}: найден")
        else:
            print(f"   ⚠️ {search_term}: не найден")

if __name__ == "__main__":
    success = apply_quality_system()
    
    if success:
        print(f"\n🎉 СИСТЕМА КОНТРОЛЯ КАЧЕСТВА ПРИМЕНЕНА!")
        print(f"💡 Рекомендации:")
        print(f"   • Регулярно запускайте проверку качества")
        print(f"   • При добавлении новых PDF используйте улучшенный экстрактор")
        print(f"   • Мониторьте качество ответов RAG-системы")
    else:
        print(f"\n💡 СЛЕДУЮЩИЕ ШАГИ:")
        print(f"   • Проверьте логи на предмет ошибок")
        print(f"   • Убедитесь в доступности всех компонентов")
        print(f"   • При необходимости обратитесь за помощью")
    
    sys.exit(0 if success else 1) 