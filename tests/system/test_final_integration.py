#!/usr/bin/env python3
"""
Финальный тест интеграции всех улучшений в RAG систему
"""

import sys
from pathlib import Path
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

def test_final_integration():
    """Финальный тест всех компонентов"""
    
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ ИНТЕГРАЦИИ ВСЕХ УЛУЧШЕНИЙ")
    print("=" * 60)
    print("📊 Тестируем работу с продвинутым экстрактором")
    print("🧠 Проверяем качество RAG системы")
    print("📈 Оцениваем готовность к NotebookLM конкуренции")
    print()
    
    success_count = 0
    total_tests = 6
    
    # Тест 1: Продвинутый экстрактор
    print("🧪 ТЕСТ 1: Продвинутый PDF экстрактор")
    print("-" * 40)
    try:
        from config import config
        from lysobacter_rag.pdf_extractor.advanced_pdf_extractor import AdvancedPDFExtractor
        
        if config.USE_ENHANCED_EXTRACTOR:
            extractor = AdvancedPDFExtractor()
            print("✅ Продвинутый экстрактор инициализирован")
            print("✅ Конфигурация: USE_ENHANCED_EXTRACTOR = True")
            success_count += 1
        else:
            print("⚠️ Продвинутый экстрактор отключен в конфигурации")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: База данных с табличными данными
    print(f"\n🧪 ТЕСТ 2: База данных с продвинутыми данными")
    print("-" * 40)
    try:
        from lysobacter_rag.indexer.indexer import Indexer
        indexer = Indexer()
        stats = indexer.get_collection_stats()
        
        total_chunks = stats.get('total_chunks', 0)
        chunk_types = stats.get('chunk_types', {})
        table_chunks = chunk_types.get('table', 0)
        
        print(f"📊 Всего чанков: {total_chunks}")
        print(f"📋 Табличных чанков: {table_chunks}")
        
        if total_chunks > 0 and table_chunks > 0:
            print("✅ База содержит табличные данные!")
            success_count += 1
        elif total_chunks > 0:
            print("⚠️ База есть, но мало табличных данных")
        else:
            print("❌ База данных пуста")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: Качество поиска
    print(f"\n🧪 ТЕСТ 3: Качество поиска по таблицам")
    print("-" * 40)
    try:
        test_query = "strain characteristics table morphology"
        results = indexer.search(test_query, top_k=5)
        
        if results:
            table_results = [r for r in results if r['metadata'].get('chunk_type') == 'table']
            avg_relevance = sum(r.get('relevance_score', 0) for r in results) / len(results)
            
            print(f"📝 Найдено результатов: {len(results)}")
            print(f"📊 Табличных результатов: {len(table_results)}")
            print(f"🎯 Средняя релевантность: {avg_relevance:.3f}")
            
            if len(table_results) > 0 and avg_relevance > 0.4:
                print("✅ Поиск по таблицам работает отлично!")
                success_count += 1
            elif avg_relevance > 0.3:
                print("⚠️ Поиск работает, но можно улучшить")
            else:
                print("❌ Низкое качество поиска")
        else:
            print("❌ Поиск не возвращает результатов")
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
    
    # Тест 4: RAG пайплайн с улучшениями
    print(f"\n🧪 ТЕСТ 4: RAG пайплайн с табличными данными")
    print("-" * 40)
    try:
        from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
        rag = RAGPipeline()
        
        # Тестируем специальный метод для поиска в таблицах
        if hasattr(rag, 'search_tables_only'):
            table_result = rag.search_tables_only("strain characteristics", top_k=3)
            tables_found = table_result.get('num_tables_found', 0)
            
            print(f"📊 Специальный поиск по таблицам: {tables_found} таблиц")
            
            if tables_found > 0:
                print("✅ Поиск только по таблицам работает!")
                success_count += 1
            else:
                print("⚠️ Таблицы не найдены в специальном поиске")
        else:
            print("⚠️ Метод search_tables_only недоступен")
    except Exception as e:
        print(f"❌ Ошибка RAG: {e}")
    
    # Тест 5: Улучшение качества текста
    print(f"\n🧪 ТЕСТ 5: Улучшения качества текста")
    print("-" * 40)
    try:
        from lysobacter_rag.pdf_extractor.text_quality_improver import text_quality_improver
        
        # Тестируем различные проблемы
        test_cases = [
            ("growthofstrain PB-6250", "рост штамма"),
            ("temperaturerange15-42°C", "температурный диапазон"),
            ("Lysobactercapsici", "название вида"),
            ("pH7.0optimum", "pH оптимум")
        ]
        
        improved_count = 0
        for original, description in test_cases:
            improved = text_quality_improver.improve_text_quality(original)
            if improved != original:
                print(f"✅ {description}: {original} → {improved}")
                improved_count += 1
            else:
                print(f"⚠️ {description}: без изменений")
        
        if improved_count >= 2:
            print("✅ Улучшения качества текста работают!")
            success_count += 1
        else:
            print("⚠️ Улучшения качества работают частично")
    except Exception as e:
        print(f"❌ Ошибка улучшений: {e}")
    
    # Тест 6: Готовность к конкуренции с NotebookLM
    print(f"\n🧪 ТЕСТ 6: Готовность к конкуренции с NotebookLM")
    print("-" * 40)
    try:
        # Критические запросы из наших тестов
        critical_queries = [
            "YC5194 temperature growth conditions",
            "strain biochemical characteristics table"
        ]
        
        notebooklm_ready = 0
        
        for query in critical_queries:
            results = indexer.search(query, top_k=3)
            if results:
                best_relevance = max(r.get('relevance_score', 0) for r in results)
                has_tables = any(r['metadata'].get('chunk_type') == 'table' for r in results)
                
                print(f"📝 '{query}': релевантность {best_relevance:.3f}, таблицы: {has_tables}")
                
                if best_relevance > 0.45 and has_tables:
                    notebooklm_ready += 1
        
        readiness_percent = (notebooklm_ready / len(critical_queries)) * 100
        
        if readiness_percent >= 75:
            print("🎉 Готовность к конкуренции с NotebookLM: ОТЛИЧНО!")
            success_count += 1
        elif readiness_percent >= 50:
            print("✅ Готовность к конкуренции с NotebookLM: ХОРОШО")
            success_count += 1
        else:
            print("⚠️ Требуется дополнительная работа для конкуренции с NotebookLM")
    except Exception as e:
        print(f"❌ Ошибка тестирования готовности: {e}")
    
    # Общий результат
    print(f"\n🏆 ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 30)
    
    success_rate = (success_count / total_tests) * 100
    print(f"📊 Успешных тестов: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 ПРЕВОСХОДНО! Все улучшения интегрированы!")
        print("✅ Система готова к продакшену")
        print("🚀 Можно конкурировать с NotebookLM")
        status = "excellent"
    elif success_rate >= 75:
        print("✅ ОТЛИЧНО! Основные улучшения работают")
        print("🎯 Система значительно улучшена")
        print("📈 Качество приближается к NotebookLM")
        status = "good"
    elif success_rate >= 50:
        print("⚠️ ХОРОШО! Есть улучшения, но нужна доработка")
        print("🔧 Основа заложена, требуется настройка")
        status = "fair"
    else:
        print("❌ ТРЕБУЕТСЯ РАБОТА")
        print("🔧 Много компонентов нуждаются в исправлении")
        status = "poor"
    
    print(f"\n🎯 КЛЮЧЕВЫЕ ДОСТИЖЕНИЯ:")
    if 'advanced_extractor' in locals():
        print("✅ Продвинутый PDF экстрактор (pymupdf4llm + pdfplumber + tabula)")
    if table_chunks > 0:
        print(f"✅ Извлечение таблиц: {table_chunks} табличных чанков")
    if success_count >= 3:
        print("✅ Улучшенное качество поиска")
    if success_count >= 4:
        print("✅ Интеграция в RAG пайплайн")
    
    return status, success_rate

if __name__ == "__main__":
    test_final_integration() 