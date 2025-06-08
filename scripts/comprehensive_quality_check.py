#!/usr/bin/env python3
"""
Комплексная проверка качества данных для всех штаммов лизобактерий
"""
import sys
import re
from pathlib import Path
from collections import defaultdict
import json

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def comprehensive_quality_check():
    """Комплексная проверка качества всех данных"""
    
    print("🔍 КОМПЛЕКСНАЯ ПРОВЕРКА КАЧЕСТВА ДАННЫХ")
    print("=" * 60)
    
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        
        # Инициализируем индексер
        indexer = Indexer()
        
        # Получаем статистику базы
        stats = indexer.get_collection_stats()
        total_chunks = stats.get('total_chunks', 0)
        
        print(f"📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего чанков: {total_chunks}")
        print(f"   Типы чанков: {stats.get('chunk_types', {})}")
        print(f"   Источников: {stats.get('unique_sources', 0)}")
        
        # Список общих поисковых терминов для тестирования качества
        test_queries = [
            "temperature growth", "pH range", "NaCl tolerance", 
            "genome size", "G+C content", "oxidase", "catalase",
            "fatty acids", "quinones", "Antarctic", "soil",
            "marine", "alkaline", "sp. nov", "type strain"
        ]
        
        print(f"\n🧪 ТЕСТИРОВАНИЕ КАЧЕСТВА ПО КАТЕГОРИЯМ:")
        
        quality_issues = defaultdict(int)
        total_results = 0
        problematic_chunks = []
        
        for query in test_queries:
            print(f"\n📝 Категория: '{query}'")
            results = indexer.search(query, top_k=10)
            
            if results:
                print(f"   ✅ Найдено {len(results)} результатов")
                total_results += len(results)
                
                # Анализируем качество каждого результата
                for i, result in enumerate(results[:5], 1):  # Проверяем топ-5
                    text = result['text']
                    issues = analyze_text_quality(text)
                    
                    if issues:
                        problematic_chunks.append({
                            'query': query,
                            'rank': i,
                            'text_preview': text[:100] + "...",
                            'issues': issues,
                            'relevance': result.get('relevance_score', 0)
                        })
                        
                        for issue_type, count in issues.items():
                            quality_issues[issue_type] += count
                    
                    # Показываем краткий анализ
                    if issues:
                        issue_summary = ", ".join([f"{k}:{v}" for k, v in issues.items()])
                        print(f"      {i}. ⚠️ Проблемы: {issue_summary}")
                    else:
                        print(f"      {i}. ✅ Качество OK")
            else:
                print(f"   ❌ Результатов не найдено")
        
        # Общий анализ качества
        print(f"\n📊 ОБЩИЙ АНАЛИЗ КАЧЕСТВА:")
        print(f"   Проверено результатов: {total_results}")
        print(f"   Проблемных чанков: {len(problematic_chunks)}")
        
        if quality_issues:
            print(f"\n⚠️ НАЙДЕННЫЕ ПРОБЛЕМЫ:")
            for issue_type, count in sorted(quality_issues.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {issue_type}: {count} случаев")
        
        # Анализ специфических научных терминов
        print(f"\n🧬 ПРОВЕРКА НАУЧНЫХ ТЕРМИНОВ:")
        scientific_terms = [
            "Lysobacter", "sp. nov", "type strain", "16S rRNA",
            "DNA-DNA hybridization", "phylogenetic", "chemotaxonomic",
            "phenotypic", "genotypic", "taxonomy"
        ]
        
        scientific_quality = {}
        for term in scientific_terms:
            results = indexer.search(term, top_k=5)
            if results:
                # Проверяем корректность термина в контексте
                correct_usage = 0
                for result in results:
                    if check_scientific_term_usage(result['text'], term):
                        correct_usage += 1
                
                accuracy = (correct_usage / len(results)) * 100
                scientific_quality[term] = accuracy
                status = "✅" if accuracy > 80 else "⚠️" if accuracy > 50 else "❌"
                print(f"   {status} {term}: {accuracy:.0f}% корректность")
        
        # Проверка штаммовых номеров
        print(f"\n🧪 ПРОВЕРКА ШТАММОВЫХ НОМЕРОВ:")
        strain_patterns = [
            r'\w+\d+-\d+T',  # Основной паттерн типа GW1-59T
            r'\w+\s+\d+T',   # Паттерн типа KCTC 12131T
            r'DSM\s+\d+',    # Deutsche Sammlung von Mikroorganismen
            r'ATCC\s+\d+'    # American Type Culture Collection
        ]
        
        strain_issues = check_strain_nomenclature(indexer)
        
        for pattern_name, issues in strain_issues.items():
            if issues > 0:
                print(f"   ⚠️ {pattern_name}: {issues} проблем")
            else:
                print(f"   ✅ {pattern_name}: корректно")
        
        # Проверка числовых данных
        print(f"\n🔢 ПРОВЕРКА ЧИСЛОВЫХ ДАННЫХ:")
        numerical_quality = check_numerical_data_quality(indexer)
        
        for data_type, quality_score in numerical_quality.items():
            status = "✅" if quality_score > 0.8 else "⚠️" if quality_score > 0.5 else "❌"
            print(f"   {status} {data_type}: {quality_score:.1%}")
        
        # Итоговый скор качества
        overall_quality = calculate_overall_quality_score(
            quality_issues, total_results, scientific_quality, 
            strain_issues, numerical_quality
        )
        
        print(f"\n📈 ИТОГОВАЯ ОЦЕНКА КАЧЕСТВА:")
        print(f"   🎯 Общий скор: {overall_quality:.0f}/100")
        
        if overall_quality >= 80:
            print("   🎉 ОТЛИЧНОЕ КАЧЕСТВО!")
            status = "excellent"
        elif overall_quality >= 60:
            print("   ✅ ХОРОШЕЕ КАЧЕСТВО")
            status = "good"
        elif overall_quality >= 40:
            print("   ⚠️ СРЕДНЕЕ КАЧЕСТВО - нужны улучшения")
            status = "medium"
        else:
            print("   🚨 НИЗКОЕ КАЧЕСТВО - требуется переиндексация!")
            status = "poor"
        
        # Рекомендации по улучшению
        print(f"\n💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        recommendations = generate_improvement_recommendations(
            quality_issues, scientific_quality, strain_issues, numerical_quality
        )
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Сохраняем отчет
        save_quality_report({
            'overall_quality': overall_quality,
            'status': status,
            'total_chunks': total_chunks,
            'quality_issues': dict(quality_issues),
            'scientific_quality': scientific_quality,
            'strain_issues': dict(strain_issues),
            'numerical_quality': numerical_quality,
            'recommendations': recommendations,
            'problematic_chunks': problematic_chunks[:10]  # Топ-10 проблемных
        })
        
        return status != "poor"
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def analyze_text_quality(text):
    """Анализирует качество извлеченного текста"""
    issues = {}
    
    # Разорванные штаммовые номера
    broken_strains = len(re.findall(r'\w+\s*-\s*\d+\s+\w*T', text))
    if broken_strains > 0:
        issues['разорванные_штаммы'] = broken_strains
    
    # Разорванные химические формулы
    broken_formulas = len(re.findall(r'C\s+\d+\s*:\s*\d+', text))
    if broken_formulas > 0:
        issues['разорванные_формулы'] = broken_formulas
    
    # Слитные слова (длиннее 50 символов)
    long_words = [w for w in text.split() if len(w) > 50]
    if long_words:
        issues['слитные_слова'] = len(long_words)
    
    # Поврежденные числа
    broken_numbers = len(re.findall(r'\d+\s+\.\s+\d+', text))
    if broken_numbers > 0:
        issues['поврежденные_числа'] = broken_numbers
    
    # Некорректные единицы измерения
    broken_units = len(re.findall(r'\d+\s+°\s+C|\d+\s+%\s+\w+', text))
    if broken_units > 0:
        issues['разорванные_единицы'] = broken_units
    
    return issues

def check_scientific_term_usage(text, term):
    """Проверяет корректность использования научного термина"""
    
    # Простая эвристика для проверки контекста
    term_lower = term.lower()
    text_lower = text.lower()
    
    if term_lower not in text_lower:
        return False
    
    # Специфические проверки
    if term == "sp. nov":
        # Должно быть в контексте названия вида
        return bool(re.search(r'\w+\s+\w+\s+sp\.\s+nov', text, re.IGNORECASE))
    
    elif term == "type strain":
        # Должно быть с штаммовым номером
        return bool(re.search(r'type\s+strain.*[A-Z]+\d+', text, re.IGNORECASE))
    
    elif term == "16S rRNA":
        # Должно быть в контексте генетического анализа
        return any(keyword in text_lower for keyword in [
            'sequence', 'gene', 'phylogen', 'analysis', 'similarity'
        ])
    
    return True  # Базовое присутствие термина

def check_strain_nomenclature(indexer):
    """Проверяет качество номенклатуры штаммов"""
    
    issues = defaultdict(int)
    
    # Поиск штаммов с потенциальными проблемами
    strain_results = indexer.search("strain type T", top_k=20)
    
    for result in strain_results:
        text = result['text']
        
        # Ищем разорванные штаммовые номера
        broken_patterns = [
            r'\w+\s*-\s*\d+\s+T',  # GW1- 59T
            r'\w+\d+\s*-\s*\d+\s+T',  # KCTC 12131- T
        ]
        
        for pattern in broken_patterns:
            matches = re.findall(pattern, text)
            if matches:
                issues['разорванные_номера'] += len(matches)
        
        # Ищем некорректные форматы
        if re.search(r'[a-z]+\d+[a-z]+', text):  # Слитные обозначения
            issues['слитные_номера'] += 1
    
    return issues

def check_numerical_data_quality(indexer):
    """Проверяет качество числовых данных"""
    
    quality_scores = {}
    
    # Температурные данные
    temp_results = indexer.search("temperature °C growth", top_k=10)
    temp_quality = 0
    if temp_results:
        correct_temp = sum(1 for r in temp_results 
                          if re.search(r'\d+[-–]\d+°C', r['text']))
        temp_quality = correct_temp / len(temp_results)
    quality_scores['температура'] = temp_quality
    
    # pH данные
    ph_results = indexer.search("pH range growth", top_k=10)
    ph_quality = 0
    if ph_results:
        correct_ph = sum(1 for r in ph_results 
                        if re.search(r'pH\s+\d+\.?\d*[-–]\d+\.?\d*', r['text']))
        ph_quality = correct_ph / len(ph_results)
    quality_scores['pH'] = ph_quality
    
    # Размер генома
    genome_results = indexer.search("genome size Mb", top_k=10)
    genome_quality = 0
    if genome_results:
        correct_genome = sum(1 for r in genome_results 
                           if re.search(r'\d+\.?\d*\s*Mb', r['text']))
        genome_quality = correct_genome / len(genome_results)
    quality_scores['геном'] = genome_quality
    
    return quality_scores

def calculate_overall_quality_score(quality_issues, total_results, 
                                  scientific_quality, strain_issues, numerical_quality):
    """Вычисляет общий скор качества"""
    
    # Базовый скор (отсутствие проблем извлечения)
    if total_results > 0:
        extraction_score = max(0, 100 - (sum(quality_issues.values()) / total_results * 100))
    else:
        extraction_score = 0
    
    # Научная корректность
    science_score = sum(scientific_quality.values()) / len(scientific_quality) if scientific_quality else 0
    
    # Качество штаммовых номеров
    strain_score = max(0, 100 - sum(strain_issues.values()) * 5)
    
    # Качество числовых данных
    numerical_score = sum(numerical_quality.values()) / len(numerical_quality) * 100 if numerical_quality else 0
    
    # Взвешенный итоговый скор
    overall_score = (
        extraction_score * 0.4 +  # 40% - качество извлечения
        science_score * 0.3 +     # 30% - научная корректность
        strain_score * 0.2 +      # 20% - штаммовые номера
        numerical_score * 0.1     # 10% - числовые данные
    )
    
    return max(0, min(100, overall_score))

def generate_improvement_recommendations(quality_issues, scientific_quality, 
                                       strain_issues, numerical_quality):
    """Генерирует рекомендации по улучшению"""
    
    recommendations = []
    
    # Рекомендации по проблемам извлечения
    if quality_issues:
        top_issue = max(quality_issues.items(), key=lambda x: x[1])
        if top_issue[1] > 5:
            recommendations.append(f"🔧 Приоритет: исправить {top_issue[0]} ({top_issue[1]} случаев)")
    
    # Рекомендации по научным терминам
    low_science_terms = [term for term, score in scientific_quality.items() if score < 60]
    if low_science_terms:
        recommendations.append(f"📚 Улучшить обработку терминов: {', '.join(low_science_terms[:3])}")
    
    # Рекомендации по штаммам
    if sum(strain_issues.values()) > 3:
        recommendations.append("🧪 Добавить специальную обработку штаммовых номеров")
    
    # Рекомендации по числовым данным
    low_numerical = [data for data, score in numerical_quality.items() if score < 0.6]
    if low_numerical:
        recommendations.append(f"🔢 Улучшить извлечение числовых данных: {', '.join(low_numerical)}")
    
    # Общие рекомендации
    if not recommendations:
        recommendations.append("✅ Качество хорошее, мелкие улучшения по необходимости")
    else:
        recommendations.append("🚀 Рекомендуется переиндексация с улучшенным экстрактором")
    
    return recommendations

def save_quality_report(report):
    """Сохраняет отчет о качестве"""
    
    report_path = Path("quality_report.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен: {report_path}")

if __name__ == "__main__":
    success = comprehensive_quality_check()
    
    if not success:
        print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Запустите 'make fix-extraction' для исправления")
        print("2. Проверьте логи на предмет конкретных ошибок")
        print("3. При необходимости настройте дополнительные правила")
    
    sys.exit(0 if success else 1) 