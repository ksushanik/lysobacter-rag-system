#!/usr/bin/env python3
"""
Тестирование исправленной RAG системы с гибридным поиском
"""
import sys
sys.path.insert(0, 'src')

from lysobacter_rag.rag_pipeline import RAGPipeline

def test_fixed_rag():
    """
    Тестируем исправленную RAG систему
    """
    print("🔧 ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ RAG СИСТЕМЫ")
    print("=" * 60)
    
    rag = RAGPipeline()
    
    # Проблемные запросы, которые раньше не работали
    test_queries = [
        "Какие характеристики штамма Lysobacter capsici YC5194?",
        "Что известно о штамме GW1-59T?",
        "YC5194",
        "GW1-59T"
    ]
    
    for query in test_queries:
        print(f"\n🧪 ТЕСТ: '{query}'")
        print("-" * 50)
        
        try:
            result = rag.ask_question(query, top_k=5)
            
            answer = result['answer']
            sources = result['sources']
            confidence = result['confidence']
            
            print(f"✅ Ответ получен:")
            print(f"🎯 Уверенность: {confidence:.3f}")
            print(f"📚 Источников: {len(sources)}")
            
            # Проверяем, есть ли искомые штаммы в ответе
            answer_upper = answer.upper()
            yc_found = 'YC5194' in answer_upper
            gw_found = 'GW1-59' in answer_upper
            
            if 'YC5194' in query and yc_found:
                print("🎯 ✅ YC5194 найден в ответе!")
            elif 'GW1-59' in query and gw_found:
                print("🎯 ✅ GW1-59T найден в ответе!")
            elif 'YC5194' in query or 'GW1-59' in query:
                print("❌ Искомый штамм НЕ найден в ответе")
            
            # Показываем источники
            print(f"\n📂 Источники:")
            for source in sources[:3]:
                print(f"  - {source['document']} (стр. {source.get('page_number', 'N/A')})")
                print(f"    Релевантность: {source['relevance_score']:.3f}")
            
            # Показываем начало ответа
            print(f"\n💬 Начало ответа:")
            print(f"   {answer[:300]}...")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print("\n" + "="*60)

def demo_yc5194_fix():
    """
    Демонстрируем решение проблемы YC5194
    """
    print("🎯 ДЕМОНСТРАЦИЯ РЕШЕНИЯ ПРОБЛЕМЫ YC5194")
    print("=" * 50)
    
    rag = RAGPipeline()
    
    query = "Какие характеристики штамма Lysobacter capsici YC5194?"
    print(f"Запрос: {query}")
    
    result = rag.ask_question(query, top_k=10)
    
    answer = result['answer']
    sources = result['sources']
    confidence = result['confidence']
    
    print(f"\n📊 Результаты:")
    print(f"✅ Ответ получен: {'Да' if answer else 'Нет'}")
    print(f"🎯 Уверенность: {confidence:.3f}")
    print(f"📚 Источников использовано: {len(sources)}")
    print(f"🔍 YC5194 в ответе: {'Да' if 'YC5194' in answer.upper() else 'Нет'}")
    
    # Анализируем источники
    capsici_sources = [s for s in sources if 'capsici' in s['document'].lower()]
    print(f"📄 Источников с 'capsici': {len(capsici_sources)}")
    
    print(f"\n💬 Полный ответ:")
    print(answer)
    
    print(f"\n📚 Все источники:")
    for i, source in enumerate(sources, 1):
        print(f"{i}. {source['document']}")
        print(f"   Страница: {source.get('page_number', 'N/A')}")
        print(f"   Тип: {source.get('chunk_type', 'N/A')}")
        print(f"   Релевантность: {source['relevance_score']:.3f}")

if __name__ == "__main__":
    test_fixed_rag()
    print("\n\n")
    demo_yc5194_fix() 