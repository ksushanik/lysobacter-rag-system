#!/usr/bin/env python3
"""
Тест улучшенной RAG системы со структурированными ответами о штаммах
"""

import sys
import os
sys.path.append('src')

from src.lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
from src.lysobacter_rag.rag_pipeline.structured_strain_analyzer import StructuredStrainAnalyzer
import json
from datetime import datetime

def test_improved_strain_responses():
    """Тестирует улучшенную систему со структурированными ответами"""
    
    print("🚀 Тестирование УЛУЧШЕННОЙ RAG системы со структурированными ответами")
    print("=" * 80)
    
    # Инициализация компонентов
    try:
        rag = EnhancedRAGPipeline(use_notebooklm_style=True)
        strain_analyzer = StructuredStrainAnalyzer()
        print("✅ Улучшенная RAG система и анализатор штаммов инициализированы")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Тестовые вопросы
    test_questions = [
        {
            "question": "Какие характеристики штамма Lysobacter capsici YC5194?",
            "strain": "YC5194",
            "strain_full_name": "Lysobacter capsici YC5194"
        },
        {
            "question": "Что известно о штамме GW1-59T?",
            "strain": "GW1-59T",
            "strain_full_name": "GW1-59T"
        }
    ]
    
    results = {}
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n🔬 УЛУЧШЕННЫЙ тест {i}: {test_case['strain']}")
        print("-" * 50)
        print(f"Вопрос: {test_case['question']}")
        
        try:
            # Шаг 1: Получаем базовый ответ от RAG системы
            rag_result = rag.ask_question(
                query=test_case['question'],
                top_k=15,  # Больше чанков для лучшего покрытия
                use_notebooklm_style=True
            )
            
            print(f"\n📊 Базовые метаданные:")
            print(f"- Найдено источников: {rag_result.num_sources_used}")
            print(f"- Уверенность RAG: {rag_result.confidence:.3f}")
            
            # Шаг 2: Создаем контекст из найденных источников
            context_parts = []
            for source in rag_result.sources:
                if 'content' in source:
                    context_parts.append(source['content'])
                elif 'text' in source:
                    context_parts.append(source['text'])
            
            context = "\n\n".join(context_parts)
            
            # Шаг 3: Применяем структурированный анализ
            if context.strip():
                strain_characteristics = strain_analyzer.analyze_strain_from_context(
                    context, test_case['strain_full_name']
                )
                
                # Шаг 4: Форматируем структурированный ответ
                structured_answer = strain_analyzer.format_structured_response(strain_characteristics)
                
                print(f"\n📝 УЛУЧШЕННЫЙ структурированный ответ:")
                print(structured_answer)
                
                print(f"\n📈 Анализ структурированности:")
                print(f"- Уверенность анализатора: {strain_characteristics.confidence_score:.3f}")
                print(f"- Извлечено категорий: {_count_filled_categories(strain_characteristics)}/8")
                
                # Сохраняем результат
                results[test_case['strain']] = {
                    "question": test_case['question'],
                    "original_answer": rag_result.answer,
                    "structured_answer": structured_answer,
                    "rag_confidence": rag_result.confidence,
                    "structure_confidence": strain_characteristics.confidence_score,
                    "sources_count": rag_result.num_sources_used,
                    "categories_filled": _count_filled_categories(strain_characteristics),
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
                print(f"\n❌ Контекст пуст - не удалось извлечь информацию")
                results[test_case['strain']] = {
                    "question": test_case['question'],
                    "error": "Пустой контекст",
                    "rag_confidence": rag_result.confidence,
                    "sources_count": rag_result.num_sources_used
                }
                
        except Exception as e:
            print(f"❌ Ошибка при обработке вопроса: {e}")
            results[test_case['strain']] = {
                "question": test_case['question'],
                "error": str(e)
            }
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/quality/improved_strain_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {results_file}")
    
    # Анализ улучшений
    print(f"\n📊 СРАВНЕНИЕ С ПРЕДЫДУЩИМИ РЕЗУЛЬТАТАМИ")
    print("=" * 50)
    
    for strain, result in results.items():
        if 'error' not in result:
            print(f"\n🔬 {strain}:")
            print(f"   📈 Категории заполнены: {result.get('categories_filled', 0)}/8")
            print(f"   🎯 Уверенность структуры: {result.get('structure_confidence', 0):.3f}")
            print(f"   📊 Уверенность RAG: {result.get('rag_confidence', 0):.3f}")
            print(f"   📚 Использовано источников: {result.get('sources_count', 0)}")
    
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

def compare_with_previous_results():
    """Сравнивает с предыдущими результатами"""
    print(f"\n💡 ПЛАН ДАЛЬНЕЙШИХ УЛУЧШЕНИЙ:")
    print("-" * 40)
    print("1. 🔍 Если YC5194 все еще провал - диагностировать поиск")
    print("2. 📋 Добавить специфические промпты для каждой категории")
    print("3. 🎯 Улучшить извлечение конкретных данных")
    print("4. 🧪 Добавить кросс-валидацию между источниками")
    print("5. 📊 Создать систему оценки качества ответов")

if __name__ == "__main__":
    results = test_improved_strain_responses()
    compare_with_previous_results() 