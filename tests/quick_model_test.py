#!/usr/bin/env python3
"""
🚀 Быстрый тестировщик моделей для RAG-системы
"""
import sys
import time
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
from config import config

def test_all_models():
    """Тестируем все доступные модели"""
    
    models = [
        "deepseek/deepseek-chat",
        "deepseek/deepseek-v3-base:free", 
        "deepseek/deepseek-chat-v3-0324:free",
        "deepseek/deepseek-r1:free",
        "google/gemini-2.0-flash-exp:free"
    ]
    
    query = "Что известно о штамме GW1-59T?"
    results = []
    
    print("🏆 СРАВНЕНИЕ LLM МОДЕЛЕЙ")
    print("=" * 60)
    print(f"📝 Тестовый запрос: {query}")
    print("=" * 60)
    
    for i, model in enumerate(models, 1):
        print(f"\n🔬 [{i}/{len(models)}] Тестирую: {model}")
        print("-" * 40)
        
        # Меняем модель в конфиге
        original_model = config.OPENROUTER_MODEL
        config.OPENROUTER_MODEL = model
        
        try:
            # Создаем RAG pipeline
            rag = RAGPipeline()
            
            start_time = time.time()
            result = rag.ask_question(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            answer_length = len(result.get('answer', ''))
            sources_count = len(result.get('sources', []))
            
            print(f"✅ Успех!")
            print(f"⏱️ Время: {response_time:.2f} сек")
            print(f"📝 Длина ответа: {answer_length} символов")
            print(f"📚 Источников: {sources_count}")
            
            results.append({
                'model': model,
                'success': True,
                'time': response_time,
                'answer_length': answer_length,
                'sources_count': sources_count,
                'answer': result.get('answer', '')[:200] + "..."  # Первые 200 символов
            })
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)[:100]}")
            results.append({
                'model': model,
                'success': False,
                'error': str(e),
                'time': 0,
                'answer_length': 0,
                'sources_count': 0
            })
        
        finally:
            config.OPENROUTER_MODEL = original_model
        
        time.sleep(2)  # Пауза между запросами
    
    # Сводка результатов
    print(f"\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Успешных: {len(successful)}/{len(results)}")
    
    if successful:
        # Самая быстрая
        fastest = min(successful, key=lambda x: x['time'])
        print(f"🚀 Самая быстрая: {fastest['model']} ({fastest['time']:.2f}с)")
        
        # Самый подробный ответ
        longest = max(successful, key=lambda x: x['answer_length'])
        print(f"📝 Самый подробный: {longest['model']} ({longest['answer_length']} симв.)")
        
        # Больше источников
        most_sources = max(successful, key=lambda x: x['sources_count'])
        print(f"📚 Больше источников: {most_sources['model']} ({most_sources['sources_count']} источн.)")
        
        print(f"\n⏱️ ВРЕМЕНА ОТВЕТОВ:")
        for result in sorted(successful, key=lambda x: x['time']):
            print(f"   {result['model']}: {result['time']:.2f}с")
    
    if failed:
        print(f"\n❌ ОШИБКИ:")
        for result in failed:
            print(f"   {result['model']}: {result['error'][:50]}...")
    
    return results

if __name__ == "__main__":
    test_all_models() 