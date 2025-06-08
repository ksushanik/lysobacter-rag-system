#!/usr/bin/env python3
"""
🧪 Тестировщик моделей для RAG-системы лизобактерий
==================================================

Тестирует различные LLM модели на качество ответов
о штамме GW1-59T и других лизобактериях.
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List
import json

# Добавляем пути для импортов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
from config import config
import logging

logger = logging.getLogger(__name__)

class ModelTester:
    """Тестировщик различных LLM моделей"""
    
    def __init__(self):
        self.test_queries = [
            "Что известно о штамме GW1-59T?",
            "GW1-59T strain characteristics", 
            "Морфология лизобактерий GW1-59T",
            "Где был выделен штамм GW1-59T?",
            "Биохимические свойства GW1-59T",
            "Филогенетический анализ GW1-59T"
        ]
        
        self.models_to_test = [
            "deepseek/deepseek-chat",
            "deepseek/deepseek-v3-base:free", 
            "deepseek/deepseek-chat-v3-0324:free",
            "deepseek/deepseek-r1:free",
            "google/gemini-2.0-flash-exp:free"
        ]
    
    def test_model(self, model_name: str, query: str = None) -> Dict:
        """
        Тестирует конкретную модель
        
        Args:
            model_name: Название модели для тестирования
            query: Тестовый запрос (по умолчанию о GW1-59T)
            
        Returns:
            Dict: Результаты тестирования
        """
        print(f"🔬 Тестирую модель: {model_name}")
        print("=" * 50)
        
        if query is None:
            query = "Что известно о штамме GW1-59T?"
        
        # Временно меняем модель в конфиге
        original_model = config.OPENROUTER_MODEL
        config.OPENROUTER_MODEL = model_name
        
        try:
            # Инициализируем RAG pipeline
            rag = RAGPipeline()
            
            start_time = time.time()
            
                         # Выполняем запрос
            result = rag.ask_question(query)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"📝 Запрос: {query}")
            print(f"⏱️ Время ответа: {response_time:.2f} сек")
            print(f"📊 Найдено источников: {len(result.get('sources', []))}")
            print("\n💬 Ответ:")
            print("-" * 40)
            print(result.get('answer', 'Ответ не получен'))
            print("-" * 40)
            
            # Показываем источники
            if result.get('sources'):
                print(f"\n📚 Источники ({len(result['sources'])}):")
                for i, source in enumerate(result['sources'][:3], 1):
                    print(f"  {i}. {source.get('source', 'Неизвестно')} "
                          f"(релевантность: {source.get('score', 0):.3f})")
            
            return {
                'model': model_name,
                'query': query,
                'answer': result.get('answer', ''),
                'response_time': response_time,
                'sources_count': len(result.get('sources', [])),
                'success': True,
                'error': None
            }
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании модели {model_name}: {e}")
            return {
                'model': model_name,
                'query': query,
                'answer': '',
                'response_time': 0,
                'sources_count': 0,
                'success': False,
                'error': str(e)
            }
        
        finally:
            # Восстанавливаем оригинальную модель
            config.OPENROUTER_MODEL = original_model
    
    def compare_models(self, models: List[str] = None, query: str = None) -> List[Dict]:
        """
        Сравнивает несколько моделей
        
        Args:
            models: Список моделей для сравнения
            query: Тестовый запрос
            
        Returns:
            List[Dict]: Результаты сравнения
        """
        if models is None:
            models = self.models_to_test
            
        if query is None:
            query = "Что известно о штамме GW1-59T?"
        
        print(f"🏆 СРАВНЕНИЕ МОДЕЛЕЙ")
        print("=" * 60)
        print(f"📝 Тестовый запрос: {query}")
        print("=" * 60)
        
        results = []
        
        for model in models:
            print(f"\n🔬 Тестирую: {model}")
            print("-" * 40)
            
            result = self.test_model(model, query)
            results.append(result)
            
            time.sleep(2)  # Пауза между запросами
        
        # Сводка результатов
        print(f"\n📊 СВОДКА РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        successful_models = [r for r in results if r['success']]
        
        if successful_models:
            # Сортируем по времени ответа
            by_speed = sorted(successful_models, key=lambda x: x['response_time'])
            print(f"🚀 Самая быстрая: {by_speed[0]['model']} ({by_speed[0]['response_time']:.2f}с)")
            
            # Сортируем по количеству источников
            by_sources = sorted(successful_models, key=lambda x: x['sources_count'], reverse=True)
            print(f"📚 Больше источников: {by_sources[0]['model']} ({by_sources[0]['sources_count']} источников)")
        
        # Показываем ошибки
        failed_models = [r for r in results if not r['success']]
        if failed_models:
            print(f"\n❌ Модели с ошибками:")
            for result in failed_models:
                print(f"   • {result['model']}: {result['error']}")
        
        return results
    
    def benchmark_all_queries(self, model: str) -> Dict:
        """
        Тестирует модель на всех тестовых запросах
        
        Args:
            model: Название модели
            
        Returns:
            Dict: Полные результаты бенчмарка
        """
        print(f"📋 ПОЛНЫЙ БЕНЧМАРК МОДЕЛИ: {model}")
        print("=" * 60)
        
        results = []
        total_time = 0
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n🔍 Запрос {i}/{len(self.test_queries)}: {query}")
            print("-" * 40)
            
            result = self.test_model(model, query)
            results.append(result)
            
            if result['success']:
                total_time += result['response_time']
            
            time.sleep(1)
        
        # Сводная статистика
        successful = [r for r in results if r['success']]
        success_rate = len(successful) / len(results) * 100
        avg_time = total_time / len(successful) if successful else 0
        avg_sources = sum(r['sources_count'] for r in successful) / len(successful) if successful else 0
        
        print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 40)
        print(f"✅ Успешных запросов: {len(successful)}/{len(results)} ({success_rate:.1f}%)")
        print(f"⏱️ Среднее время ответа: {avg_time:.2f} сек")
        print(f"📚 Среднее количество источников: {avg_sources:.1f}")
        
        return {
            'model': model,
            'total_queries': len(self.test_queries),
            'successful_queries': len(successful),
            'success_rate': success_rate,
            'average_response_time': avg_time,
            'average_sources': avg_sources,
            'detailed_results': results
        }

def test_model(model_name: str, query: str = None):
    """Функция для тестирования одной модели"""
    tester = ModelTester()
    tester.test_model(model_name, query)

def compare_models(models: List[str] = None):
    """Функция для сравнения моделей"""
    tester = ModelTester()
    tester.compare_models(models)

def main():
    """Главная функция для запуска из командной строки"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Тестировщик моделей")
    parser.add_argument('--model', help='Модель для тестирования')
    parser.add_argument('--query', default='Что известно о штамме GW1-59T?', help='Тестовый запрос')
    parser.add_argument('--compare', action='store_true', help='Сравнить несколько моделей')
    parser.add_argument('--benchmark', action='store_true', help='Полный бенчмарк модели')
    
    args = parser.parse_args()
    
    tester = ModelTester()
    
    if args.compare:
        tester.compare_models()
    elif args.benchmark and args.model:
        tester.benchmark_all_queries(args.model)
    elif args.model:
        tester.test_model(args.model, args.query)
    else:
        print("Укажите --model для тестирования или --compare для сравнения")

if __name__ == "__main__":
    main() 