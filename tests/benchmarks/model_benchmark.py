#!/usr/bin/env python3
"""
🏆 Продвинутый бенчмарк LLM моделей для RAG-системы лизобактерий
================================================================

Тестирует и сравнивает различные модели с подробными метриками.
Сохраняет результаты в JSON и показывает прогресс в реальном времени.
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Добавляем пути для импорта из корня проекта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "scripts"))

from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
from config import config

class ModelBenchmark:
    """Класс для бенчмарка моделей"""
    
    def __init__(self):
        self.models = [
            "deepseek/deepseek-chat",                # Базовая DeepSeek
            "deepseek/deepseek-v3-base:free",        # Новая v3 base
            "deepseek/deepseek-chat-v3-0324:free",   # Чат v3
            "deepseek/deepseek-r1:free",             # R1 для рассуждений
            "google/gemini-2.0-flash-exp:free"       # Google Gemini 2.0
        ]
        
        self.test_queries = [
            "Что известно о штамме GW1-59T?",
            "GW1-59T strain characteristics",
            "Морфология лизобактерий GW1-59T",
            "Где был выделен штамм GW1-59T?",
            "Биохимические свойства GW1-59T"
        ]
        
        self.results_file = project_root / "benchmark_results.json"
        
    def progress_bar(self, current: int, total: int, width: int = 40) -> str:
        """Создает индикатор прогресса"""
        percent = current / total
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percent:.1%} ({current}/{total})"
    
    def test_single_model(self, model: str, query: str) -> Dict[str, Any]:
        """Тестирует одну модель на одном запросе"""
        print(f"  🔬 Модель: {model}")
        print(f"  📝 Запрос: {query}")
        
        # Меняем модель в конфиге
        original_model = config.OPENROUTER_MODEL
        config.OPENROUTER_MODEL = model
        
        try:
            # Создаем RAG pipeline
            rag = RAGPipeline()
            
            start_time = time.time()
            result = rag.ask_question(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            answer = result.get('answer', '')
            answer_length = len(answer)
            sources_count = len(result.get('sources', []))
            confidence = result.get('confidence', 0)
            
            print(f"  ✅ Время: {response_time:.2f}с | Символов: {answer_length} | Источников: {sources_count}")
            
            return {
                'model': model,
                'query': query,
                'success': True,
                'response_time': response_time,
                'answer_length': answer_length,
                'sources_count': sources_count,
                'confidence': confidence,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Ошибка: {error_msg[:50]}...")
            
            return {
                'model': model,
                'query': query,
                'success': False,
                'error': error_msg,
                'response_time': 0,
                'answer_length': 0,
                'sources_count': 0,
                'confidence': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        finally:
            # Восстанавливаем оригинальную модель
            config.OPENROUTER_MODEL = original_model
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Запускает полный бенчмарк всех моделей на всех запросах"""
        print("🏆 ПОЛНЫЙ БЕНЧМАРК LLM МОДЕЛЕЙ")
        print("=" * 60)
        print(f"📊 Моделей: {len(self.models)}")
        print(f"📝 Запросов: {len(self.test_queries)}")
        print(f"🔢 Всего тестов: {len(self.models) * len(self.test_queries)}")
        print("=" * 60)
        
        all_results = []
        total_tests = len(self.models) * len(self.test_queries)
        current_test = 0
        
        benchmark_start = datetime.now()
        
        for model_idx, model in enumerate(self.models, 1):
            print(f"\n🎯 [{model_idx}/{len(self.models)}] Тестирую модель: {model}")
            print("-" * 50)
            
            model_results = []
            
            for query_idx, query in enumerate(self.test_queries, 1):
                current_test += 1
                
                print(f"\n{self.progress_bar(current_test, total_tests)}")
                print(f"📍 Тест {current_test}/{total_tests}")
                
                result = self.test_single_model(model, query)
                model_results.append(result)
                all_results.append(result)
                
                # Сохраняем промежуточные результаты
                self.save_results({
                    'benchmark_start': benchmark_start.isoformat(),
                    'current_time': datetime.now().isoformat(),
                    'progress': f"{current_test}/{total_tests}",
                    'results': all_results
                })
                
                time.sleep(1)  # Пауза между запросами
            
            # Статистика по модели
            successful = [r for r in model_results if r['success']]
            if successful:
                avg_time = sum(r['response_time'] for r in successful) / len(successful)
                avg_length = sum(r['answer_length'] for r in successful) / len(successful)
                success_rate = len(successful) / len(model_results) * 100
                
                print(f"\n📈 Статистика модели {model}:")
                print(f"   ✅ Успешность: {success_rate:.1f}%")
                print(f"   ⏱️ Среднее время: {avg_time:.2f}с")
                print(f"   📝 Средняя длина: {avg_length:.0f} символов")
        
        benchmark_end = datetime.now()
        
        # Финальные результаты
        final_results = {
            'benchmark_info': {
                'start_time': benchmark_start.isoformat(),
                'end_time': benchmark_end.isoformat(),
                'duration_seconds': (benchmark_end - benchmark_start).total_seconds(),
                'total_tests': total_tests,
                'models_tested': len(self.models),
                'queries_tested': len(self.test_queries)
            },
            'results': all_results,
            'summary': self.analyze_results(all_results)
        }
        
        self.save_results(final_results)
        self.print_summary(final_results)
        
        return final_results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализирует результаты тестирования"""
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if not successful:
            return {'error': 'Нет успешных результатов для анализа'}
        
        # Группируем по моделям
        by_model = {}
        for result in successful:
            model = result['model']
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(result)
        
        model_stats = {}
        for model, model_results in by_model.items():
            model_stats[model] = {
                'success_rate': len(model_results) / len([r for r in results if r['model'] == model]) * 100,
                'avg_response_time': sum(r['response_time'] for r in model_results) / len(model_results),
                'avg_answer_length': sum(r['answer_length'] for r in model_results) / len(model_results),
                'avg_sources_count': sum(r['sources_count'] for r in model_results) / len(model_results),
                'total_tests': len(model_results)
            }
        
        # Рейтинги
        fastest_model = min(model_stats.items(), key=lambda x: x[1]['avg_response_time'])
        most_detailed = max(model_stats.items(), key=lambda x: x[1]['avg_answer_length'])
        most_sources = max(model_stats.items(), key=lambda x: x[1]['avg_sources_count'])
        
        return {
            'total_successful': len(successful),
            'total_failed': len(failed),
            'success_rate_overall': len(successful) / len(results) * 100,
            'model_statistics': model_stats,
            'rankings': {
                'fastest': {'model': fastest_model[0], 'time': fastest_model[1]['avg_response_time']},
                'most_detailed': {'model': most_detailed[0], 'length': most_detailed[1]['avg_answer_length']},
                'most_sources': {'model': most_sources[0], 'sources': most_sources[1]['avg_sources_count']}
            }
        }
    
    def save_results(self, results: Dict[str, Any]):
        """Сохраняет результаты в JSON файл"""
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def print_summary(self, results: Dict[str, Any]):
        """Выводит краткую сводку результатов"""
        summary = results['summary']
        
        print(f"\n🏆 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ БЕНЧМАРКА")
        print("=" * 60)
        print(f"⏱️ Длительность: {results['benchmark_info']['duration_seconds']:.1f} секунд")
        print(f"✅ Успешных тестов: {summary['total_successful']}/{results['benchmark_info']['total_tests']}")
        print(f"📊 Общая успешность: {summary['success_rate_overall']:.1f}%")
        
        print(f"\n🏅 РЕЙТИНГИ:")
        print(f"🚀 Самая быстрая: {summary['rankings']['fastest']['model']} ({summary['rankings']['fastest']['time']:.2f}с)")
        print(f"📝 Самые подробные ответы: {summary['rankings']['most_detailed']['model']} ({summary['rankings']['most_detailed']['length']:.0f} символов)")
        print(f"📚 Больше источников: {summary['rankings']['most_sources']['model']} ({summary['rankings']['most_sources']['sources']:.1f} источников)")
        
        print(f"\n📈 СТАТИСТИКА ПО МОДЕЛЯМ:")
        for model, stats in summary['model_statistics'].items():
            print(f"   {model}:")
            print(f"      ✅ Успешность: {stats['success_rate']:.1f}%")
            print(f"      ⏱️ Среднее время: {stats['avg_response_time']:.2f}с")
            print(f"      📝 Средняя длина: {stats['avg_answer_length']:.0f} символов")
            print(f"      📚 Среднее источников: {stats['avg_sources_count']:.1f}")
        
        print(f"\n💾 Подробные результаты сохранены в: {self.results_file}")

def main():
    """Главная функция"""
    benchmark = ModelBenchmark()
    
    print("🚀 Запускаю полный бенчмарк моделей...")
    print("💡 Результаты сохраняются в benchmark_results.json")
    print("⏯️ Прогресс отображается в реальном времени")
    
    input("\n📍 Нажмите Enter для начала тестирования...")
    
    try:
        results = benchmark.run_full_benchmark()
        print(f"\n🎉 Бенчмарк завершен успешно!")
        
    except KeyboardInterrupt:
        print(f"\n⏸️ Бенчмарк прерван пользователем")
        print(f"💾 Промежуточные результаты сохранены в {benchmark.results_file}")
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении бенчмарка: {e}")

if __name__ == "__main__":
    main() 