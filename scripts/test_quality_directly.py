#!/usr/bin/env python3
"""
Прямое тестирование системы улучшения качества
"""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_quality_enhancements():
    """Тестирует улучшения качества на конкретных примерах"""
    
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ УЛУЧШЕНИЯ КАЧЕСТВА")
    print("=" * 55)
    
    try:
        from lysobacter_rag.quality_control.text_enhancer import ScientificTextEnhancer
        
        enhancer = ScientificTextEnhancer()
        
        # Примеры с проблемами качества (из диагностики)
        test_cases = [
            {
                'name': 'Разорванный штамм GW1-59T',
                'original': 'strain GW1- 5 9T was isolated from Antarctic freshwater lake',
                'expected_fix': 'GW1-59T'
            },
            {
                'name': 'Разорванная температура',
                'original': 'growth temperature range 15 – 37 °C optimum 30 °C',
                'expected_fix': '15–37°C'
            },
            {
                'name': 'Разорванная химическая формула',
                'original': 'major fatty acids C 15 : 0 and C 16 : 0',
                'expected_fix': 'C15:0'
            },
            {
                'name': 'Разорванный pH',
                'original': 'pH range for growth 9 . 0 – 11 . 0',
                'expected_fix': 'pH 9.0–11.0'
            },
            {
                'name': 'Разорванное название вида',
                'original': 'Lyso bacter antarcticus sp . nov .',
                'expected_fix': 'Lysobacter antarcticus sp. nov.'
            },
            {
                'name': 'Разорванный размер генома',
                'original': 'genome size 2 . 8 Mb with 2,487 genes',
                'expected_fix': '2.8 Mb'
            },
            {
                'name': 'Слитные научные термины',
                'original': 'analysisusing16SrRNAsequencesandDNA-DNAhybridization',
                'expected_fix': '16S rRNA sequences'
            }
        ]
        
        print(f"📊 ТЕСТИРОВАНИЕ {len(test_cases)} СЛУЧАЕВ:")
        
        total_improvements = 0
        successful_fixes = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}:")
            
            original = test_case['original']
            enhanced, metrics = enhancer.enhance_text(original)
            validation = enhancer.validate_enhancement(original, enhanced)
            
            print(f"   До:     {original}")
            print(f"   После:  {enhanced}")
            
            # Проверяем, содержит ли результат ожидаемое исправление
            expected = test_case['expected_fix']
            if expected in enhanced and expected not in original:
                print(f"   ✅ Исправление '{expected}' найдено!")
                successful_fixes += 1
            elif enhanced != original:
                print(f"   ⚠️ Текст изменен, но исправление '{expected}' не найдено")
            else:
                print(f"   ❌ Исправление '{expected}' НЕ применено")
            
            print(f"   📊 Улучшение качества: {validation['improvement']:.1%}")
            print(f"   🔧 Исправлений: штаммы:{metrics.strain_fixes}, формулы:{metrics.formula_fixes}, единицы:{metrics.unit_fixes}, термины:{metrics.term_fixes}, числа:{metrics.number_fixes}")
            
            total_improvements += validation['improvement']
        
        # Итоговая статистика
        avg_improvement = total_improvements / len(test_cases)
        success_rate = successful_fixes / len(test_cases)
        
        print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   Успешных исправлений: {successful_fixes}/{len(test_cases)} ({success_rate:.1%})")
        print(f"   Среднее улучшение качества: {avg_improvement:.1%}")
        
        if success_rate >= 0.8 and avg_improvement >= 0.3:
            print(f"   🎉 ОТЛИЧНЫЕ РЕЗУЛЬТАТЫ! Система готова к применению")
            quality_verdict = "excellent"
        elif success_rate >= 0.6 and avg_improvement >= 0.2:
            print(f"   ✅ ХОРОШИЕ РЕЗУЛЬТАТЫ! Рекомендуется применение")
            quality_verdict = "good"
        elif success_rate >= 0.4 and avg_improvement >= 0.1:
            print(f"   ⚠️ Умеренные результаты, необходима доработка")
            quality_verdict = "moderate"
        else:
            print(f"   ❌ Система требует значительной доработки")
            quality_verdict = "poor"
        
        # Рекомендации по применению
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if quality_verdict in ["excellent", "good"]:
            print(f"   1. 🚀 Запустите полную переиндексацию: make full-quality-reindex")
            print(f"   2. 📊 Проверьте результаты: make check-overall-quality")
            print(f"   3. 🧪 Протестируйте на запросе о GW1-59T")
        elif quality_verdict == "moderate":
            print(f"   1. 🔧 Доработайте правила для слабых случаев")
            print(f"   2. 🧪 Проведите выборочное тестирование")
            print(f"   3. ⚠️ Применяйте с осторожностью")
        else:
            print(f"   1. 🔍 Проанализируйте неудачные случаи")
            print(f"   2. 🔧 Улучшите алгоритмы исправления")
            print(f"   3. ❌ НЕ применяйте к продуктивным данным")
        
        return quality_verdict in ["excellent", "good"]
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_real_world_usage():
    """Демонстрирует применение на реальных данных"""
    
    print(f"\n🔬 ДЕМОНСТРАЦИЯ НА РЕАЛЬНЫХ ДАННЫХ")
    print("-" * 40)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        from lysobacter_rag.quality_control.text_enhancer import ScientificTextEnhancer
        
        indexer = Indexer()
        enhancer = ScientificTextEnhancer()
        
        # Ищем проблемные данные
        problem_queries = [
            "GW1-5 9T",  # Разорванный штамм
            "C 15 : 0",  # Разорванная формула
            "pH 9 . 0"   # Разорванное значение pH
        ]
        
        found_problems = False
        
        for query in problem_queries:
            print(f"\n🔍 Поиск: '{query}'")
            results = indexer.search(query, top_k=2)
            
            if results:
                found_problems = True
                print(f"   Найдено {len(results)} результатов с проблемами")
                
                for i, result in enumerate(results, 1):
                    original_text = result['text'][:200] + "..."
                    enhanced_text, metrics = enhancer.enhance_text(result['text'])
                    enhanced_preview = enhanced_text[:200] + "..."
                    
                    validation = enhancer.validate_enhancement(result['text'], enhanced_text)
                    
                    print(f"\n   Результат {i}:")
                    print(f"      До:     {original_text}")
                    print(f"      После:  {enhanced_preview}")
                    print(f"      Улучшение: {validation['improvement']:.1%}")
            else:
                print(f"   ✅ Проблем не найдено")
        
        if not found_problems:
            print(f"\n🎉 В базе данных не найдено явных проблем качества!")
            print(f"   Возможно, данные уже были улучшены ранее")
        else:
            print(f"\n⚠️ Обнаружены проблемы качества в реальных данных")
            print(f"   Рекомендуется применить систему улучшения")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации: {e}")
        return False

if __name__ == "__main__":
    print("🎯 СИСТЕМА КОНТРОЛЯ КАЧЕСТВА - ПРЯМОЕ ТЕСТИРОВАНИЕ")
    print("=" * 60)
    
    # Тестируем улучшения
    test_success = test_quality_enhancements()
    
    if test_success:
        # Демонстрируем на реальных данных
        demo_success = demonstrate_real_world_usage()
        
        if demo_success:
            print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print(f"\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
            print(f"   1. Примените улучшения: make apply-quality-system")
            print(f"   2. Запустите мониторинг: make monitor-quality")
            print(f"   3. Протестируйте запросы о штаммах")
    else:
        print(f"\n❌ ТЕСТИРОВАНИЕ ВЫЯВИЛО ПРОБЛЕМЫ")
        print(f"   Система требует доработки перед применением")
    
    sys.exit(0 if test_success else 1) 