#!/usr/bin/env python3
"""
📊 Просмотрщик результатов бенчмарка моделей
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def view_benchmark_results(results_file: str = "benchmark_results.json"):
    """Показывает результаты бенчмарка"""
    
    results_path = Path(results_file)
    
    if not results_path.exists():
        print(f"❌ Файл результатов не найден: {results_file}")
        print("💡 Запустите сначала: python model_benchmark.py")
        return
    
    try:
        with open(results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return
    
    # Проверяем формат данных
    if 'benchmark_info' in data:
        print_full_results(data)
    else:
        print_partial_results(data)

def print_full_results(data):
    """Выводит полные результаты бенчмарка"""
    info = data['benchmark_info']
    summary = data.get('summary', {})
    
    print("🏆 РЕЗУЛЬТАТЫ БЕНЧМАРКА LLM МОДЕЛЕЙ")
    print("=" * 60)
    
    # Общая информация
    start_time = datetime.fromisoformat(info['start_time'])
    end_time = datetime.fromisoformat(info['end_time'])
    
    print(f"📅 Начало: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Окончание: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Длительность: {info['duration_seconds']:.1f} секунд")
    print(f"🔢 Всего тестов: {info['total_tests']}")
    print(f"🤖 Моделей: {info['models_tested']}")
    print(f"📝 Запросов: {info['queries_tested']}")
    
    if 'summary' in data and 'rankings' in summary:
        rankings = summary['rankings']
        
        print(f"\n🏅 РЕЙТИНГИ:")
        print(f"🚀 Самая быстрая: {rankings['fastest']['model']} ({rankings['fastest']['time']:.2f}с)")
        print(f"📝 Самые подробные ответы: {rankings['most_detailed']['model']} ({rankings['most_detailed']['length']:.0f} символов)")
        print(f"📚 Больше источников: {rankings['most_sources']['model']} ({rankings['most_sources']['sources']:.1f} источников)")
        
        print(f"\n📈 СТАТИСТИКА ПО МОДЕЛЯМ:")
        for model, stats in summary['model_statistics'].items():
            print(f"   {model}:")
            print(f"      ✅ Успешность: {stats['success_rate']:.1f}%")
            print(f"      ⏱️ Среднее время: {stats['avg_response_time']:.2f}с")
            print(f"      📝 Средняя длина: {stats['avg_answer_length']:.0f} символов")
            print(f"      📚 Среднее источников: {stats['avg_sources_count']:.1f}")

def print_partial_results(data):
    """Выводит частичные результаты (в процессе тестирования)"""
    print("⏯️ ПРОМЕЖУТОЧНЫЕ РЕЗУЛЬТАТЫ БЕНЧМАРКА")
    print("=" * 60)
    
    if 'current_time' in data:
        current_time = datetime.fromisoformat(data['current_time'])
        print(f"📅 Текущее время: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if 'progress' in data:
        print(f"📊 Прогресс: {data['progress']}")
    
    results = data.get('results', [])
    if results:
        successful = len([r for r in results if r.get('success', False)])
        total = len(results)
        
        print(f"✅ Завершено тестов: {total}")
        print(f"✅ Успешных: {successful}/{total}")
        
        # Показываем последние результаты
        if total > 0:
            last_result = results[-1]
            print(f"\n🔬 Последний тест:")
            print(f"   Модель: {last_result.get('model', 'Неизвестно')}")
            print(f"   Запрос: {last_result.get('query', 'Неизвестно')}")
            if last_result.get('success'):
                print(f"   ✅ Время: {last_result.get('response_time', 0):.2f}с")
            else:
                print(f"   ❌ Ошибка: {last_result.get('error', 'Неизвестно')}")

def watch_progress():
    """Следит за прогрессом тестирования в реальном времени"""
    import time
    
    print("👀 СЛЕЖЕНИЕ ЗА ПРОГРЕССОМ БЕНЧМАРКА")
    print("=" * 40)
    print("💡 Нажмите Ctrl+C для выхода")
    print()
    
    try:
        while True:
            view_benchmark_results()
            print("\n" + "="*60)
            print("🔄 Обновление через 10 секунд...")
            time.sleep(10)
            
            # Очищаем экран (работает в большинстве терминалов)
            print("\033[2J\033[H", end="")
            
    except KeyboardInterrupt:
        print("\n👋 Слежение остановлено")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--watch":
            watch_progress()
        else:
            view_benchmark_results(sys.argv[1])
    else:
        view_benchmark_results()

if __name__ == "__main__":
    main() 