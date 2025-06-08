#!/usr/bin/env python3
"""
Тест улучшенного поиска после модернизации PDF экстракции
"""

import sys
from pathlib import Path
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

from lysobacter_rag.indexer.indexer import Indexer

def test_improved_search():
    """Тестирует улучшенный поиск"""
    
    print('🔍 ТЕСТ УЛУЧШЕННОГО ПОИСКА')
    print('=' * 50)
    
    indexer = Indexer()
    
    # Критические запросы для сравнения с NotebookLM
    test_queries = [
        {
            'query': 'YC5194 temperature range growth',
            'expected': 'Температурный диапазон роста для YC5194',
            'notebooklm_answer': '15-37°C'
        },
        {
            'query': 'Lysobacter capsici cell morphology size',
            'expected': 'Размеры и морфология клеток',
            'notebooklm_answer': '0.3-0.5 × 2.0-20 мкм'
        },
        {
            'query': 'strain biochemical characteristics table',
            'expected': 'Биохимические характеристики в табличной форме',
            'notebooklm_answer': 'Каталаза +, Оксидаза -, Глюкоза +'
        },
        {
            'query': 'pepper rhizosphere isolation origin',
            'expected': 'Происхождение из ризосферы перца',
            'notebooklm_answer': 'Ризосфера перца (pepper rhizosphere)'
        }
    ]
    
    print(f'🎯 Тестируем {len(test_queries)} критических запросов\n')
    
    improved_results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f'📝 ЗАПРОС {i}: "{test["query"]}"')
        print(f'   Ожидаем: {test["expected"]}')
        print(f'   NotebookLM: {test["notebooklm_answer"]}')
        
        results = indexer.search(test['query'], top_k=3)
        
        print(f'   📊 Результаты:')
        
        best_relevance = 0
        table_found = False
        answer_quality = 0
        
        for j, result in enumerate(results, 1):
            relevance = result.get('relevance_score', 0)
            text = result.get('text', '')
            
            # Определяем тип контента
            content_type = '📊' if 'таблица' in text.lower() or 'table' in text.lower() else '📝'
            if content_type == '📊':
                table_found = True
            
            print(f'      {j}. {content_type} Релевантность: {relevance:.3f}')
            print(f'         {text[:120]}...')
            
            if relevance > best_relevance:
                best_relevance = relevance
        
        # Оценка качества ответа
        if best_relevance > 0.6:
            answer_quality = 3  # Отлично
        elif best_relevance > 0.45:
            answer_quality = 2  # Хорошо
        elif best_relevance > 0.3:
            answer_quality = 1  # Удовлетворительно
        else:
            answer_quality = 0  # Плохо
        
        improved_results.append({
            'query': test['query'],
            'best_relevance': best_relevance,
            'table_found': table_found,
            'answer_quality': answer_quality,
            'notebooklm_target': test['notebooklm_answer']
        })
        
        print(f'   ✅ Оценка: {["❌ Плохо", "⚠️ Удовлетворительно", "✅ Хорошо", "🎉 Отлично"][answer_quality]}')
        print()
    
    # Общий анализ
    print('📈 ОБЩИЙ АНАЛИЗ УЛУЧШЕНИЙ')
    print('=' * 40)
    
    avg_relevance = sum(r['best_relevance'] for r in improved_results) / len(improved_results)
    tables_found = sum(1 for r in improved_results if r['table_found'])
    excellent_answers = sum(1 for r in improved_results if r['answer_quality'] == 3)
    good_answers = sum(1 for r in improved_results if r['answer_quality'] >= 2)
    
    print(f'📊 Средняя релевантность: {avg_relevance:.3f}')
    print(f'📋 Найдено таблиц: {tables_found}/{len(test_queries)}')
    print(f'🎉 Отличных ответов: {excellent_answers}/{len(test_queries)}')
    print(f'✅ Хороших ответов: {good_answers}/{len(test_queries)}')
    
    # Сравнение с предыдущими результатами
    print('\n🔄 СРАВНЕНИЕ С ПРЕДЫДУЩЕЙ СИСТЕМОЙ')
    print('=' * 40)
    
    # Предыдущие результаты (из анализа)
    old_avg_relevance = 0.45  # Из предыдущего анализа
    old_tables_found = 0      # Таблиц не было
    
    relevance_improvement = ((avg_relevance - old_avg_relevance) / old_avg_relevance) * 100
    table_improvement = "∞" if old_tables_found == 0 else tables_found - old_tables_found
    
    print(f'📈 Улучшение релевантности: +{relevance_improvement:.1f}%')
    print(f'📊 Улучшение таблиц: +{table_improvement}')
    print(f'🎯 Готовность к конкуренции с NotebookLM: {good_answers}/{len(test_queries)} запросов')
    
    # Рекомендации
    print('\n🎯 РЕКОМЕНДАЦИИ')
    print('=' * 20)
    
    if avg_relevance > 0.6:
        print('🎉 Отличные результаты! Система готова к продакшену.')
    elif avg_relevance > 0.45:
        print('✅ Хорошие результаты! Незначительная настройка поможет.')
    else:
        print('⚠️ Требуется дополнительная настройка параметров поиска.')
    
    print(f'📊 Извлечение таблиц: {"✅ Работает отлично" if tables_found > 0 else "❌ Требует доработки"}')
    
    return improved_results

if __name__ == "__main__":
    test_improved_search() 