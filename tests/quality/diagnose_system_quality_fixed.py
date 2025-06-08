#!/usr/bin/env python3
"""
СИСТЕМНАЯ ДИАГНОСТИКА: Качество извлечения из всех PDF файлов
"""

import sys
import os
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from lysobacter_rag.indexer.indexer import Indexer
from config import config

print("🔍 СИСТЕМНАЯ ДИАГНОСТИКА КАЧЕСТВА ИЗВЛЕЧЕНИЯ")
print("=" * 60)

indexer = Indexer()
stats = indexer.get_collection_stats()

print(f"📊 ОБЩАЯ СТАТИСТИКА:")
print(f"   Всего чанков: {stats.get('total_chunks', 0)}")

# Получаем все источники
collection = indexer.chroma_client.get_collection(name=config.CHROMA_COLLECTION_NAME)
all_data = collection.get()
all_metadata = all_data['metadatas']
all_documents = all_data['documents']

print(f"   Получено метаданных: {len(all_metadata)}")

# Анализируем источники
sources = {}
total_text_length = 0
total_documents = len(all_documents)

for i, (metadata, document) in enumerate(zip(all_metadata, all_documents)):
    source = metadata.get('source_pdf', 'unknown')
    chunk_type = metadata.get('chunk_type', 'text')
    
    if source not in sources:
        sources[source] = {'text': 0, 'table': 0, 'total': 0, 'avg_length': 0, 'total_length': 0}
    
    sources[source][chunk_type] = sources[source].get(chunk_type, 0) + 1
    sources[source]['total'] += 1
    sources[source]['total_length'] += len(document) if document else 0
    
    total_text_length += len(document) if document else 0

# Вычисляем средние длины
for source_data in sources.values():
    if source_data['total'] > 0:
        source_data['avg_length'] = source_data['total_length'] // source_data['total']

print(f"   Средняя длина чанка: {total_text_length // total_documents if total_documents > 0 else 0} символов")

print(f"\n📚 АНАЛИЗ ПО ИСТОЧНИКАМ (топ-20):")
print("-" * 80)

# Сортируем по общему количеству чанков
sorted_sources = sorted(sources.items(), key=lambda x: x[1]['total'], reverse=True)

print(f"{'Файл':<35} {'Текст':<6} {'Таблицы':<8} {'Всего':<6} {'Ср.длина':<8}")
print("-" * 80)

problematic_sources = []
good_sources = []

for source, counts in sorted_sources[:20]:
    filename = source.replace('.pdf', '')[:30] + '...' if len(source) > 33 else source
    
    avg_len = counts['avg_length']
    total = counts['total']
    
    print(f"{filename:<35} {counts.get('text', 0):<6} {counts.get('table', 0):<8} {total:<6} {avg_len:<8}")
    
    # Выявляем проблемные источники
    if total < 3:  # Слишком мало чанков
        problematic_sources.append((source, "мало чанков"))
    elif avg_len < 50:  # Слишком короткие чанки
        problematic_sources.append((source, "короткие чанки"))
    elif avg_len > 2000:  # Слишком длинные чанки
        problematic_sources.append((source, "длинные чанки"))
    else:
        good_sources.append(source)

print(f"\n🎯 КЛАССИФИКАЦИЯ ИСТОЧНИКОВ:")
print("-" * 40)
print(f"✅ Хорошие источники: {len(good_sources)}")
print(f"⚠️ Проблемные источники: {len(problematic_sources)}")

if problematic_sources:
    print(f"\n❌ ПРОБЛЕМНЫЕ ИСТОЧНИКИ:")
    for source, issue in problematic_sources[:10]:
        filename = source.replace('.pdf', '')[:40]
        print(f"   - {filename}: {issue}")

# Анализ качества поиска по научным терминам
print(f"\n🧬 ТЕСТ ПОИСКА НАУЧНЫХ ТЕРМИНОВ:")
print("-" * 50)

scientific_terms = [
    "Lysobacter",
    "type strain", 
    "sp. nov.",
    "16S rRNA",
    "phylogenetic",
    "G+C content",
    "temperature range",
    "pH range",
    "catalase positive",
    "cell morphology"
]

search_quality = []

for term in scientific_terms:
    try:
        results = indexer.search(term, top_k=5)
        
        if results:
            avg_relevance = sum(r['relevance_score'] for r in results) / len(results)
            best_relevance = max(r['relevance_score'] for r in results)
            
            # Подсчитываем разнообразие источников
            unique_sources = set(r['metadata'].get('source_pdf', '') for r in results)
            
            search_quality.append({
                'term': term,
                'avg_relevance': avg_relevance,
                'best_relevance': best_relevance,
                'results_count': len(results),
                'unique_sources': len(unique_sources)
            })
            
            status = "✅" if avg_relevance > 0.4 else "⚠️" if avg_relevance > 0.2 else "❌"
            print(f"{status} {term:<18} - ср:{avg_relevance:.3f} макс:{best_relevance:.3f} источников:{len(unique_sources)}")
        else:
            print(f"❌ {term:<18} - НЕ НАЙДЕН")
            search_quality.append({
                'term': term,
                'avg_relevance': 0,
                'best_relevance': 0,
                'results_count': 0,
                'unique_sources': 0
            })
    except Exception as e:
        print(f"❌ {term:<18} - ОШИБКА: {e}")

# Общая оценка качества системы
avg_search_quality = sum(sq['avg_relevance'] for sq in search_quality) / len(search_quality)
terms_found = sum(1 for sq in search_quality if sq['results_count'] > 0)

print(f"\n📊 ОБЩАЯ ОЦЕНКА КАЧЕСТВА СИСТЕМЫ:")
print("-" * 40)
print(f"📈 Средняя релевантность поиска: {avg_search_quality:.3f}")
print(f"🎯 Найдено терминов: {terms_found}/{len(scientific_terms)} ({terms_found/len(scientific_terms)*100:.1f}%)")
print(f"📚 Всего источников: {len(sources)}")
print(f"⚠️ Проблемных источников: {len(problematic_sources)} ({len(problematic_sources)/len(sources)*100:.1f}%)")

# Рекомендации
print(f"\n💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
print("-" * 40)

if avg_search_quality < 0.3:
    print("🚨 КРИТИЧЕСКОЕ: Низкое качество поиска")
    print("   ➤ Требуется переиндексация с улучшенным экстрактором")
elif avg_search_quality < 0.5:
    print("⚠️ СЕРЬЕЗНО: Среднее качество поиска")
    print("   ➤ Улучшить извлечение текста и промпты")
else:
    print("✅ ХОРОШО: Приемлемое качество поиска")

if len(problematic_sources) > len(sources) * 0.3:
    print("📉 Много проблемных источников")
    print("   ➤ Оптимизировать настройки чанкинга")

# Конкретный план действий
print(f"\n🚀 ПЛАН ДЕЙСТВИЙ:")
print("1. Создать улучшенный PDF экстрактор с лучшей обработкой научных текстов")
print("2. Оптимизировать размер чанков (рекомендуемый: 300-600 символов)")
print("3. Добавить пост-обработку для исправления OCR ошибок")
print("4. Внедрить гибридный поиск (семантический + точное совпадение)")
print("5. Улучшить промпты RAG для синтеза информации из нескольких источников")

if problematic_sources:
    print(f"\n🎯 ПРИОРИТЕТНЫЕ ФАЙЛЫ ДЛЯ ПЕРЕИНДЕКСАЦИИ:")
    for source, issue in problematic_sources[:5]:
        print(f"   - {source}")

print(f"\n✅ ДИАГНОСТИКА ЗАВЕРШЕНА") 