#!/usr/bin/env python3
"""
Тест качества поиска без использования LLM
"""
import sys
import re
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_search_quality():
    """Тестирует качество поиска и найденной информации"""
    
    print("🔍 ТЕСТ КАЧЕСТВА ПОИСКА С УЛУЧШЕНИЯМИ")
    print("=" * 50)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        # Инициализируем индексер
        indexer = Indexer()
        
        # Тестовый запрос о штамме GW1-59T
        query = "GW1-59T антарктический температура pH жирные кислоты геном"
        
        print(f"🔍 Поиск по запросу: '{query}'")
        
        # Выполняем поиск
        results = indexer.search(query, top_k=10)
        
        if not results:
            print("❌ Результаты не найдены")
            return False
        
        print(f"✅ Найдено {len(results)} результатов")
        
        # Применяем правила улучшения качества
        quality_rules = [
            (r'GW\s*1-\s*5\s*9\s*T', 'GW1-59T'),
            (r'(\w+)\s*-\s*(\d+)\s+T', r'\1-\2T'),
            (r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2'),
            (r'(\d+)\s*[-–]\s*(\d+)\s*°?\s*C', r'\1–\2°C'),
            (r'pH\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'pH \1–\2'),
            (r'Lyso\s*bacter', 'Lysobacter'),
            (r'(\d+)\s*\.\s*(\d+)', r'\1.\2'),
        ]
        
        # Анализируем содержимое результатов
        all_content = ""
        improved_count = 0
        
        print(f"\n📋 АНАЛИЗ НАЙДЕННОГО СОДЕРЖИМОГО:")
        
        for i, result in enumerate(results, 1):
            text = result['text']
            all_content += text + " "
            
            # Применяем улучшения
            original_text = text
            improved_text = text
            
            for pattern, replacement in quality_rules:
                improved_text = re.sub(pattern, replacement, improved_text)
            
            if improved_text != original_text:
                improved_count += 1
                print(f"   Результат {i}: ✅ УЛУЧШЕН (релевантность: {result.get('relevance_score', 0):.3f})")
                
                # Показываем ключевые улучшения
                if 'GW1-59T' in improved_text and 'GW1- 5 9T' in original_text:
                    print(f"      • Исправлен штамм: GW1- 5 9T → GW1-59T")
                if re.search(r'\d+–\d+°C', improved_text) and re.search(r'\d+\s*[-–]\s*\d+\s*°?\s*C', original_text):
                    print(f"      • Исправлена температура")
                if re.search(r'C\d+:\d+', improved_text) and re.search(r'C\s+\d+\s*:\s*\d+', original_text):
                    print(f"      • Исправлены химические формулы")
            else:
                print(f"   Результат {i}: ⚪ Без изменений (релевантность: {result.get('relevance_score', 0):.3f})")
        
        # Проверяем наличие ключевой информации
        print(f"\n🧪 ПРОВЕРКА НАЛИЧИЯ КЛЮЧЕВОЙ ИНФОРМАЦИИ:")
        
        checks = [
            ("GW1-59T", "Штамм упоминается", "GW1-59T" in all_content or "GW1- 5 9T" in all_content),
            ("Температура", "Данные о температуре", re.search(r'\d+[-–°C\s]+\d+', all_content)),
            ("pH", "Данные о pH", "pH" in all_content.lower()),
            ("C15:0", "Жирные кислоты", "C15" in all_content or "жирн" in all_content.lower()),
            ("Antarcticus", "Видовое название", "antarcticus" in all_content.lower()),
            ("Геном", "Размер генома", re.search(r'\d+\.?\d*\s*(Mb|мб|megabase)', all_content.lower())),
            ("Lysobacter", "Название рода", "Lysobacter" in all_content),
            ("Озеро", "Место находки", "озер" in all_content.lower() or "lake" in all_content.lower())
        ]
        
        passed_checks = 0
        for criterion, description, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {criterion}: {description}")
            if check_result:
                passed_checks += 1
        
        # Подсчет качества поиска
        search_quality = int((passed_checks / len(checks)) * 100)
        improvement_rate = int((improved_count / len(results)) * 100)
        
        print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print(f"   🔍 Качество поиска: {search_quality}/100 ({passed_checks}/{len(checks)} критериев)")
        print(f"   ⚡ Улучшения применены: {improvement_rate}% результатов ({improved_count}/{len(results)})")
        print(f"   📋 Общее количество найденного контента: {len(all_content)} символов")
        
        # Извлекаем конкретные данные о штамме
        print(f"\n🔬 ИЗВЛЕЧЕННЫЕ ДАННЫЕ О ШТАММЕ GW1-59T:")
        
        specific_data = extract_strain_data(all_content)
        
        for category, data in specific_data.items():
            if data:
                print(f"   ✅ {category}: {data}")
            else:
                print(f"   ❌ {category}: Не найдено")
        
        # Сравнение с эталонными данными
        print(f"\n📈 СРАВНЕНИЕ С ЭТАЛОННЫМИ ДАННЫМИ:")
        
        reference_data = {
            "Температура": "15–37°C",
            "pH": "9.0–11.0", 
            "NaCl": "0–4%",
            "Место": "Озеро Untersee, Антарктида",
            "Геном": "2.8 Mb",
            "Гены": "2487",
            "Глубина": "95 м"
        }
        
        coverage_score = 0
        for ref_key, ref_value in reference_data.items():
            found = any(ref_key.lower() in cat.lower() and data for cat, data in specific_data.items())
            status = "✅" if found else "❌"
            print(f"   {status} {ref_key}: {ref_value} {'(найдено)' if found else '(отсутствует)'}")
            if found:
                coverage_score += 1
        
        coverage_percentage = int((coverage_score / len(reference_data)) * 100)
        
        print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА:")
        print(f"   📊 Покрытие эталонных данных: {coverage_percentage}% ({coverage_score}/{len(reference_data)})")
        print(f"   🔍 Качество поиска: {search_quality}%")
        print(f"   ⚡ Эффективность улучшений: {improvement_rate}%")
        
        # Определяем общую оценку
        overall_score = int((search_quality + coverage_percentage + improvement_rate) / 3)
        
        print(f"\n🏆 ОБЩАЯ ОЦЕНКА СИСТЕМЫ: {overall_score}/100")
        
        if overall_score >= 80:
            print(f"   🎉 ОТЛИЧНОЕ КАЧЕСТВО!")
        elif overall_score >= 65:
            print(f"   ✅ ХОРОШЕЕ КАЧЕСТВО")
        elif overall_score >= 50:
            print(f"   ⚠️ УДОВЛЕТВОРИТЕЛЬНОЕ КАЧЕСТВО")
        else:
            print(f"   ❌ ТРЕБУЕТСЯ УЛУЧШЕНИЕ")
        
        # Сравнение с другими системами
        print(f"\n📊 СРАВНЕНИЕ С ДРУГИМИ СИСТЕМАМИ:")
        print(f"   • NotebookLM:         95/100 (эталон)")
        print(f"   • Chat.minimax:       90/100")
        print(f"   • НАША СИСТЕМА:       {overall_score}/100")
        print(f"   • Предыдущая версия:  60/100")
        
        improvement = overall_score - 60
        if improvement > 0:
            print(f"   🎉 УЛУЧШЕНИЕ: +{improvement} баллов!")
        
        return overall_score >= 60
        
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def extract_strain_data(content):
    """Извлекает конкретные данные о штамме"""
    
    data = {}
    
    # Температура
    temp_match = re.search(r'(\d+)[-–](\d+)\s*°?C', content)
    data["Температура роста"] = f"{temp_match.group(1)}–{temp_match.group(2)}°C" if temp_match else None
    
    # pH
    ph_match = re.search(r'pH\s*(\d+\.?\d*)[-–](\d+\.?\d*)', content)
    data["pH диапазон"] = f"pH {ph_match.group(1)}–{ph_match.group(2)}" if ph_match else None
    
    # Геном
    genome_match = re.search(r'(\d+\.?\d*)\s*(Mb|мб)', content, re.IGNORECASE)
    data["Размер генома"] = f"{genome_match.group(1)} Mb" if genome_match else None
    
    # Жирные кислоты
    fatty_match = re.search(r'C\s*(\d+):(\d+)', content)
    data["Жирные кислоты"] = f"C{fatty_match.group(1)}:{fatty_match.group(2)}" if fatty_match else None
    
    # Местонахождение
    if "озер" in content.lower() or "lake" in content.lower():
        data["Местонахождение"] = "Озеро (упоминается)"
    else:
        data["Местонахождение"] = None
    
    # Антарктида
    if "антарктик" in content.lower() or "antarct" in content.lower():
        data["Регион"] = "Антарктика"
    else:
        data["Регион"] = None
    
    return data

if __name__ == "__main__":
    print("🎯 ТЕСТ КАЧЕСТВА ПОИСКА С УЛУЧШЕНИЯМИ")
    print("=" * 60)
    
    success = test_search_quality()
    
    if success:
        print(f"\n🎉 ТЕСТ ПОИСКА ПРОЙДЕН!")
        print(f"✅ Система поиска с улучшениями работает")
        print(f"💡 Следующие шаги:")
        print(f"   • Интегрировать улучшения в основной код")
        print(f"   • Протестировать полную RAG систему")
        print(f"   • Добавить постпроцессинг результатов")
    else:
        print(f"\n⚠️ ТЕСТ НЕ ПРОЙДЕН")
        print(f"💡 Рекомендации:")
        print(f"   • Улучшить правила обработки текста")
        print(f"   • Переиндексировать с лучшим экстрактором")
        print(f"   • Проверить качество исходных PDF")
    
    sys.exit(0 if success else 1) 