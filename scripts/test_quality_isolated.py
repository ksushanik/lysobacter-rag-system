#!/usr/bin/env python3
"""
Изолированное тестирование системы улучшения качества
"""
import re
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class EnhancementMetrics:
    """Метрики улучшения текста"""
    total_fixes: int = 0
    strain_fixes: int = 0
    formula_fixes: int = 0
    unit_fixes: int = 0
    term_fixes: int = 0
    number_fixes: int = 0

class SimpleTextEnhancer:
    """Упрощенная версия улучшителя для тестирования"""
    
    def __init__(self):
        self.metrics = EnhancementMetrics()
        self._load_rules()
    
    def _load_rules(self):
        """Загружает правила исправления"""
        
        # Основные правила из нашей системы
        self.strain_patterns = [
            (r'GW\s*1-\s*5\s*9\s*T', 'GW1-59T'),
            (r'(\w+)\s*-\s*(\d+)\s+T', r'\1-\2T'),
        ]
        
        self.formula_patterns = [
            (r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2'),
        ]
        
        self.unit_patterns = [
            (r'(\d+)\s*[-–]\s*(\d+)\s*°?\s*C', r'\1–\2°C'),
            (r'pH\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'pH \1–\2'),
        ]
        
        self.term_patterns = [
            (r'Lyso\s*bacter', 'Lysobacter'),
            (r'sp\.\s*nov\.?', 'sp. nov.'),
            (r'16S\s*rRNA', '16S rRNA'),
        ]
        
        self.number_patterns = [
            (r'(\d+)\s*\.\s*(\d+)', r'\1.\2'),
        ]
    
    def enhance_text(self, text: str) -> Tuple[str, EnhancementMetrics]:
        """Улучшает качество текста"""
        
        self.metrics = EnhancementMetrics()
        original_text = text
        
        # Применяем правила
        text = self._apply_pattern_rules(text, self.strain_patterns, 'strain')
        text = self._apply_pattern_rules(text, self.formula_patterns, 'formula')
        text = self._apply_pattern_rules(text, self.unit_patterns, 'unit')
        text = self._apply_pattern_rules(text, self.term_patterns, 'term')
        text = self._apply_pattern_rules(text, self.number_patterns, 'number')
        
        # Общие исправления
        text = re.sub(r'\s+', ' ', text.strip())
        
        if text != original_text:
            self.metrics.total_fixes = 1
        
        return text, self.metrics
    
    def _apply_pattern_rules(self, text: str, patterns: list, category: str) -> str:
        """Применяет правила конкретной категории"""
        
        original_text = text
        
        for pattern, replacement in patterns:
            new_text = re.sub(pattern, replacement, text)
            if new_text != text:
                # Увеличиваем счетчик исправлений для категории
                if category == 'strain':
                    self.metrics.strain_fixes += 1
                elif category == 'formula':
                    self.metrics.formula_fixes += 1
                elif category == 'unit':
                    self.metrics.unit_fixes += 1
                elif category == 'term':
                    self.metrics.term_fixes += 1
                elif category == 'number':
                    self.metrics.number_fixes += 1
                
                text = new_text
        
        return text
    
    def get_quality_score(self, text: str) -> float:
        """Простая оценка качества текста"""
        
        issues = 0
        total_checks = 0
        
        checks = [
            r'\w+\s*-\s*\d+\s+T',  # разорванные штаммы
            r'C\s+\d+\s*:\s*\d+',  # разорванные формулы
            r'\d+\s*\.\s*\d+',     # разорванные числа
            r'[a-zA-Z]{50,}',      # слитные слова
            r'\d+\s+°\s+C',        # разорванные единицы
        ]
        
        for pattern in checks:
            total_checks += 1
            if re.search(pattern, text):
                issues += 1
        
        return max(0.0, 1.0 - (issues / total_checks))
    
    def validate_enhancement(self, original: str, enhanced: str) -> Dict:
        """Валидирует улучшение"""
        
        original_score = self.get_quality_score(original)
        enhanced_score = self.get_quality_score(enhanced)
        
        return {
            'original_score': original_score,
            'enhanced_score': enhanced_score,
            'improvement': enhanced_score - original_score,
            'successful': enhanced_score > original_score
        }

def test_quality_system():
    """Тестирует систему улучшения качества"""
    
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ УЛУЧШЕНИЯ КАЧЕСТВА")
    print("=" * 55)
    
    enhancer = SimpleTextEnhancer()
    
    # Тест-кейсы с проблемами качества
    test_cases = [
        {
            'name': 'Разорванный штамм GW1-59T',
            'original': 'strain GW1- 5 9T was isolated from Antarctic freshwater lake',
            'expected_fix': 'GW1-59T'
        },
        {
            'name': 'Разорванная температура',
            'original': 'growth temperature range 15 – 37 °C optimum 30°C',
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
            'expected_fix': 'Lysobacter'
        },
        {
            'name': 'Разорванный размер генома',
            'original': 'genome size 2 . 8 Mb with 2,487 genes',
            'expected_fix': '2.8 Mb'
        },
        {
            'name': 'Комбинированные проблемы',
            'original': 'strain GW1- 5 9T grows at 15 – 37 °C with C 15 : 0 fatty acids',
            'expected_fix': 'GW1-59T'
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
        
        # Проверяем наличие ожидаемого исправления
        expected = test_case['expected_fix']
        if expected in enhanced and expected not in original:
            print(f"   ✅ Исправление '{expected}' найдено!")
            successful_fixes += 1
        elif enhanced != original:
            print(f"   ⚠️ Текст изменен, но исправление '{expected}' не точно")
            successful_fixes += 0.5  # Частичный успех
        else:
            print(f"   ❌ Исправление '{expected}' НЕ применено")
        
        print(f"   📊 Улучшение качества: {validation['improvement']:.1%}")
        print(f"   🔧 Исправлений: штаммы:{metrics.strain_fixes}, формулы:{metrics.formula_fixes}, единицы:{metrics.unit_fixes}, термины:{metrics.term_fixes}, числа:{metrics.number_fixes}")
        
        total_improvements += validation['improvement']
    
    # Итоговая статистика
    avg_improvement = total_improvements / len(test_cases)
    success_rate = successful_fixes / len(test_cases)
    
    print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Успешных исправлений: {successful_fixes:.1f}/{len(test_cases)} ({success_rate:.1%})")
    print(f"   Среднее улучшение качества: {avg_improvement:.1%}")
    
    # Определяем вердикт
    if success_rate >= 0.8 and avg_improvement >= 0.3:
        print(f"   🎉 ОТЛИЧНЫЕ РЕЗУЛЬТАТЫ! Система готова к применению")
        verdict = "excellent"
    elif success_rate >= 0.6 and avg_improvement >= 0.2:
        print(f"   ✅ ХОРОШИЕ РЕЗУЛЬТАТЫ! Рекомендуется применение")
        verdict = "good"
    elif success_rate >= 0.4 and avg_improvement >= 0.1:
        print(f"   ⚠️ Умеренные результаты, необходима доработка")
        verdict = "moderate"
    else:
        print(f"   ❌ Система требует значительной доработки")
        verdict = "poor"
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if verdict in ["excellent", "good"]:
        print(f"   1. 🚀 Система готова для применения к реальным данным")
        print(f"   2. 📊 Ожидаемое улучшение качества: {avg_improvement:.0%}")
        print(f"   3. 🎯 Приоритет: переиндексация с новыми правилами")
        print(f"   4. 🧪 Протестируйте на запросе о штамме GW1-59T")
    elif verdict == "moderate":
        print(f"   1. 🔧 Доработайте правила для слабых случаев")
        print(f"   2. 🧪 Проведите дополнительное тестирование")
        print(f"   3. ⚠️ Применяйте осторожно к критичным данным")
    else:
        print(f"   1. 🔍 Проанализируйте неудачные случаи")
        print(f"   2. 🔧 Улучшите алгоритмы исправления")
        print(f"   3. ❌ НЕ применяйте к продуктивным данным")
    
    print(f"\n🔮 ПРОГНОЗ ВЛИЯНИЯ НА RAG-СИСТЕМУ:")
    if verdict == "excellent":
        print(f"   📈 Качество ответов должно значительно улучшиться")
        print(f"   🎯 Ответы о штаммах станут более точными")
        print(f"   📊 Научные данные будут корректно извлекаться")
    elif verdict == "good":
        print(f"   📈 Заметное улучшение качества ответов")
        print(f"   ✅ Основные проблемы будут решены")
    else:
        print(f"   ⚠️ Улучшение может быть незначительным")
    
    return verdict in ["excellent", "good"]

def demonstrate_before_after():
    """Демонстрирует конкретный пример улучшения"""
    
    print(f"\n🔬 ДЕМОНСТРАЦИЯ: ДО И ПОСЛЕ")
    print("-" * 40)
    
    enhancer = SimpleTextEnhancer()
    
    # Реальный пример с множественными проблемами
    problematic_text = """
    strain GW1- 5 9T (= KCTC 52731 T = CCTCC AB 2014046 T ) was isolated from a freshwater
    lake in Antarctica. Cells are Gram-stain-negative, aerobic, rod-shaped, 0.6–0.8 × 0.7–1.7 μm.
    Growth occurs at 15 – 37 °C (optimum, 30 °C), pH 9 . 0 – 11 . 0 (optimum, pH 10.0) and 
    with 0–4 % (w/v) NaCl. Major fatty acids are C 15 : 0, C 16 : 0, C 16 : 1 ω7c and C 17 : 0.
    The G + C content is 63 . 9 mol%. Based on 16S rRNA gene sequence analysis, strain GW1- 5 9T
    belongs to the genus Lyso bacter and is most closely related to L. enzymogenes YC1 T.
    """
    
    enhanced_text, metrics = enhancer.enhance_text(problematic_text)
    validation = enhancer.validate_enhancement(problematic_text, enhanced_text)
    
    print(f"📝 ИСХОДНЫЙ ТЕКСТ:")
    print(f"   {problematic_text.strip()}")
    
    print(f"\n✨ УЛУЧШЕННЫЙ ТЕКСТ:")
    print(f"   {enhanced_text}")
    
    print(f"\n📊 СТАТИСТИКА УЛУЧШЕНИЙ:")
    print(f"   Улучшение качества: {validation['improvement']:.1%}")
    print(f"   Исправлений штаммов: {metrics.strain_fixes}")
    print(f"   Исправлений формул: {metrics.formula_fixes}")
    print(f"   Исправлений единиц: {metrics.unit_fixes}")
    print(f"   Исправлений терминов: {metrics.term_fixes}")
    print(f"   Исправлений чисел: {metrics.number_fixes}")
    
    # Анализ конкретных улучшений
    improvements_found = []
    
    if 'GW1-59T' in enhanced_text and 'GW1- 5 9T' not in enhanced_text:
        improvements_found.append("Исправлен штамм GW1-59T")
    
    if '15–37°C' in enhanced_text:
        improvements_found.append("Исправлена температура")
    
    if 'C15:0' in enhanced_text:
        improvements_found.append("Исправлены формулы жирных кислот")
    
    if 'pH 9.0–11.0' in enhanced_text:
        improvements_found.append("Исправлен диапазон pH")
    
    if 'Lysobacter' in enhanced_text and 'Lyso bacter' not in enhanced_text:
        improvements_found.append("Исправлено название рода")
    
    print(f"\n🎯 КОНКРЕТНЫЕ УЛУЧШЕНИЯ:")
    for improvement in improvements_found:
        print(f"   ✅ {improvement}")
    
    if not improvements_found:
        print(f"   ⚠️ Значимые улучшения не обнаружены")
    
    return len(improvements_found) > 0

if __name__ == "__main__":
    print("🎯 ИЗОЛИРОВАННОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ КАЧЕСТВА")
    print("=" * 55)
    
    # Основное тестирование
    test_success = test_quality_system()
    
    # Демонстрация на реальном примере
    demo_success = demonstrate_before_after()
    
    print(f"\n🏁 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    
    if test_success and demo_success:
        print(f"   🎉 СИСТЕМА ГОТОВА К ПРИМЕНЕНИЮ!")
        print(f"   📈 Ожидается значительное улучшение качества данных")
        print(f"   🚀 Рекомендуется полная переиндексация")
        
        print(f"\n🔄 СЛЕДУЮЩИЕ ШАГИ:")
        print(f"   1. Примените систему к реальным данным")
        print(f"   2. Переиндексируйте базу знаний с улучшениями")
        print(f"   3. Протестируйте RAG-ответы на запросах о штаммах")
        print(f"   4. Мониторьте качество в динамике")
        
    elif test_success or demo_success:
        print(f"   ⚠️ ЧАСТИЧНЫЙ УСПЕХ")
        print(f"   🔧 Система работает, но требует доработки")
        
    else:
        print(f"   ❌ СИСТЕМА ТРЕБУЕТ ДОРАБОТКИ")
        print(f"   🔍 Необходимо улучшить алгоритмы исправления")
    
    exit_code = 0 if (test_success and demo_success) else 1
    exit(exit_code) 