#!/usr/bin/env python3
"""
Диагностика проблем с штаммом GW1-59T
"""

import sys
import os
# Добавляем пути для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lysobacter_rag.rag_pipeline import RAGPipeline
from src.lysobacter_rag.rag_pipeline.structured_strain_analyzer import StructuredStrainAnalyzer

def main():
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМ С GW1-59T")
    print("=" * 50)
    
    # Инициализация системы
    rag = RAGPipeline()
    analyzer = StructuredStrainAnalyzer()
    
    # Тестовый запрос
    question = "Что известно о штамме GW1-59T?"
    print(f"📋 Вопрос: {question}")
    
    # Получаем ответ системы
    response = rag.ask_question(question)
    print(f"\n📄 Ответ системы:")
    print(f"Уверенность: {response.get('confidence_score', 'N/A')}")
    print(f"Длина ответа: {len(response.get('answer', ''))}")
    
    # Анализируем структурированные данные
    analysis = analyzer.analyze_strain_from_context(response.get('answer', ''), 'GW1-59T')
    
    print(f"\n🔬 СТРУКТУРИРОВАННЫЙ АНАЛИЗ:")
    print(f"Общая уверенность: {analysis.confidence_score:.2f}")
    print(f"Штамм: {analysis.strain_name}")
    
    print(f"\n📊 КАТЕГОРИИ (заполненность):")
    categories = {
        "Классификация": analysis.classification,
        "Происхождение": analysis.origin,
        "Морфология": analysis.morphology,
        "Условия роста": analysis.growth_conditions,
        "Биохимия": analysis.biochemical_properties,
        "Хемотаксономия": analysis.chemotaxonomy,
        "Геномика": analysis.genomics,
        "Биоактивность": analysis.biological_activity
    }
    
    filled_count = 0
    for category, value in categories.items():
        # Проверяем тип данных - может быть строка или словарь
        if isinstance(value, dict):
            filled = bool(value)  # Словарь считается заполненным если не пуст
            content_length = len(str(value))
        elif isinstance(value, str):
            filled = bool(value and value.strip())
            content_length = len(value) if value else 0
        else:
            filled = bool(value)
            content_length = len(str(value)) if value else 0
            
        status = "✅" if filled else "❌"
        print(f"   {status} {category}: {content_length} символов")
        if filled:
            filled_count += 1
    
    print(f"\n📈 ЗАПОЛНЕННЫЕ КАТЕГОРИИ: {filled_count}/8 ({filled_count/8*100:.1f}%)")
    
    # Анализируем источники
    sources = response.get('sources', [])
    print(f"\n📚 ИСТОЧНИКИ: {len(sources)} документов")
    for i, source in enumerate(sources[:5]):  # Показываем первые 5
        print(f"   {i+1}. {source}")
    
    # Показываем сам ответ для ручного анализа
    print(f"\n📝 ПОЛНЫЙ ОТВЕТ:")
    print("-" * 50)
    print(response.get('answer', 'Ответ отсутствует'))
    
    return analysis

if __name__ == "__main__":
    main() 