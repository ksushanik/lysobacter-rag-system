#!/usr/bin/env python3
"""
Тест качества ответов с примененными улучшениями
"""
import sys
import re
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_enhanced_rag_quality():
    """Тестирует качество ответов RAG с улучшениями"""
    
    print("🧪 ТЕСТ КАЧЕСТВА ОТВЕТОВ С УЛУЧШЕНИЯМИ")
    print("=" * 50)
    
    try:
        from config import config
        from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
        
        # Инициализируем RAG pipeline
        print("🔧 Инициализация RAG pipeline...")
        pipeline = RAGPipeline()
        
        # Ключевой тестовый вопрос о штамме GW1-59T
        test_question = "Расскажи подробно о штамме GW1-59T: температура роста, pH, жирные кислоты, где найден, размер генома"
        
        print(f"\n❓ ТЕСТОВЫЙ ВОПРОС:")
        print(f"   {test_question}")
        
        # Генерируем ответ
        print(f"\n🤖 Генерация ответа...")
        response = pipeline.ask_question(test_question)
        
        if not response:
            print("❌ Ответ не получен")
            return False
        
        answer = response.get('answer', '')
        sources = response.get('sources', [])
        
        print(f"\n📝 ПОЛУЧЕННЫЙ ОТВЕТ:")
        print(f"{'='*60}")
        print(answer)
        print(f"{'='*60}")
        
        print(f"\n📚 Источники: {len(sources)} документов")
        
        # Анализ качества ответа
        print(f"\n🔍 АНАЛИЗ КАЧЕСТВА:")
        
        quality_checks = [
            ("GW1-59T", "Правильное название штамма", "GW1- 5 9T" not in answer and "GW1-59T" in answer),
            ("Температура", "Диапазон температур указан", re.search(r'\d+[-–]\d+°?C', answer)),
            ("pH", "Диапазон pH указан", re.search(r'pH\s*\d+\.?\d*[-–]\d+\.?\d*', answer)),
            ("Жирные кислоты", "Упоминание жирных кислот", re.search(r'C\d+:\d+', answer) or 'жирн' in answer.lower()),
            ("Местонахождение", "Указано место находки", 'антарктик' in answer.lower() or 'озер' in answer.lower()),
            ("Геном", "Размер генома указан", re.search(r'\d+\.?\d*\s*(Mb|мб)', answer.lower())),
            ("Таксономия", "Полное научное название", 'Lysobacter antarcticus' in answer),
            ("Детальность", "Достаточно подробный ответ", len(answer) > 500)
        ]
        
        passed_checks = 0
        total_checks = len(quality_checks)
        
        for criterion, description, check_result in quality_checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {criterion}: {description}")
            if check_result:
                passed_checks += 1
        
        # Подсчет общего качества
        quality_score = int((passed_checks / total_checks) * 100)
        
        print(f"\n📊 ОБЩАЯ ОЦЕНКА КАЧЕСТВА: {quality_score}/100")
        print(f"   Пройдено проверок: {passed_checks}/{total_checks}")
        
        # Сравнение с предыдущими результатами
        print(f"\n📈 СРАВНЕНИЕ С ЭТАЛОНАМИ:")
        print(f"   • NotebookLM (эталон):    95/100")
        print(f"   • Chat.minimax:           90/100")
        print(f"   • Текущая система:        {quality_score}/100")
        print(f"   • Предыдущий результат:   70/100")
        
        improvement = quality_score - 70
        if improvement > 0:
            print(f"   🎉 УЛУЧШЕНИЕ: +{improvement} баллов!")
        elif improvement == 0:
            print(f"   ⚪ Качество на том же уровне")
        else:
            print(f"   ⚠️ Качество снизилось на {abs(improvement)} баллов")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ:")
        
        if quality_score < 85:
            if not any(check[2] for check in quality_checks if "GW1-59T" in check[0]):
                print(f"   • Улучшить индексацию штамма GW1-59T")
            if not any(check[2] for check in quality_checks if "Температура" in check[0]):
                print(f"   • Добавить больше данных о температуре")
            if not any(check[2] for check in quality_checks if "pH" in check[0]):
                print(f"   • Улучшить извлечение данных о pH")
            if not any(check[2] for check in quality_checks if "Детальность" in check[0]):
                print(f"   • Увеличить длину и детальность ответов")
        else:
            print(f"   ✅ Система показывает отличные результаты!")
        
        # Детальный анализ проблемных моментов
        if "GW1- 5 9T" in answer:
            print(f"\n⚠️ НАЙДЕНЫ ПРОБЛЕМЫ КАЧЕСТВА:")
            print(f"   • Разорванный номер штамма: 'GW1- 5 9T'")
            print(f"   • Требуется дополнительная обработка данных")
        
        # Тест поиска релевантной информации
        print(f"\n🔍 ТЕСТ ПОИСКА РЕЛЕВАНТНОЙ ИНФОРМАЦИИ:")
        
        search_queries = [
            "GW1-59T",
            "Lysobacter antarcticus", 
            "температура роста 15-37",
            "pH 9.0-11.0"
        ]
        
        for query in search_queries:
            relevant_sources = [s for s in sources if query.lower().replace('-', ' ') in s.lower()]
            status = "✅" if relevant_sources else "❌"
            print(f"   {status} Поиск '{query}': {len(relevant_sources)} релевантных источников")
        
        return quality_score >= 75  # Хороший результат 75+
        
    except Exception as e:
        print(f"❌ ОШИБКА ТЕСТИРОВАНИЯ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def compare_before_after():
    """Сравнивает результаты до и после улучшений"""
    
    print(f"\n📊 ДЕТАЛЬНОЕ СРАВНЕНИЕ РЕЗУЛЬТАТОВ:")
    print(f"{'='*70}")
    
    comparison_data = [
        ("Система", "Качество", "Сильные стороны", "Слабые стороны"),
        ("NotebookLM", "95/100", "Полные данные, точность", "Не наша система"),
        ("Chat.minimax", "90/100", "Структура, практичность", "Ограниченный доступ"),
        ("Текущая система", "?/100", "Наши улучшения", "Тестируется сейчас"),
        ("Предыдущая система", "70/100", "Базовая функциональность", "Проблемы качества данных"),
        ("DeepSeek R1", "60/100", "Экономичность", "Неполные ответы")
    ]
    
    for row in comparison_data:
        print(f"{row[0]:<20} {row[1]:<10} {row[2]:<25} {row[3]}")
    
    print(f"{'='*70}")

if __name__ == "__main__":
    print("🎯 ТЕСТ КАЧЕСТВА УЛУЧШЕННОЙ СИСТЕМЫ")
    print("=" * 60)
    
    # Сравнение систем
    compare_before_after()
    
    # Основной тест
    success = test_enhanced_rag_quality()
    
    if success:
        print(f"\n🎉 ТЕСТ ПРОЙДЕН!")
        print(f"✅ Система качества работает")
        print(f"💡 Рекомендации:")
        print(f"   • Протестируйте разные вопросы")
        print(f"   • Сравните с другими системами")
        print(f"   • При необходимости добавьте правила")
    else:
        print(f"\n⚠️ ТЕСТ НЕ ПРОЙДЕН")
        print(f"💡 Что делать:")
        print(f"   • Проверьте настройки RAG pipeline")
        print(f"   • Убедитесь в правильности модели")
        print(f"   • Проверьте качество данных")
    
    sys.exit(0 if success else 1) 