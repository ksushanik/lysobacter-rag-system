#!/usr/bin/env python3
"""
ТЕСТ КАЧЕСТВА: Сравнение ответов до и после умного чанкинга
"""

import sys
import os
from pathlib import Path
import time

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.indexer.indexer import Indexer

def test_quality_improvements():
    """Тестирует улучшения качества после умного чанкинга"""
    
    print("🔬 ТЕСТ КАЧЕСТВА: До vs После умного чанкинга")
    print("=" * 60)
    
    # Инициализируем систему
    indexer = Indexer()
    
    # Проверяем состояние базы
    stats = indexer.get_collection_stats()
    print(f"📊 Текущее состояние базы:")
    print(f"   Всего чанков: {stats.get('total_chunks', 0)}")
    
    if stats.get('total_chunks', 0) == 0:
        print("❌ База данных пуста! Запустите переиндексацию сначала.")
        return False
    
    # Тестовые запросы для оценки качества
    test_cases = [
        {
            'query': 'Lysobacter capsici YC5194 характеристики',
            'expected_keywords': ['YC5194', 'capsici', 'type strain', 'rhizosphere', 'pepper'],
            'description': 'Основная информация о штамме YC5194'
        },
        {
            'query': 'temperature range growth Lysobacter',
            'expected_keywords': ['temperature', '°C', 'growth', 'range', 'optimal'],
            'description': 'Температурные условия роста'
        },
        {
            'query': 'G+C content DNA mol%',
            'expected_keywords': ['G+C', 'content', 'mol%', 'DNA', 'genomic'],
            'description': 'Содержание G+C в ДНК'
        },
        {
            'query': 'cell morphology size micrometers',
            'expected_keywords': ['cell', 'morphology', 'μm', 'size', 'rod-shaped'],
            'description': 'Морфология клеток'
        },
        {
            'query': 'pH range tolerance acidic alkaline',
            'expected_keywords': ['pH', 'range', 'growth', 'acidic', 'alkaline'],
            'description': 'pH толерантность'
        },
        {
            'query': 'catalase oxidase positive biochemical',
            'expected_keywords': ['catalase', 'oxidase', 'positive', 'biochemical', 'enzyme'],
            'description': 'Биохимические характеристики'
        },
        {
            'query': '16S rRNA phylogenetic analysis',
            'expected_keywords': ['16S', 'rRNA', 'phylogenetic', 'sequence', 'analysis'],
            'description': 'Филогенетический анализ'
        },
        {
            'query': 'antimicrobial activity biocontrol plant pathogen',
            'expected_keywords': ['antimicrobial', 'activity', 'biocontrol', 'pathogen', 'plant'],
            'description': 'Антимикробная активность'
        }
    ]
    
    print(f"\n🔍 Тестирование {len(test_cases)} запросов...")
    print("-" * 50)
    
    total_score = 0
    detailed_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 🔍 {test_case['description']}")
        print(f"   Запрос: '{test_case['query']}'")
        
        try:
            # Выполняем поиск
            results = indexer.search(test_case['query'], top_k=5)
            
            if not results:
                print(f"   ❌ Результаты не найдены")
                detailed_results.append({
                    'query': test_case['query'],
                    'description': test_case['description'],
                    'score': 0,
                    'issues': ['no_results'],
                    'relevance_scores': []
                })
                continue
            
            # Анализируем качество результатов
            relevance_scores = [r['relevance_score'] for r in results]
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            max_relevance = max(relevance_scores)
            
            print(f"   📊 Найдено: {len(results)} результатов")
            print(f"   📈 Релевантность: ср={avg_relevance:.3f}, макс={max_relevance:.3f}")
            
            # Проверяем наличие ожидаемых ключевых слов
            all_text = ' '.join([r['text'] for r in results])
            found_keywords = []
            for keyword in test_case['expected_keywords']:
                if keyword.lower() in all_text.lower():
                    found_keywords.append(keyword)
            
            keyword_ratio = len(found_keywords) / len(test_case['expected_keywords'])
            print(f"   🔑 Ключевые слова: {len(found_keywords)}/{len(test_case['expected_keywords'])} ({keyword_ratio:.1%})")
            print(f"      Найдены: {', '.join(found_keywords) if found_keywords else 'нет'}")
            
            # Анализируем размеры чанков
            chunk_sizes = [len(r['text']) for r in results]
            avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
            print(f"   📏 Средний размер чанка: {avg_chunk_size:.0f} символов")
            
            # Проверяем разнообразие источников
            sources = set(r['metadata'].get('source_pdf', 'unknown') for r in results)
            print(f"   📚 Источников: {len(sources)}")
            
            # Вычисляем общий балл
            relevance_score = min(100, avg_relevance * 100)
            keyword_score = keyword_ratio * 100
            size_score = max(0, 100 - abs(avg_chunk_size - 350) / 350 * 100)  # Оптимальный размер 350
            diversity_score = min(100, len(sources) * 25)  # Максимум 4 источника
            
            overall_score = (relevance_score + keyword_score + size_score + diversity_score) / 4
            
            print(f"   🎯 Оценка качества: {overall_score:.1f}%")
            print(f"      Релевантность: {relevance_score:.1f}%")
            print(f"      Ключевые слова: {keyword_score:.1f}%")
            print(f"      Размер чанков: {size_score:.1f}%")
            print(f"      Разнообразие: {diversity_score:.1f}%")
            
            # Определяем проблемы
            issues = []
            if avg_relevance < 0.3:
                issues.append('low_relevance')
            if keyword_ratio < 0.5:
                issues.append('missing_keywords')
            if avg_chunk_size > 1000:
                issues.append('chunks_too_large')
            if avg_chunk_size < 100:
                issues.append('chunks_too_small')
            if len(sources) < 2:
                issues.append('low_diversity')
            
            # Показываем лучший результат
            best_result = results[0]
            print(f"   💡 Лучший результат (релевантность {best_result['relevance_score']:.3f}):")
            print(f"      Источник: {best_result['metadata'].get('source_pdf', 'N/A')}")
            print(f"      Текст: {best_result['text'][:200]}...")
            
            detailed_results.append({
                'query': test_case['query'],
                'description': test_case['description'],
                'score': overall_score,
                'relevance_scores': relevance_scores,
                'keyword_ratio': keyword_ratio,
                'chunk_size': avg_chunk_size,
                'source_count': len(sources),
                'issues': issues
            })
            
            total_score += overall_score
            
        except Exception as e:
            print(f"   ❌ Ошибка при тестировании: {e}")
            detailed_results.append({
                'query': test_case['query'],
                'description': test_case['description'],
                'score': 0,
                'issues': [f'error: {str(e)}'],
                'relevance_scores': []
            })
    
    # Итоговая оценка
    avg_score = total_score / len(test_cases) if test_cases else 0
    
    print(f"\n🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 40)
    print(f"📊 Средняя оценка качества: {avg_score:.1f}%")
    
    # Классификация результатов
    excellent_tests = [r for r in detailed_results if r['score'] >= 80]
    good_tests = [r for r in detailed_results if 60 <= r['score'] < 80]
    poor_tests = [r for r in detailed_results if r['score'] < 60]
    
    print(f"🏆 Отличные результаты: {len(excellent_tests)}/{len(test_cases)}")
    print(f"✅ Хорошие результаты: {len(good_tests)}/{len(test_cases)}")
    print(f"⚠️ Плохие результаты: {len(poor_tests)}/{len(test_cases)}")
    
    # Анализ проблем
    all_issues = []
    for result in detailed_results:
        all_issues.extend(result['issues'])
    
    issue_counts = {}
    for issue in all_issues:
        issue_counts[issue] = issue_counts.get(issue, 0) + 1
    
    if issue_counts:
        print(f"\n🔍 Основные проблемы:")
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {issue}: {count} случаев")
    
    # Финальная оценка
    if avg_score >= 80:
        print(f"\n🎉 ОТЛИЧНО: Умный чанкинг значительно улучшил качество!")
        print(f"   Система готова для продуктивного использования")
        success_level = "excellent"
    elif avg_score >= 60:
        print(f"\n✅ ХОРОШО: Заметные улучшения качества")
        print(f"   Система работает приемлемо, можно использовать")
        success_level = "good"
    elif avg_score >= 40:
        print(f"\n⚠️ УДОВЛЕТВОРИТЕЛЬНО: Некоторые улучшения")
        print(f"   Требуется дополнительная настройка")
        success_level = "satisfactory"
    else:
        print(f"\n❌ ПЛОХО: Серьёзные проблемы остаются")
        print(f"   Необходимо пересмотреть подход")
        success_level = "poor"
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if 'low_relevance' in issue_counts:
        print("   🔧 Улучшить настройки эмбеддингов или модель")
    if 'missing_keywords' in issue_counts:
        print("   🔧 Улучшить извлечение ключевых терминов")
    if 'chunks_too_large' in issue_counts:
        print("   🔧 Уменьшить размер чанков")
    if 'chunks_too_small' in issue_counts:
        print("   🔧 Увеличить размер чанков")
    if 'low_diversity' in issue_counts:
        print("   🔧 Улучшить алгоритм поиска для большего разнообразия")
    
    # Сравнение с предыдущими результатами
    print(f"\n📈 ПРОГРЕСС ПО СРАВНЕНИЮ С ДИАГНОСТИКОЙ:")
    print("   Диагностика показала среднюю релевантность: 0.444")
    if detailed_results:
        current_avg_relevance = sum(
            sum(r['relevance_scores']) / len(r['relevance_scores']) 
            for r in detailed_results 
            if r['relevance_scores']
        ) / len([r for r in detailed_results if r['relevance_scores']])
        
        improvement = (current_avg_relevance - 0.444) / 0.444 * 100
        print(f"   Текущая средняя релевантность: {current_avg_relevance:.3f}")
        print(f"   Улучшение: {improvement:+.1f}%")
    
    return success_level in ['excellent', 'good']

if __name__ == "__main__":
    success = test_quality_improvements()
    exit(0 if success else 1) 