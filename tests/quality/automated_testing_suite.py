#!/usr/bin/env python3
"""
Автоматическая система тестирования для отслеживания прогресса итераций
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import traceback
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

import sys
import os
# Добавляем пути для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from tests.quality.baseline_metrics import MetricsTracker, create_test_iteration_metrics
from src.lysobacter_rag.rag_pipeline import RAGPipeline
from src.lysobacter_rag.rag_pipeline.structured_strain_analyzer import StructuredStrainAnalyzer

@dataclass
class TestCase:
    """Тестовый случай для проверки системы"""
    strain: str
    question: str
    expected_categories: List[str]
    min_score: float
    critical: bool = False  # Критичный ли тест для прохождения итерации

class AutomatedTestSuite:
    """Автоматическая система тестирования"""
    
    def __init__(self):
        self.rag_system = None
        self.metrics_tracker = MetricsTracker()
        
        # Основные тестовые случаи
        self.test_cases = [
            TestCase(
                strain="YC5194",
                question="Какие характеристики штамма Lysobacter capsici YC5194?",
                expected_categories=["classification", "origin", "morphology", "growth_conditions", "biological_activity"],
                min_score=50.0,
                critical=True
            ),
            TestCase(
                strain="GW1-59T",
                question="Что известно о штамме GW1-59T?",
                expected_categories=["classification", "origin", "morphology", "growth_conditions"],
                min_score=50.0,
                critical=True
            ),
            TestCase(
                strain="YC5194",
                question="Какова морфология штамма YC5194?",
                expected_categories=["morphology"],
                min_score=30.0,
                critical=False
            ),
            TestCase(
                strain="GW1-59T",
                question="В каких условиях растет штамм GW1-59T?",
                expected_categories=["growth_conditions"],
                min_score=30.0,
                critical=False
            )
        ]
    
    def initialize_rag_system(self) -> bool:
        """Инициализирует RAG систему"""
        try:
            print("🔄 Инициализация RAG системы...")
            self.rag_system = RAGPipeline()
            self.strain_analyzer = StructuredStrainAnalyzer()
            print("✅ RAG система инициализирована")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации RAG системы: {e}")
            print(traceback.format_exc())
            return False
    
    def run_single_test(self, test_case: TestCase) -> Dict[str, Any]:
        """Выполняет один тестовый случай"""
        print(f"🧪 Тестирование {test_case.strain}: {test_case.question[:50]}...")
        
        start_time = time.time()
        
        try:
            response = self.rag_system.ask_question(test_case.question)
            response_time = (time.time() - start_time) * 1000  # в миллисекундах
            
            # Анализируем структурированный ответ
            # Извлекаем имя штамма из вопроса
            strain_name = self._extract_strain_name(test_case.question)
            strain_analysis = self.strain_analyzer.analyze_strain_from_context(
                response.get('answer', ''), strain_name
            )
            
            # Подсчитываем заполненные категории
            categories_filled = self._count_filled_categories(strain_analysis)
            
            return {
                "success": True,
                "response": response,
                "strain_analysis": strain_analysis,
                "response_time_ms": response_time,
                "categories_filled": categories_filled,
                "structure_confidence": strain_analysis.confidence_score,
                "strain_characteristics": {
                    "classification": strain_analysis.classification,
                    "origin": strain_analysis.origin,
                    "morphology": strain_analysis.morphology,
                    "growth_conditions": strain_analysis.growth_conditions,
                    "biochemistry": strain_analysis.biochemical_properties,
                    "chemotaxonomy": strain_analysis.chemotaxonomy,
                    "genomics": strain_analysis.genomics,
                    "biological_activity": strain_analysis.biological_activity
                }
            }
            
        except Exception as e:
            print(f"❌ Ошибка в тесте {test_case.strain}: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }
    
    def run_full_test_suite(self, iteration_name: str) -> Dict[str, Any]:
        """Выполняет полный набор тестов"""
        print(f"\n🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ: {iteration_name}")
        print("=" * 70)
        
        if not self.initialize_rag_system():
            return {"error": "Не удалось инициализировать RAG систему"}
        
        test_results = {}
        total_time = 0
        critical_failures = 0
        
        for test_case in self.test_cases:
            result = self.run_single_test(test_case)
            test_results[f"{test_case.strain}_{len(test_results)}"] = result
            
            if result.get("success"):
                score = self.calculate_test_score(result, test_case)
                print(f"   📊 Балл: {score:.1f} (минимум: {test_case.min_score})")
                
                if score < test_case.min_score and test_case.critical:
                    critical_failures += 1
                    print(f"   ⚠️ КРИТИЧЕСКИЙ ПРОВАЛ: {score:.1f} < {test_case.min_score}")
                
                total_time += result.get("response_time_ms", 0)
            else:
                print(f"   ❌ ОШИБКА: {result.get('error', 'Неизвестная ошибка')}")
                if test_case.critical:
                    critical_failures += 1
        
        # Создаем метрики итерации
        iteration_metrics = create_test_iteration_metrics(iteration_name, test_results)
        iteration_metrics.response_time_ms = total_time / len(self.test_cases)
        
        # Проверяем регрессии
        regression_count = self.check_for_regressions(test_results)
        iteration_metrics.regression_count = regression_count
        
        # Определяем статус итерации
        success = critical_failures == 0 and self.meets_iteration_threshold(iteration_metrics)
        
        test_summary = {
            "iteration_name": iteration_name,
            "success": success,
            "critical_failures": critical_failures,
            "total_tests": len(self.test_cases),
            "metrics": iteration_metrics,
            "results": test_results
        }
        
        self.print_test_summary(test_summary)
        
        # Сохраняем результаты
        self.metrics_tracker.add_iteration_result(iteration_metrics)
        
        return test_summary
    
    def calculate_test_score(self, result: Dict[str, Any], test_case: TestCase) -> float:
        """Рассчитывает балл за тест"""
        if not result.get("success"):
            return 0.0
        
        categories_filled = result.get("categories_filled", 0)
        confidence_score = result.get("structure_confidence", 0)
        
        # Базовый балл: покрытие категорий + уверенность
        categories_score = (categories_filled / 8) * 100
        confidence_score_percent = confidence_score * 100
        
        return (categories_score + confidence_score_percent) / 2
    
    def check_for_regressions(self, current_results: Dict[str, Any]) -> int:
        """Проверяет на регрессии относительно базовой линии"""
        regressions = 0
        baseline = self.metrics_tracker.baseline
        
        # Простая проверка: если текущий результат значительно хуже базового
        for strain in ["YC5194", "GW1-59T"]:
            baseline_score = baseline.strain_scores.get(strain, 0)
            
            # Находим текущий результат для штамма
            current_score = 0
            for key, result in current_results.items():
                if strain in key and result.get("success"):
                    current_score = self.calculate_test_score(result, self.test_cases[0])
                    break
            
            if current_score > 0 and current_score < baseline_score - 10:  # Регрессия >10 баллов
                regressions += 1
                print(f"⚠️ РЕГРЕССИЯ для {strain}: {baseline_score:.1f} → {current_score:.1f}")
        
        return regressions
    
    def meets_iteration_threshold(self, metrics) -> bool:
        """Проверяет, достигает ли итерация целевого порога"""
        thresholds = {
            "Итерация 1": 50,
            "Итерация 2": 65,
            "Итерация 3": 75
        }
        
        threshold = thresholds.get(metrics.iteration_name, 50)
        return metrics.overall_score >= threshold
    
    def print_test_summary(self, summary: Dict[str, Any]):
        """Выводит сводку тестирования"""
        print(f"\n📋 СВОДКА ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        metrics = summary["metrics"]
        
        # Общий статус
        if summary["success"]:
            print("🎉 ИТЕРАЦИЯ УСПЕШНА!")
            print("✅ Все критические тесты пройдены")
            print("🚀 Готово к внедрению")
        else:
            print("❌ ИТЕРАЦИЯ НЕ ПРОШЛА")
            print(f"⚠️ Критических провалов: {summary['critical_failures']}")
            print("🔧 Требуется доработка")
        
        print(f"\n📊 Детальные метрики:")
        print(f"   Общий балл: {metrics.overall_score:.1f}")
        print(f"   Время ответа: {metrics.response_time_ms:.0f}мс")
        print(f"   Регрессий: {metrics.regression_count}")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        if summary["success"]:
            print("   • Можно внедрять в production")
            print("   • Переходить к следующей итерации")
        else:
            if summary["critical_failures"] > 0:
                print("   • Исправить критические ошибки")
                print("   • Повторить тестирование")
            if metrics.regression_count > 0:
                print("   • Устранить регрессии")
                print("   • Проверить совместимость изменений")
    
    def _extract_strain_name(self, question: str) -> str:
        """Извлекает имя штамма из вопроса"""
        # Ищем паттерны типа YC5194, GW1-59T и т.д.
        patterns = [
            r'(YC\d+)',
            r'(GW\d+-\d+T?)',
            r'([A-Z]+\d+[-_]?\d*T?)',
            r'(штамм[ае]?\s+([A-Z][A-Za-z0-9\-_]+))',
            r'(strain\s+([A-Z][A-Za-z0-9\-_]+))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                # Возвращаем найденное имя штамма
                groups = match.groups()
                return groups[1] if len(groups) > 1 else groups[0]
        
        # Если не найдено, возвращаем общее имя
        return "Unknown"
    
    def _count_filled_categories(self, characteristics: 'StrainCharacteristics') -> int:
        """Подсчитывает количество заполненных категорий"""
        categories = [
            characteristics.classification,
            characteristics.origin,
            characteristics.morphology,
            characteristics.growth_conditions,
            characteristics.biochemical_properties,
            characteristics.chemotaxonomy,
            characteristics.genomics,
            characteristics.biological_activity
        ]
        
        filled_count = 0
        for category in categories:
            if category and any(category.values()):  # Если есть хотя бы одно значение
                filled_count += 1
        
        return filled_count

def run_iteration_test(iteration_name: str = "Итерация 1"):
    """Запускает тестирование конкретной итерации"""
    suite = AutomatedTestSuite()
    return suite.run_full_test_suite(iteration_name)

if __name__ == "__main__":
    # Запуск базового тестирования
    import argparse
    
    parser = argparse.ArgumentParser(description="Автоматическое тестирование RAG системы")
    parser.add_argument("--iteration", default="Итерация 1", help="Название итерации")
    
    args = parser.parse_args()
    
    print("🧪 АВТОМАТИЧЕСКАЯ СИСТЕМА ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    result = run_iteration_test(args.iteration)
    
    if result.get("success"):
        print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        exit(0)
    else:
        print("\n❌ ТЕСТИРОВАНИЕ НЕ ПРОЙДЕНО")
        exit(1) 