#!/usr/bin/env python3
"""
Базовые метрики для отслеживания прогресса улучшений системы
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class IterationMetrics:
    """Метрики для одной итерации разработки"""
    iteration_name: str
    date: str
    overall_score: float
    strain_scores: Dict[str, float]
    coverage_scores: Dict[str, float]  # По категориям
    confidence_scores: Dict[str, float]
    accuracy_scores: Dict[str, float]
    response_time_ms: float
    regression_count: int
    notes: str

@dataclass
class BaselineMetrics:
    """Базовые метрики до начала улучшений"""
    date: str = "2025-06-08"
    overall_score: float = 32.0
    
    strain_scores: Dict[str, float] = None
    coverage_by_category: Dict[str, float] = None
    response_times: Dict[str, float] = None
    
    def __post_init__(self):
        if self.strain_scores is None:
            self.strain_scores = {
                "YC5194": 31.2,  # 50% покрытие + 12.5% уверенность
                "GW1-59T": 32.5  # 50% покрытие + 15% уверенность
            }
        
        if self.coverage_by_category is None:
            self.coverage_by_category = {
                "classification": 50.0,  # 2/4 категории работают
                "origin": 37.5,         # 1.5/4 в среднем
                "morphology": 0.0,      # Не работает
                "growth_conditions": 0.0,  # Не работает
                "biochemistry": 0.0,    # Не работает
                "chemotaxonomy": 25.0,  # Частично работает
                "genomics": 0.0,        # Не работает
                "biological_activity": 25.0  # Частично работает
            }
        
        if self.response_times is None:
            self.response_times = {
                "search_time": 2500,    # мс
                "analysis_time": 1200,  # мс
                "total_time": 3700      # мс
            }

class MetricsTracker:
    """Система отслеживания метрик улучшений"""
    
    def __init__(self, metrics_file: str = "tests/quality/metrics_history.json"):
        self.metrics_file = metrics_file
        self.baseline = BaselineMetrics()
        self.history: List[IterationMetrics] = []
        self.load_history()
    
    def load_history(self):
        """Загружает историю метрик"""
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = [IterationMetrics(**item) for item in data.get('history', [])]
        except FileNotFoundError:
            self.history = []
    
    def save_history(self):
        """Сохраняет историю метрик"""
        data = {
            'baseline': asdict(self.baseline),
            'history': [asdict(metrics) for metrics in self.history]
        }
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_iteration_result(self, metrics: IterationMetrics):
        """Добавляет результат итерации"""
        self.history.append(metrics)
        self.save_history()
        self.print_iteration_summary(metrics)
    
    def print_iteration_summary(self, metrics: IterationMetrics):
        """Выводит сводку по итерации"""
        baseline_score = self.baseline.overall_score
        improvement = metrics.overall_score - baseline_score
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ИТЕРАЦИИ: {metrics.iteration_name}")
        print("=" * 60)
        print(f"📈 Общий балл: {baseline_score:.1f} → {metrics.overall_score:.1f} ({improvement:+.1f})")
        
        # Прогресс по штаммам
        print(f"\n🔬 Прогресс по штаммам:")
        for strain, score in metrics.strain_scores.items():
            baseline_strain = self.baseline.strain_scores.get(strain, 0)
            strain_improvement = score - baseline_strain
            print(f"   {strain}: {baseline_strain:.1f} → {score:.1f} ({strain_improvement:+.1f})")
        
        # Статус относительно цели
        print(f"\n🎯 Статус итерации:")
        target_scores = {
            "iteration_1": 50,
            "iteration_2": 65, 
            "iteration_3": 75,
            "production": 85
        }
        
        iteration_num = metrics.iteration_name.lower().replace("итерация ", "iteration_").replace(" ", "_")
        target = target_scores.get(iteration_num, 50)
        
        if metrics.overall_score >= target:
            print(f"   ✅ УСПЕХ! Достигнут целевой балл {target}")
            print(f"   🚀 Готово к внедрению в production")
        elif metrics.overall_score >= target - 5:
            print(f"   ⚠️ БЛИЗКО К ЦЕЛИ (цель: {target}, получено: {metrics.overall_score:.1f})")
            print(f"   🔧 Рекомендуется доработка")
        else:
            print(f"   ❌ ЦЕЛЬ НЕ ДОСТИГНУТА (цель: {target}, получено: {metrics.overall_score:.1f})")
            print(f"   🔄 Требуется пересмотр подхода")
        
        # Время ответа
        baseline_time = self.baseline.response_times['total_time']
        time_change = metrics.response_time_ms - baseline_time
        print(f"\n⏱️ Время ответа: {baseline_time}мс → {metrics.response_time_ms:.0f}мс ({time_change:+.0f}мс)")
        
        # Регрессии
        if metrics.regression_count > 0:
            print(f"\n⚠️ Обнаружено регрессий: {metrics.regression_count}")
        else:
            print(f"\n✅ Регрессий не обнаружено")
    
    def get_progress_report(self) -> str:
        """Генерирует отчет о прогрессе"""
        if not self.history:
            return "📊 История улучшений пуста"
        
        latest = self.history[-1]
        total_improvement = latest.overall_score - self.baseline.overall_score
        
        report = f"""
