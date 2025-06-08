#!/usr/bin/env python3
"""
ИСПРАВЛЕННАЯ версия теста со структурированными ответами
Фикс: правильное извлечение текста из источников
"""

import sys
import os
sys.path.append('src')

from src.lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
from src.lysobacter_rag.rag_pipeline.structured_strain_analyzer import StructuredStrainAnalyzer
from src.lysobacter_rag.indexer import Indexer
import json
from datetime import datetime

def test_fixed_strain_responses():
    """Тестирует ИСПРАВЛЕННУЮ систему с правильным извлечением контекста"""
    
    print("🛠️ Тестирование ИСПРАВЛЕННОЙ RAG системы")
    print("=" * 60)
    
    # Инициализация компонентов
    try:
        indexer = Indexer()
        strain_analyzer = StructuredStrainAnalyzer()
        print("✅ Индексер и анализатор штаммов инициализированы")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Тестовые вопросы
    test_questions = [
        {
            "question": "Какие характеристики штамма Lysobacter capsici YC5194?",
            "strain": "YC5194",
            "strain_full_name": "Lysobacter capsici YC5194",
            "search_terms": ["YC5194", "Lysobacter capsici", "capsici YC5194"]
        },
        {
            "question": "Что известно о штамме GW1-59T?",
            "strain": "GW1-59T",
            "strain_full_name": "GW1-59T",
            "search_terms": ["GW1-59T", "Lysobacter antarcticus", "antarcticus GW1"]
        }
    ]
    
    results = {}
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n🔬 ИСПРАВЛЕННЫЙ тест {i}: {test_case['strain']}")
        print("-" * 50)
        print(f"Вопрос: {test_case['question']}")
        
        try:
            # Шаг 1: Прямой поиск с множественными запросами
            all_chunks = []
            for search_term in test_case['search_terms']:
                print(f"  🔍 Ищу: '{search_term}'")
                chunks = indexer.search(search_term, top_k=8)
                all_chunks.extend(chunks)
            
            # Удаляем дубликаты по ID
            unique_chunks = {}
            for chunk in all_chunks:
                chunk_id = chunk.get('id', str(hash(chunk.get('text', ''))))
                if chunk_id not in unique_chunks:
                    unique_chunks[chunk_id] = chunk
            
            final_chunks = list(unique_chunks.values())
            print(f"  📊 Найдено уникальных чанков: {len(final_chunks)}")
            
            # Шаг 2: ПРАВИЛЬНОЕ извлечение контекста
            context_parts = []
            for chunk in final_chunks:
                # Извлекаем текст из правильного поля
                text = chunk.get('text', '')  # Основное поле с полным текстом
                if text:
                    context_parts.append(text)
                    print(f"    ✅ Добавлен чанк: {len(text)} символов")
                else:
                    print(f"    ❌ Пустой чанк: {list(chunk.keys())}")
            
            context = "\n\n".join(context_parts)
            print(f"  📄 Общий контекст: {len(context)} символов")
            
            # Шаг 3: Структурированный анализ
            if context.strip():
                print(f"  🔬 Анализирую штамм {test_case['strain_full_name']}")
                
                strain_characteristics = strain_analyzer.analyze_strain_from_context(
                    context, test_case['strain_full_name']
                )
                
                # Шаг 4: Форматируем ответ
                structured_answer = strain_analyzer.format_structured_response(strain_characteristics)
                
                print(f"\n📝 ИСПРАВЛЕННЫЙ структурированный ответ:")
                print(structured_answer)
                
                print(f"\n📈 Метрики качества:")
                filled_categories = _count_filled_categories(strain_characteristics)
                print(f"- Заполнено категорий: {filled_categories}/8 ({filled_categories/8*100:.1f}%)")
                print(f"- Уверенность анализатора: {strain_characteristics.confidence_score:.3f}")
                print(f"- Использовано чанков: {len(final_chunks)}")
                
                # Детальная разбивка по категориям
                print(f"\n📋 Детализация по категориям:")
                categories = [
                    ("🏷️ Классификация", strain_characteristics.classification),
                    ("📍 Происхождение", strain_characteristics.origin),
                    ("🔬 Морфология", strain_characteristics.morphology),
                    ("🌡️ Условия роста", strain_characteristics.growth_conditions),
                    ("⚗️ Биохимия", strain_characteristics.biochemical_properties),
                    ("🧪 Хемотаксономия", strain_characteristics.chemotaxonomy),
                    ("🧬 Геномика", strain_characteristics.genomics),
                    ("🦠 Активность", strain_characteristics.biological_activity)
                ]
                
                for name, data in categories:
                    status = "✅" if data else "❌"
                    count = len(data) if data else 0
                    print(f"  {status} {name}: {count} параметров")
                
                # Сохраняем результат
                results[test_case['strain']] = {
                    "question": test_case['question'],
                    "structured_answer": structured_answer,
                    "context_length": len(context),
                    "structure_confidence": strain_characteristics.confidence_score,
                    "chunks_count": len(final_chunks),
                    "categories_filled": filled_categories,
                    "strain_characteristics": {
                        "classification": strain_characteristics.classification,
                        "origin": strain_characteristics.origin,
                        "morphology": strain_characteristics.morphology,
                        "growth_conditions": strain_characteristics.growth_conditions,
                        "biochemical": strain_characteristics.biochemical_properties,
                        "chemotaxonomy": strain_characteristics.chemotaxonomy,
                        "genomics": strain_characteristics.genomics,
                        "biological_activity": strain_characteristics.biological_activity,
                        "unique_features": strain_characteristics.unique_features
                    }
                }
            else:
                print(f"\n❌ Контекст все еще пуст после исправления")
                results[test_case['strain']] = {
                    "question": test_case['question'],
                    "error": "Пустой контекст после исправления",
                    "chunks_count": len(final_chunks)
                }
                
        except Exception as e:
            print(f"❌ Ошибка при обработке: {e}")
            import traceback
            traceback.print_exc()
            results[test_case['strain']] = {
                "question": test_case['question'],
                "error": str(e)
            }
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/quality/fixed_strain_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {results_file}")
    
    # Итоговая оценка
    print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА ИСПРАВЛЕНИЙ")
    print("=" * 50)
    
    total_score = 0
    for strain, result in results.items():
        if 'error' not in result:
            categories_percent = (result.get('categories_filled', 0) / 8) * 100
            confidence = result.get('structure_confidence', 0) * 100
            
            score = (categories_percent + confidence) / 2
            total_score += score
            
            print(f"\n🔬 {strain}:")
            print(f"   📊 Категории: {result.get('categories_filled', 0)}/8 ({categories_percent:.1f}%)")
            print(f"   🎯 Уверенность: {confidence:.1f}%")
            print(f"   📈 Общий балл: {score:.1f}/100")
            
            if score >= 70:
                print(f"   🏆 ОТЛИЧНЫЙ результат!")
            elif score >= 50:
                print(f"   ✅ Хороший результат")
            elif score >= 30:
                print(f"   ⚠️ Удовлетворительно")
            else:
                print(f"   ❌ Нужны улучшения")
    
    avg_score = total_score / len([r for r in results.values() if 'error' not in r]) if results else 0
    print(f"\n🏁 СРЕДНИЙ БАЛЛ СИСТЕМЫ: {avg_score:.1f}/100")
    
    return results

def _count_filled_categories(characteristics) -> int:
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
    
    return sum(1 for cat in categories if cat)

def compare_with_notebooklm():
    """Сравнение с эталонными ответами NotebookLM"""
    print(f"\n📊 СРАВНЕНИЕ С NOTEBOOKLM")
    print("-" * 30)
    print("🎯 ЦЕЛИ:")
    print("- YC5194: 95%+ покрытие тем (было 0%)")
    print("- GW1-59T: 95%+ покрытие тем (было 66.7%)")
    print("- Структурированность: Четкие категории")
    print("- Детальность: Конкретные данные vs общие фразы")

if __name__ == "__main__":
    results = test_fixed_strain_responses()
    compare_with_notebooklm() 