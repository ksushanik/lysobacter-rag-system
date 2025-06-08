#!/usr/bin/env python3
"""
СИСТЕМНАЯ ДИАГНОСТИКА: Качество извлечения из всех PDF файлов
"""

import sys
import os
from pathlib import Path
import random

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.indexer.indexer import Indexer

print("🔍 СИСТЕМНАЯ ДИАГНОСТИКА КАЧЕСТВА ИЗВЛЕЧЕНИЯ")
print("=" * 60)

indexer = Indexer()
stats = indexer.get_collection_stats()

print(f"📊 ОБЩАЯ СТАТИСТИКА:")
print(f"   Всего чанков: {stats.get('total_chunks', 0)}")
print(f"   Текстовых: {stats.get('text_chunks', 0)}")
print(f"   Табличных: {stats.get('table_chunks', 0)}")

# Получаем все источники
from config import config
collection = indexer.chroma_client.get_collection(name=config.CHROMA_COLLECTION_NAME)
all_metadata = collection.get()['metadatas']

sources = {}
for metadata in all_metadata:
    source = metadata.get('source_pdf', 'unknown')
    chunk_type = metadata.get('chunk_type', 'unknown')
    
    if source not in sources:
        sources[source] = {'text': 0, 'table': 0, 'total': 0}
    
    sources[source][chunk_type] = sources[source].get(chunk_type, 0) + 1
    sources[source]['total'] += 1

print(f"\n📚 АНАЛИЗ ПО ИСТОЧНИКАМ:")
print("-" * 50)

# Сортируем по общему количеству чанков
sorted_sources = sorted(sources.items(), key=lambda x: x[1]['total'], reverse=True)

print(f"{'Файл':<40} {'Текст':<8} {'Таблицы':<8} {'Всего':<8}")
print("-" * 70)

text_heavy = []
table_heavy = []
balanced = []
low_content = []

for source, counts in sorted_sources:
    filename = source.replace('.pdf', '')[:35] + '...' if len(source) > 38 else source
    
    print(f"{filename:<40} {counts.get('text', 0):<8} {counts.get('table', 0):<8} {counts['total']:<8}")
    
    # Классифицируем источники
    text_ratio = counts.get('text', 0) / counts['total']
    table_ratio = counts.get('table', 0) / counts['total']
    
    if counts['total'] < 5:
        low_content.append(source)
    elif text_ratio > 0.8:
        text_heavy.append(source)
    elif table_ratio > 0.8:
        table_heavy.append(source)
    else:
        balanced.append(source)

print(f"\n🎯 КЛАССИФИКАЦИЯ ИСТОЧНИКОВ:")
print("-" * 40)
print(f"📄 Текстовые (>80% текста): {len(text_heavy)}")
print(f"📊 Табличные (>80% таблиц): {len(table_heavy)}")
print(f"⚖️ Сбалансированные: {len(balanced)}")
print(f"⚠️ Мало содержания (<5 чанков): {len(low_content)}")

# Анализ качества текста
print(f"\n🔍 АНАЛИЗ КАЧЕСТВА ТЕКСТА:")
print("-" * 40)

# Берем случайные образцы текста
sample_queries = [
    "temperature range growth",
    "cell size morphology",
    "pH range tolerance", 
    "G+C content DNA",
    "catalase oxidase positive",
    "type strain isolated"
]

quality_issues = []

for query in sample_queries:
    results = indexer.search(query, top_k=5)
    
    print(f"\n🔍 Запрос: '{query}'")
    
    for i, result in enumerate(results[:3], 1):
        text = result['text']
        source = result['metadata'].get('source_pdf', 'N/A')
        
        # Проверяем качество текста
        issues = []
        
        # Разорванные слова
        if ' - ' in text and any(char.isalnum() for char in text.split(' - ')[0][-1:]):
            issues.append("разорванные слова")
        
        # Слитные числа/единицы
        if any(pattern in text for pattern in ['°C', 'mM', 'pH']):
            if any(f" {unit}" in text for unit in ['C', 'M']):
                issues.append("разорванные единицы")
        
        # OCR ошибки
        if any(char in text for char in ['§', '¶', '±', '¿']):
            issues.append("OCR артефакты")
        
        # Короткие чанки (мало информации)
        if len(text) < 100:
            issues.append("короткий чанк")
        
        # Качество релевантности
        relevance = result['relevance_score']
        if relevance < 0.3:
            issues.append("низкая релевантность")
        
        if issues:
            quality_issues.append({
                'source': source,
                'query': query,
                'issues': issues,
                'relevance': relevance,
                'text_preview': text[:100]
            })
        
        status = "❌" if issues else "✅"
        issues_str = ", ".join(issues) if issues else "OK"
        print(f"   {i}. {source[:25]}... - {relevance:.3f} {status} {issues_str}")

# Специфические проблемы научных текстов
print(f"\n🧬 ДИАГНОСТИКА НАУЧНЫХ ТЕРМИНОВ:")
print("-" * 40)

scientific_terms = [
    ("Lysobacter", "название рода"),
    ("sp. nov.", "новый вид"),
    ("type strain", "типовой штамм"),
    ("16S rRNA", "генетический маркер"),
    ("phylogenetic", "филогения"),
    ("G+C content", "содержание ГЦ"),
    ("°C", "температура"),
    ("pH", "кислотность")
]

for term, description in scientific_terms:
    results = indexer.search(term, top_k=3)
    
    if results:
        avg_relevance = sum(r['relevance_score'] for r in results) / len(results)
        status = "✅" if avg_relevance > 0.4 else "⚠️" if avg_relevance > 0.2 else "❌"
        print(f"{status} {term:<15} ({description:<20}) - ср. релевантность: {avg_relevance:.3f}")
    else:
        print(f"❌ {term:<15} ({description:<20}) - НЕ НАЙДЕН")

# Финальные рекомендации
print(f"\n💡 СИСТЕМНЫЕ РЕКОМЕНДАЦИИ:")
print("-" * 40)

total_issues = len(quality_issues)
total_samples = len(sample_queries) * 3

if total_issues > total_samples * 0.5:
    print("🚨 КРИТИЧЕСКОЕ: Более 50% образцов имеют проблемы качества")
    print("   Рекомендация: ПОЛНАЯ ПЕРЕИНДЕКСАЦИЯ с улучшенным экстрактором")
elif total_issues > total_samples * 0.3:
    print("⚠️ СЕРЬЕЗНО: 30-50% образцов имеют проблемы")
    print("   Рекомендация: Переиндексация проблемных источников")
else:
    print("✅ ПРИЕМЛЕМО: Менее 30% проблем")
    print("   Рекомендация: Точечные улучшения")

if len(low_content) > len(sorted_sources) * 0.2:
    print(f"📉 ПРОБЛЕМА: {len(low_content)} источников с малым содержанием")
    print("   Рекомендация: Проверить настройки чанкинга")

print(f"\n📈 ПЛАН УЛУЧШЕНИЙ:")
print("1. Улучшить продвинутый экстрактор PDF")
print("2. Оптимизировать размер и перекрытие чанков")
print("3. Добавить пост-обработку извлеченного текста")
print("4. Внедрить гибридный поиск (семантический + ключевые слова)")
print("5. Улучшить промпты для синтеза информации")

print(f"\n🎯 ПРОБЛЕМНЫЕ ИСТОЧНИКИ ДЛЯ ПРИОРИТЕТНОЙ ПЕРЕИНДЕКСАЦИИ:")
for issue in quality_issues[:10]:  # Топ-10 проблем
    print(f"   - {issue['source']}: {', '.join(issue['issues'])}") 