📊 ОТЧЕТ О ПРОГРЕССЕ СИСТЕМЫ

🎯 Цель: 85 баллов (уровень NotebookLM)
📈 Текущий прогресс: {self.baseline.overall_score} → {latest.overall_score:.1f} ({total_improvement:+.1f})
📅 Последнее обновление: {latest.date}

🔬 Лучшие результаты по штаммам:
"""
        
        for strain in ["YC5194", "GW1-59T"]:
            best_score = max([m.strain_scores.get(strain, 0) for m in self.history] + [self.baseline.strain_scores.get(strain, 0)])
            baseline_strain = self.baseline.strain_scores.get(strain, 0)
            improvement = best_score - baseline_strain
            report += f"   {strain}: {baseline_strain:.1f} → {best_score:.1f} ({improvement:+.1f})\n"
        
        # До цели осталось
        remaining = 85 - latest.overall_score
        report += f"\n🏁 До цели осталось: {remaining:.1f} баллов"
        
        return report

def create_test_iteration_metrics(iteration_name: str, test_results: Dict) -> IterationMetrics:
    """Создает метрики итерации из результатов тестирования"""
    
    # Рассчитываем общий балл
    strain_scores = {}
    total_score = 0
    
    for strain, result in test_results.items():
        if 'error' not in result:
            categories_percent = (result.get('categories_filled', 0) / 8) * 100
            confidence_percent = result.get('structure_confidence', 0) * 100
            strain_score = (categories_percent + confidence_percent) / 2
            strain_scores[strain] = strain_score
            total_score += strain_score
    
    overall_score = total_score / len(strain_scores) if strain_scores else 0
    
    # Анализ покрытия по категориям
    coverage_scores = {}
    categories = ["classification", "origin", "morphology", "growth_conditions", 
                 "biochemistry", "chemotaxonomy", "genomics", "biological_activity"]
    
    for category in categories:
        filled_count = 0
        total_strains = len([r for r in test_results.values() if 'error' not in r])
        
        for strain, result in test_results.items():
            if 'error' not in result:
                characteristics = result.get('strain_characteristics', {})
                if characteristics.get(category):
                    filled_count += 1
        
        coverage_scores[category] = (filled_count / total_strains * 100) if total_strains > 0 else 0
    
    return IterationMetrics(
        iteration_name=iteration_name,
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        overall_score=overall_score,
        strain_scores=strain_scores,
        coverage_scores=coverage_scores,
        confidence_scores={strain: result.get('structure_confidence', 0) * 100 
                          for strain, result in test_results.items() if 'error' not in result},
        accuracy_scores={},  # Будет заполнено при добавлении accuracy тестов
        response_time_ms=0,  # Будет измерено при тестировании
        regression_count=0,  # Будет проверено автоматически
        notes=""
    )

if __name__ == "__main__":
    # Инициализация системы метрик
    tracker = MetricsTracker()
    
    print("📊 Система метрик инициализирована")
    print(f"📈 Базовая линия: {tracker.baseline.overall_score} баллов")
    print(f"🎯 Цель: 85 баллов")
    print(f"📁 Файл метрик: {tracker.metrics_file}")
    
    # Сохраняем базовую линию
    tracker.save_history()
    print("✅ Базовая линия сохранена") 