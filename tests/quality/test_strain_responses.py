#!/usr/bin/env python3
"""
Тестирование качества ответов RAG системы для штаммов
Сравнение с эталонными ответами NotebookLM
"""

import sys
import os
sys.path.append('src')

from src.lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
import json
from datetime import datetime

def test_strain_questions():
    """Тестирует ответы системы на ключевые вопросы о штаммах"""
    
    print("🧪 Тестирование качества ответов RAG системы")
    print("=" * 60)
    
    # Инициализация RAG системы
    try:
        rag = EnhancedRAGPipeline()
        print("✅ RAG система инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Тестовые вопросы
    test_questions = [
        {
            "question": "Какие характеристики штамма Lysobacter capsici YC5194?",
            "strain": "YC5194",
            "expected_topics": [
                "происхождение из ризосферы перца",
                "морфологические характеристики",
                "условия роста",
                "биохимические свойства",
                "противогрибковая активность",
                "чувствительность к антибиотикам"
            ]
        },
        {
            "question": "Что известно о штамме GW1-59T?",
            "strain": "GW1-59T", 
            "expected_topics": [
                "Lysobacter antarcticus sp. nov.",
                "изоляция из Антарктиды",
                "морфология",
                "температурные условия",
                "геномные характеристики",
                "биохимические свойства"
            ]
        }
    ]
    
    results = {}
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n🔍 Тест {i}: {test_case['strain']}")
        print("-" * 40)
        print(f"Вопрос: {test_case['question']}")
        
        try:
            # Получаем ответ от системы
            result = rag.ask_question(
                query=test_case['question'],
                top_k=10
            )
            
            # Преобразуем в формат для анализа
            response = {
                'answer': result.answer,
                'chunks': [{'metadata': source} for source in result.sources],
                'relevance_score': result.confidence
            }
            
            print(f"\n📝 Ответ системы:")
            print(response['answer'])
            
            print(f"\n📊 Метаданные:")
            print(f"- Найдено чанков: {len(response.get('chunks', []))}")
            print(f"- Релевантность: {response.get('relevance_score', 'N/A')}")
            
            # Сохраняем результат
            results[test_case['strain']] = {
                "question": test_case['question'],
                "answer": response['answer'],
                "chunks_count": len(response.get('chunks', [])),
                "relevance": response.get('relevance_score'),
                "expected_topics": test_case['expected_topics'],
                "sources": [chunk.get('metadata', {}).get('source', 'Unknown') 
                          for chunk in response.get('chunks', [])]
            }
            
        except Exception as e:
            print(f"❌ Ошибка при обработке вопроса: {e}")
            results[test_case['strain']] = {
                "question": test_case['question'],
                "error": str(e)
            }
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/quality/strain_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {results_file}")
    
    return results

def analyze_coverage(our_answer: str, expected_topics: list) -> dict:
    """Анализирует покрытие ожидаемых тем в ответе"""
    
    coverage = {}
    our_answer_lower = our_answer.lower()
    
    for topic in expected_topics:
        # Простая проверка наличия ключевых слов
        topic_words = topic.lower().split()
        found_words = sum(1 for word in topic_words if word in our_answer_lower)
        coverage_percent = (found_words / len(topic_words)) * 100 if topic_words else 0
        
        coverage[topic] = {
            "covered": coverage_percent > 50,  # Если найдено больше 50% слов темы
            "coverage_percent": coverage_percent,
            "found_words": found_words,
            "total_words": len(topic_words)
        }
    
    return coverage

def compare_with_notebooklm():
    """Сравнивает результаты с эталонными ответами NotebookLM"""
    
    print("\n📊 Анализ качества ответов")
    print("=" * 60)
    
    # Запускаем тесты
    results = test_strain_questions()
    
    if not results:
        print("❌ Нет результатов для анализа")
        return
    
    analysis = {}
    
    for strain, result in results.items():
        if 'error' in result:
            print(f"\n❌ {strain}: Ошибка - {result['error']}")
            continue
            
        print(f"\n🔬 Анализ для штамма {strain}")
        print("-" * 30)
        
        # Анализируем покрытие тем
        coverage = analyze_coverage(result['answer'], result['expected_topics'])
        
        covered_topics = sum(1 for topic_data in coverage.values() if topic_data['covered'])
        total_topics = len(coverage)
        coverage_percentage = (covered_topics / total_topics) * 100 if total_topics > 0 else 0
        
        print(f"📈 Покрытие тем: {covered_topics}/{total_topics} ({coverage_percentage:.1f}%)")
        
        for topic, data in coverage.items():
            status = "✅" if data['covered'] else "❌"
            print(f"  {status} {topic} ({data['coverage_percent']:.0f}%)")
        
        analysis[strain] = {
            "coverage_percentage": coverage_percentage,
            "covered_topics": covered_topics,
            "total_topics": total_topics,
            "coverage_details": coverage,
            "chunks_used": result['chunks_count'],
            "sources": result['sources']
        }
    
    # Общие рекомендации
    print(f"\n💡 Рекомендации по улучшению:")
    print("-" * 30)
    
    avg_coverage = sum(a['coverage_percentage'] for a in analysis.values()) / len(analysis) if analysis else 0
    
    if avg_coverage < 70:
        print("🔧 Низкое покрытие тем - нужно улучшение извлечения информации")
    if avg_coverage < 50:
        print("⚠️  КРИТИЧНО: Система упускает большинство важных характеристик")
    
    return analysis

if __name__ == "__main__":
    results = compare_with_notebooklm() 