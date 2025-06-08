#!/usr/bin/env python3
"""
ПРОСТОЙ ТЕСТ: Умный чанкинг без продвинутого экстрактора
"""

import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lysobacter_rag.pdf_extractor.scientific_chunker import ScientificTextChunker

def test_simple_chunking():
    """Простой тест умного чанкера"""
    
    print("🧬 ПРОСТОЙ ТЕСТ УМНОГО ЧАНКЕРА")
    print("=" * 50)
    
    # Тестовый научный текст (как в статье о YC5194)
    test_text = """
    Lysobacter capsici sp. nov. is a gram-negative, aerobic bacterium isolated from the rhizosphere 
    of pepper plants in South Korea. The type strain YC5194T was isolated from soil samples 
    collected in agricultural fields. Cells are rod-shaped, measuring 0.3-0.5 × 2.0-20 μm, 
    and are motile by means of a polar flagellum.
    
    The temperature range for growth is 15-37°C, with optimal growth at 28°C. The pH range 
    for growth is 5.5-8.5, with optimal growth at pH 7.0. The strain grows on nutrient agar, 
    tryptic soy agar, and Luria-Bertani agar. The strain is catalase-positive and oxidase-positive.
    
    The G+C content of the genomic DNA is 65.4 mol%. 16S rRNA gene sequence analysis showed 
    the highest similarity to Lysobacter gummosus LMG 18383T with 97.8% sequence identity. 
    Phylogenetic analysis based on 16S rRNA gene sequences placed the strain in the genus Lysobacter.
    
    The strain shows antimicrobial activity against various plant pathogens including 
    Fusarium oxysporum and Pythium ultimum. Based on the phenotypic, chemotaxonomic, 
    and phylogenetic characteristics, strain YC5194T represents a novel species of 
    the genus Lysobacter, for which the name Lysobacter capsici sp. nov. is proposed.
    """
    
    # Создаем элементы для чанкера
    test_elements = [
        {
            'content': test_text,
            'element_type': 'text',
            'page_number': 1,
            'confidence': 0.9,
            'metadata': {
                'extraction_method': 'test',
                'source': 'test_article.pdf'
            }
        }
    ]
    
    print(f"📝 Исходный текст: {len(test_text)} символов")
    
    # Инициализируем чанкер
    chunker = ScientificTextChunker(target_chunk_size=300, overlap=50)
    
    # Применяем чанкинг
    print("\n🚀 Применяю умный чанкинг...")
    
    try:
        chunks = chunker.chunk_extracted_elements(test_elements)
        
        print(f"✅ Создано {len(chunks)} чанков")
        
        # Анализируем результаты
        total_length = sum(len(chunk['content']) for chunk in chunks)
        avg_length = total_length / len(chunks) if chunks else 0
        
        print(f"\n📊 Результаты:")
        print(f"   Общая длина: {total_length} символов")
        print(f"   Средняя длина чанка: {avg_length:.0f} символов")
        print(f"   Целевой размер: 300 символов")
        
        # Показываем чанки
        print(f"\n🔍 Созданные чанки:")
        
        for i, chunk in enumerate(chunks, 1):
            content = chunk['content']
            metadata = chunk['metadata']
            
            importance = metadata.get('scientific_importance', 'unknown')
            key_terms = metadata.get('key_terms', [])
            chunk_type = metadata.get('chunk_type', 'unknown')
            
            print(f"\n   📝 Чанк {i}:")
            print(f"      Тип: {chunk_type}")
            print(f"      Важность: {importance}")
            print(f"      Длина: {len(content)} символов")
            print(f"      Ключевые термины: {', '.join(key_terms[:5]) if key_terms else 'нет'}")
            print(f"      Текст: {content[:100]}...")
        
        # Проверяем качество
        print(f"\n🎯 Оценка качества:")
        
        # Проверяем размеры
        sizes_ok = all(200 <= len(c['content']) <= 450 for c in chunks)
        print(f"   Размеры чанков: {'✅' if sizes_ok else '❌'}")
        
        # Проверяем важность
        important_chunks = [c for c in chunks 
                           if c['metadata'].get('scientific_importance') in ['high', 'critical']]
        importance_ok = len(important_chunks) > 0
        print(f"   Важные чанки найдены: {'✅' if importance_ok else '❌'} ({len(important_chunks)})")
        
        # Проверяем ключевые термины
        all_terms = []
        for c in chunks:
            all_terms.extend(c['metadata'].get('key_terms', []))
        
        scientific_terms = [t for t in all_terms 
                           if any(sci in t.lower() for sci in ['lysobacter', 'strain', 'ph', '°c'])]
        terms_ok = len(scientific_terms) >= 5
        print(f"   Научные термины: {'✅' if terms_ok else '❌'} ({len(scientific_terms)})")
        
        # Общая оценка
        if sizes_ok and importance_ok and terms_ok:
            print(f"\n🏆 ТЕСТ ПРОЙДЕН: Умный чанкинг работает отлично!")
            return True
        else:
            print(f"\n⚠️ ТЕСТ ЧАСТИЧНО ПРОЙДЕН: Есть проблемы для исправления")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА при чанкинге: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_chunking()
    exit(0 if success else 1) 