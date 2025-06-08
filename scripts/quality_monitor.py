#!/usr/bin/env python3
"""
Система постоянного мониторинга качества RAG-системы
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

class QualityMonitor:
    """Монитор качества RAG-системы"""
    
    def __init__(self):
        self.metrics_file = Path("quality_metrics.json")
        self.alerts_file = Path("quality_alerts.json")
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict]:
        """Загружает историю метрик"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Сохраняет историю метрик"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def run_quality_check(self):
        """Запускает проверку качества"""
        
        print("📊 МОНИТОРИНГ КАЧЕСТВА RAG-СИСТЕМЫ")
        print("=" * 50)
        
        try:
            from lysobacter_rag.indexer.indexer import Indexer
            from lysobacter_rag.quality_control.text_enhancer import ScientificTextEnhancer
            
            indexer = Indexer()
            enhancer = ScientificTextEnhancer()
            
            # Текущее время
            timestamp = datetime.now().isoformat()
            
            # Базовые метрики системы
            system_metrics = self._collect_system_metrics(indexer)
            
            # Метрики качества данных
            quality_metrics = self._collect_quality_metrics(indexer, enhancer)
            
            # Метрики производительности
            performance_metrics = self._collect_performance_metrics(indexer)
            
            # Объединяем все метрики
            current_metrics = {
                'timestamp': timestamp,
                'system': system_metrics,
                'quality': quality_metrics,
                'performance': performance_metrics
            }
            
            # Добавляем в историю
            self.history.append(current_metrics)
            
            # Ограничиваем историю (последние 100 записей)
            if len(self.history) > 100:
                self.history = self.history[-100:]
            
            self._save_history()
            
            # Анализ и оповещения
            alerts = self._analyze_metrics(current_metrics)
            
            # Отображение результатов
            self._display_results(current_metrics, alerts)
            
            # Генерация рекомендаций
            recommendations = self._generate_recommendations(current_metrics, alerts)
            
            if recommendations:
                print(f"\n💡 РЕКОМЕНДАЦИИ:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка мониторинга: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _collect_system_metrics(self, indexer) -> Dict:
        """Собирает системные метрики"""
        
        try:
            stats = indexer.get_collection_stats()
            return {
                'total_chunks': stats.get('total_chunks', 0),
                'unique_sources': stats.get('unique_sources', 0),
                'chunk_types': stats.get('chunk_types', {}),
                'index_health': 'healthy' if stats.get('total_chunks', 0) > 0 else 'empty'
            }
        except Exception as e:
            return {
                'error': str(e),
                'index_health': 'error'
            }
    
    def _collect_quality_metrics(self, indexer, enhancer) -> Dict:
        """Собирает метрики качества данных"""
        
        # Тестовые запросы для проверки качества
        quality_tests = [
            {'query': 'GW1-59T', 'category': 'strain_accuracy'},
            {'query': 'temperature growth', 'category': 'data_format'},
            {'query': 'pH range', 'category': 'units'},
            {'query': 'fatty acids', 'category': 'chemistry'},
            {'query': 'type strain', 'category': 'terminology'}
        ]
        
        metrics = {
            'quality_scores': {},
            'common_issues': {},
            'test_results': {}
        }
        
        total_score = 0
        total_tests = 0
        
        for test in quality_tests:
            try:
                results = indexer.search(test['query'], top_k=3)
                
                if results:
                    # Анализируем качество результатов
                    category_score = 0
                    category_issues = []
                    
                    for result in results:
                        text = result['text']
                        score = enhancer.get_quality_score(text)
                        category_score += score
                        
                        # Проверяем специфические проблемы
                        issues = self._detect_issues(text)
                        category_issues.extend(issues)
                    
                    category_score /= len(results)
                    metrics['quality_scores'][test['category']] = category_score
                    metrics['common_issues'][test['category']] = category_issues
                    
                    total_score += category_score
                    total_tests += 1
                
                metrics['test_results'][test['query']] = {
                    'found_results': len(results),
                    'avg_relevance': sum(r.get('relevance_score', 0) for r in results) / len(results) if results else 0
                }
                
            except Exception as e:
                metrics['test_results'][test['query']] = {'error': str(e)}
        
        # Общий скор качества
        metrics['overall_quality_score'] = total_score / total_tests if total_tests > 0 else 0
        
        return metrics
    
    def _collect_performance_metrics(self, indexer) -> Dict:
        """Собирает метрики производительности"""
        
        metrics = {}
        
        # Тест скорости поиска
        start_time = time.time()
        try:
            results = indexer.search("test query", top_k=5)
            search_time = time.time() - start_time
            metrics['search_latency'] = search_time
            metrics['search_status'] = 'ok'
        except Exception as e:
            metrics['search_latency'] = -1
            metrics['search_status'] = 'error'
            metrics['search_error'] = str(e)
        
        return metrics
    
    def _detect_issues(self, text: str) -> List[str]:
        """Обнаруживает проблемы в тексте"""
        
        issues = []
        
        # Разорванные штаммы
        import re
        if re.search(r'\w+\s*-\s*\d+\s+T', text):
            issues.append('broken_strain_names')
        
        # Разорванные формулы
        if re.search(r'C\s+\d+\s*:\s*\d+', text):
            issues.append('broken_formulas')
        
        # Слитные слова
        if re.search(r'[a-zA-Z]{50,}', text):
            issues.append('merged_words')
        
        # Разорванные единицы
        if re.search(r'\d+\s+°\s+C|\d+\s+%\s+\w+', text):
            issues.append('broken_units')
        
        return issues
    
    def _analyze_metrics(self, metrics: Dict) -> List[Dict]:
        """Анализирует метрики и генерирует оповещения"""
        
        alerts = []
        
        # Проверяем качество данных
        quality_score = metrics['quality']['overall_quality_score']
        
        if quality_score < 0.4:
            alerts.append({
                'level': 'critical',
                'type': 'quality',
                'message': f'Критически низкое качество данных: {quality_score:.1%}',
                'action': 'Требуется немедленная переиндексация с улучшениями'
            })
        elif quality_score < 0.6:
            alerts.append({
                'level': 'warning',
                'type': 'quality',
                'message': f'Низкое качество данных: {quality_score:.1%}',
                'action': 'Рекомендуется применить улучшения качества'
            })
        
        # Проверяем производительность
        search_latency = metrics['performance'].get('search_latency', 0)
        
        if search_latency > 2.0:
            alerts.append({
                'level': 'warning',
                'type': 'performance',
                'message': f'Медленный поиск: {search_latency:.2f}s',
                'action': 'Проверьте нагрузку на систему'
            })
        
        # Проверяем системные метрики
        total_chunks = metrics['system'].get('total_chunks', 0)
        
        if total_chunks == 0:
            alerts.append({
                'level': 'critical',
                'type': 'system',
                'message': 'Индекс пуст',
                'action': 'Запустите индексацию документов'
            })
        elif total_chunks < 1000:
            alerts.append({
                'level': 'info',
                'type': 'system',
                'message': f'Мало данных в индексе: {total_chunks} чанков',
                'action': 'Рассмотрите добавление дополнительных документов'
            })
        
        # Сохраняем оповещения
        if alerts:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': metrics['timestamp'],
                    'alerts': alerts
                }, f, ensure_ascii=False, indent=2)
        
        return alerts
    
    def _display_results(self, metrics: Dict, alerts: List[Dict]):
        """Отображает результаты мониторинга"""
        
        print(f"\n📊 ТЕКУЩИЕ МЕТРИКИ:")
        
        # Системные метрики
        system = metrics['system']
        print(f"   📁 Чанков в индексе: {system.get('total_chunks', 0)}")
        print(f"   📄 Источников: {system.get('unique_sources', 0)}")
        print(f"   🏥 Состояние индекса: {system.get('index_health', 'unknown')}")
        
        # Качество данных
        quality = metrics['quality']
        quality_score = quality.get('overall_quality_score', 0)
        quality_status = "🟢" if quality_score > 0.8 else "🟡" if quality_score > 0.6 else "🔴"
        print(f"   {quality_status} Качество данных: {quality_score:.1%}")
        
        # Производительность
        performance = metrics['performance']
        search_time = performance.get('search_latency', -1)
        if search_time >= 0:
            perf_status = "🟢" if search_time < 1.0 else "🟡" if search_time < 2.0 else "🔴"
            print(f"   {perf_status} Скорость поиска: {search_time:.2f}s")
        else:
            print(f"   🔴 Ошибка поиска")
        
        # Оповещения
        if alerts:
            print(f"\n🚨 ОПОВЕЩЕНИЯ:")
            for alert in alerts:
                level_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
                icon = level_icon.get(alert['level'], "ℹ️")
                print(f"   {icon} {alert['message']}")
                print(f"      💡 {alert['action']}")
    
    def _generate_recommendations(self, metrics: Dict, alerts: List[Dict]) -> List[str]:
        """Генерирует рекомендации по улучшению"""
        
        recommendations = []
        
        # На основе оповещений
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        warning_alerts = [a for a in alerts if a['level'] == 'warning']
        
        if critical_alerts:
            recommendations.append("🚨 Устраните критические проблемы: make full-quality-reindex")
        
        if warning_alerts:
            recommendations.append("⚠️ Рассмотрите улучшения: make quick-quality-improvement")
        
        # На основе трендов
        if len(self.history) >= 2:
            prev_metrics = self.history[-2]
            
            # Сравниваем качество
            prev_quality = prev_metrics.get('quality', {}).get('overall_quality_score', 0)
            curr_quality = metrics['quality']['overall_quality_score']
            
            if curr_quality < prev_quality - 0.1:
                recommendations.append("📉 Качество снижается - проверьте недавние изменения")
            
            # Сравниваем производительность
            prev_latency = prev_metrics.get('performance', {}).get('search_latency', 0)
            curr_latency = metrics['performance'].get('search_latency', 0)
            
            if curr_latency > prev_latency * 1.5:
                recommendations.append("🐌 Производительность снижается - проверьте нагрузку")
        
        # Общие рекомендации
        quality_score = metrics['quality']['overall_quality_score']
        
        if quality_score < 0.8:
            recommendations.append("🔧 Регулярно запускайте: make check-overall-quality")
        
        if not recommendations:
            recommendations.append("✅ Система работает стабильно")
        
        return recommendations
    
    def get_quality_trend(self, days: int = 7) -> Dict:
        """Получает тренд качества за последние дни"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_metrics = [
            m for m in self.history 
            if datetime.fromisoformat(m['timestamp']) > cutoff_date
        ]
        
        if not recent_metrics:
            return {'trend': 'no_data'}
        
        quality_scores = [
            m['quality']['overall_quality_score'] 
            for m in recent_metrics 
            if 'quality' in m and 'overall_quality_score' in m['quality']
        ]
        
        if len(quality_scores) < 2:
            return {'trend': 'insufficient_data'}
        
        # Простой тренд
        first_half = quality_scores[:len(quality_scores)//2]
        second_half = quality_scores[len(quality_scores)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first + 0.05:
            trend = 'improving'
        elif avg_second < avg_first - 0.05:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'current_score': quality_scores[-1],
            'average_score': sum(quality_scores) / len(quality_scores),
            'data_points': len(quality_scores)
        }

def main():
    """Основная функция мониторинга"""
    
    monitor = QualityMonitor()
    
    # Запускаем проверку
    success = monitor.run_quality_check()
    
    if success:
        # Показываем тренд
        trend = monitor.get_quality_trend()
        
        if trend['trend'] != 'no_data':
            print(f"\n📈 ТРЕНД КАЧЕСТВА (7 дней):")
            trend_icons = {
                'improving': '📈 Улучшается',
                'stable': '➡️ Стабильно',
                'declining': '📉 Снижается'
            }
            print(f"   {trend_icons.get(trend['trend'], '❓ Неизвестно')}")
            
            if 'current_score' in trend:
                print(f"   Текущий скор: {trend['current_score']:.1%}")
                print(f"   Средний скор: {trend['average_score']:.1%}")
        
        print(f"\n📄 Подробные метрики сохранены в quality_metrics.json")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 