#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

from lysobacter_rag.indexer.indexer import Indexer

print("🔍 ПРОВЕРКА СТАТЬИ О CAPSICI")
print("=" * 40)

indexer = Indexer()

# Проверяем есть ли статья в базе
results = indexer.search('Lysobacter capsici sp. nov', top_k=10)
print(f'📊 Найдено результатов для "Lysobacter capsici sp. nov": {len(results)}')

capsici_sources = set()
for r in results:
    source = r['metadata'].get('source_pdf', 'N/A')
    capsici_sources.add(source)
    if 'capsici' in source.lower():
        print(f'✅ НАЙДЕНА СТАТЬЯ: {source}')
        print(f'   Релевантность: {r["relevance_score"]:.3f}')
        print(f'   Тип: {r["metadata"].get("chunk_type", "N/A")}')
        print(f'   Страница: {r["metadata"].get("page_number", "N/A")}')
        preview = r['text'][:200].replace('\n', ' ')
        print(f'   Содержание: {preview}...')
        print()

print(f'📚 Все источники: {list(capsici_sources)}')

# Проверяем конкретные характеристики
print(f'\n🎯 ПОИСК ХАРАКТЕРИСТИК ИЗ NOTEBOOKLM:')
print("-" * 40)

characteristics = [
    ("ризосфера перца", "rhizosphere of pepper"),
    ("15-37°C", "15-37 degrees"),
    ("размер клеток 0.3-0.5", "cell size 0.3-0.5"),
    ("G+C 65.4", "G+C content 65.4"),
    ("каталаза положительный", "catalase positive"),
    ("хитиназа", "chitinase")
]

for rus, eng in characteristics:
    # Ищем на русском
    results_rus = indexer.search(rus, top_k=3)
    # Ищем на английском
    results_eng = indexer.search(eng, top_k=3)
    
    found_capsici = False
    for results, lang in [(results_rus, "рус"), (results_eng, "eng")]:
        for r in results:
            if 'capsici' in r['metadata'].get('source_pdf', '').lower():
                print(f'✅ {rus} -> найдено в capsici статье ({lang})')
                found_capsici = True
                break
    
    if not found_capsici:
        print(f'❌ {rus} -> НЕ найдено в capsici статье')

# Финальная проверка - есть ли детальное описание YC5194
print(f'\n🔬 ПОИСК ДЕТАЛЬНОГО ОПИСАНИЯ YC5194:')
print("-" * 40)

detailed_search = indexer.search('YC5194 type strain isolated', top_k=5)
if detailed_search:
    for r in detailed_search:
        source = r['metadata'].get('source_pdf', 'N/A')
        if 'capsici' in source.lower():
            print(f'🎯 ДЕТАЛЬНОЕ ОПИСАНИЕ НАЙДЕНО: {source}')
            print(f'   Релевантность: {r["relevance_score"]:.3f}')
            preview = r['text'][:300]
            print(f'   Содержание: {preview}...')
        else:
            print(f'❌ Описание в другой статье: {source}')
else:
    print(f'❌ Детальное описание НЕ найдено') 