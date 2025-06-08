#!/usr/bin/env python3
"""
Поиск правильных данных о штамме GW1-59T
"""
import sys
import re
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def find_correct_strain_data():
    """Ищет правильные данные о штамме GW1-59T"""
    
    print("🔍 ПОИСК ПРАВИЛЬНЫХ ДАННЫХ О ШТАММЕ GW1-59T")
    print("=" * 50)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        indexer = Indexer()
        
        # Различные поисковые запросы
        queries = [
            "GW1-59T",
            "GW1- 5 9T", 
            "Lysobacter antarcticus",
            "antarcticus GW1",
            "pH 9.0 11.0",
            "15-37°C Lysobacter",
            "Untersee lake Antarctica"
        ]
        
        all_results = {}
        
        for query in queries:
            print(f"\n🔍 Поиск: '{query}'")
            results = indexer.search(query, top_k=3)
            
            if results:
                print(f"   Найдено {len(results)} результатов")
                for i, result in enumerate(results, 1):
                    key = f"{query}_{i}"
                    all_results[key] = result
                    
                    print(f"   Результат {i}:")
                    print(f"      Релевантность: {result.get('relevance_score', 0):.3f}")
                    print(f"      Источник: {result['metadata'].get('source_pdf', 'неизвестно')}")
                    print(f"      Страница: {result['metadata'].get('page_number', 'неизвестно')}")
                    
                    # Показываем ключевые фрагменты
                    text = result['text']
                    if 'GW1' in text:
                        print(f"      ✅ Содержит GW1")
                    if 'pH' in text:
                        print(f"      ✅ Содержит pH данные")
                    if '°C' in text:
                        print(f"      ✅ Содержит температуру")
                    if 'antarcticus' in text.lower():
                        print(f"      ✅ Содержит antarcticus")
                    
                    print(f"      Фрагмент: {text[:150]}...")
            else:
                print(f"   ❌ Результаты не найдены")
        
        # Анализируем лучшие результаты
        print(f"\n📊 АНАЛИЗ ЛУЧШИХ РЕЗУЛЬТАТОВ:")
        
        # Сортируем по релевантности
        sorted_results = sorted(all_results.items(), 
                              key=lambda x: x[1].get('relevance_score', 0), 
                              reverse=True)
        
        print(f"\n🏆 ТОП-5 НАИБОЛЕЕ РЕЛЕВАНТНЫХ РЕЗУЛЬТАТОВ:")
        
        for i, (key, result) in enumerate(sorted_results[:5], 1):
            print(f"\n{i}. {key}")
            print(f"   Релевантность: {result.get('relevance_score', 0):.3f}")
            print(f"   Источник: {result['metadata'].get('source_pdf', 'неизвестно')}")
            print(f"   Содержимое: {result['text'][:300]}...")
            
            # Проверяем на наличие ключевых данных
            text = result['text']
            
            if 'GW1-59T' in text or 'GW1- 5 9T' in text:
                print(f"   ✅ СОДЕРЖИТ ШТАММ GW1-59T!")
                
                # Извлекаем данные
                
                # pH
                ph_match = re.search(r'pH\s*(\d+\.?\d*)[-–](\d+\.?\d*)', text)
                if ph_match:
                    print(f"   📊 pH: {ph_match.group(1)}–{ph_match.group(2)}")
                
                # Температура
                temp_match = re.search(r'(\d+)[-–](\d+)\s*°?C', text)
                if temp_match:
                    print(f"   🌡️ Температура: {temp_match.group(1)}–{temp_match.group(2)}°C")
                
                # Жирные кислоты
                fatty_matches = re.findall(r'C\s*(\d+):(\d+)', text)
                if fatty_matches:
                    fatty_acids = [f"C{m[0]}:{m[1]}" for m in fatty_matches]
                    print(f"   🧪 Жирные кислоты: {', '.join(fatty_acids)}")
                
                # Геном
                genome_match = re.search(r'(\d+\.?\d*)\s*(Mb|мб)', text, re.IGNORECASE)
                if genome_match:
                    print(f"   🧬 Геном: {genome_match.group(1)} Mb")
                
                # Место
                if 'озер' in text.lower() or 'lake' in text.lower():
                    print(f"   🌍 Место: Озеро (упоминается)")
                
                if 'антарктик' in text.lower() or 'antarct' in text.lower():
                    print(f"   🧊 Регион: Антарктика")
        
        # Проверяем, есть ли правильные данные
        print(f"\n🎯 ПОИСК ЭТАЛОННЫХ ДАННЫХ:")
        
        reference_checks = [
            ("pH 9.0–11.0", "pH.*9\.0.*11\.0"),
            ("15–37°C", "15.*37.*°?C"),
            ("Untersee", "Untersee"),
            ("2.8 Mb", "2\.8.*Mb"),
            ("C15:0", "C\s*15\s*:\s*0")
        ]
        
        found_references = 0
        
        for ref_desc, pattern in reference_checks:
            found = False
            for key, result in all_results.items():
                if re.search(pattern, result['text'], re.IGNORECASE):
                    found = True
                    print(f"   ✅ {ref_desc}: найдено в {key}")
                    print(f"      Источник: {result['metadata'].get('source_pdf', 'неизвестно')}")
                    break
            
            if not found:
                print(f"   ❌ {ref_desc}: НЕ НАЙДЕНО")
            else:
                found_references += 1
        
        coverage = int((found_references / len(reference_checks)) * 100)
        print(f"\n📊 ПОКРЫТИЕ ЭТАЛОННЫХ ДАННЫХ: {coverage}% ({found_references}/{len(reference_checks)})")
        
        if coverage < 50:
            print(f"\n⚠️ КРИТИЧЕСКАЯ ПРОБЛЕМА:")
            print(f"   • Эталонные данные о GW1-59T отсутствуют или плохо индексированы")
            print(f"   • Возможно, данные в других документах или повреждены при извлечении")
            print(f"   • Требуется проверка исходных PDF файлов")
        
        return coverage >= 50
        
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = find_correct_strain_data()
    
    if success:
        print(f"\n✅ Эталонные данные найдены!")
    else:
        print(f"\n❌ Эталонные данные НЕ найдены!")
        print(f"💡 Требуется:")
        print(f"   • Проверить исходные PDF")
        print(f"   • Улучшить извлечение данных")
        print(f"   • Переиндексировать с лучшим экстрактором")
    
    sys.exit(0 if success else 1) 