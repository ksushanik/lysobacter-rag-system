#!/usr/bin/env python3
"""
Демонстрация возможностей улучшенной RAG системы с DeepSeek R1
"""
import sys
from pathlib import Path

# Добавляем пути для импорта из родительской папки проекта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def demo_system_features():
    """Демонстрирует возможности системы без вызовов API"""
    
    print("🧬 ДЕМОНСТРАЦИЯ RAG СИСТЕМЫ С DEEPSEEK R1")
    print("=" * 60)
    
    try:
        from lysobacter_rag.rag_pipeline.enhanced_prompts import EnhancedPromptSystem
        from lysobacter_rag.indexer.indexer import Indexer
        from config import config
        
        print(f"🤖 Используемая модель: {config.OPENAI_MODEL}")
        print(f"🔗 API URL: {config.OPENROUTER_BASE_URL}")
        
        # Демонстрация промптов
        print(f"\n📝 ДЕМОНСТРАЦИЯ УЛУЧШЕННЫХ ПРОМПТОВ")
        print("=" * 50)
        
        enhanced_prompts = EnhancedPromptSystem()
        
        test_queries = [
            "Что известно о штамме GW1-59T?",
            "Сравните морфологические характеристики различных лизобактерий",
            "Объясните методы выделения лизобактерий",
            "Проанализируйте данные таблицы дифференциальных характеристик",
            "Как связаны геномные и фенотипические данные?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Запрос {i}: {query}")
            
            query_type = enhanced_prompts.detect_query_type(query)
            print(f"   🎯 Определенный тип: {query_type}")
            
            if query_type in enhanced_prompts.prompts:
                prompt_template = enhanced_prompts.prompts[query_type]
                print(f"   📋 Используется специализированный промпт для: {query_type}")
                print(f"   💡 Фокус промпта: {get_prompt_focus(query_type.value)}")
            else:
                print(f"   📋 Используется базовый промпт")
        
        # Демонстрация индексации
        print(f"\n📚 ДЕМОНСТРАЦИЯ СИСТЕМЫ ИНДЕКСАЦИИ")
        print("=" * 50)
        
        indexer = Indexer()
        
        # Получаем статистику коллекции
        collection = indexer.collection
        count = collection.count()
        
        print(f"📊 Статистика базы знаний:")
        print(f"   📄 Документов в коллекции: {count}")
        print(f"   🏷️ Название коллекции: {config.CHROMA_COLLECTION_NAME}")
        print(f"   🤖 Модель эмбеддингов: {config.EMBEDDING_MODEL}")
        print(f"   📁 Путь к БД: {config.CHROMA_DB_PATH}")
        
        # Демонстрация поиска
        print(f"\n🔍 ДЕМОНСТРАЦИЯ ПОИСКА")
        print("=" * 40)
        
        test_search_query = "GW1-59T"
        print(f"🔎 Тестовый поиск: '{test_search_query}'")
        
        results = indexer.search(test_search_query, top_k=3)
        
        print(f"📊 Найдено результатов: {len(results)}")
        
        for i, result in enumerate(results[:3], 1):
            print(f"\n   📄 Результат {i}:")
            print(f"      📋 ID: {result.get('id', 'N/A')}")
            print(f"      📊 Релевантность: {result.get('distance', 0):.3f}")
            print(f"      📚 Документ: {result.get('document', 'N/A')}")
            print(f"      📄 Страница: {result.get('page', 'N/A')}")
            
            if result.get('is_differential_table'):
                print(f"      🔬 Дифференциальная таблица: ✅")
            
            content = result.get('content', '')
            if len(content) > 100:
                print(f"      📝 Контент: {content[:100]}...")
            else:
                print(f"      📝 Контент: {content}")
        
        # Демонстрация конфигурации
        print(f"\n⚙️ КОНФИГУРАЦИЯ СИСТЕМЫ")
        print("=" * 40)
        
        print(f"📊 Настройки RAG:")
        print(f"   🎯 Top-K результатов: {config.RAG_TOP_K}")
        print(f"   🌡️ Температура: {config.RAG_TEMPERATURE}")
        print(f"   📏 Размер чанка: {config.CHUNK_SIZE}")
        print(f"   🔄 Перекрытие чанков: {config.CHUNK_OVERLAP}")
        print(f"   🎨 Порог нечеткого поиска: {config.FUZZY_MATCH_THRESHOLD}%")
        
        print(f"\n🎯 Доступные модели:")
        for i, model in enumerate(config.AVAILABLE_MODELS, 1):
            current = " ⭐" if model == config.OPENAI_MODEL else ""
            print(f"   {i}. {model}{current}")
        
        print(f"\n✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print(f"🧠 Система готова к работе с DeepSeek R1")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_prompt_focus(query_type: str) -> str:
    """Возвращает описание фокуса промпта"""
    
    focuses = {
        'strain_analysis': 'Детальный анализ характеристик штамма',
        'comparative_analysis': 'Сравнение множественных объектов',
        'methodology': 'Объяснение методов и процедур',
        'table_interpretation': 'Интерпретация табличных данных',
        'synthesis': 'Синтез информации из различных источников'
    }
    
    return focuses.get(query_type, 'Общий анализ')

def demo_web_interface():
    """Показывает информацию о веб-интерфейсе"""
    
    print(f"\n🌐 ВЕБ-ИНТЕРФЕЙС")
    print("=" * 30)
    
    print(f"🚀 Запуск веб-интерфейса:")
    print(f"   python run.py")
    print(f"")
    print(f"🌍 После запуска доступен по адресу:")
    print(f"   http://localhost:8501")
    print(f"")
    print(f"💬 В веб-интерфейсе можно:")
    print(f"   • Задавать вопросы о лизобактериях")
    print(f"   • Видеть источники информации")
    print(f"   • Загружать новые PDF документы")
    print(f"   • Анализировать качество ответов")

def demo_command_examples():
    """Показывает примеры команд для тестирования"""
    
    print(f"\n🛠️ КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ")
    print("=" * 40)
    
    commands = [
        {
            'command': 'python switch_model.py --list',
            'description': 'Показать доступные модели'
        },
        {
            'command': 'python switch_model.py --test',
            'description': 'Тестировать текущую модель'
        },
        {
            'command': 'python test_enhanced_rag_simple.py',
            'description': 'Простой тест улучшенной системы'
        },
        {
            'command': 'python run.py',
            'description': 'Запустить веб-интерфейс'
        },
        {
            'command': 'python model_benchmark.py',
            'description': 'Бенчмарк различных моделей'
        }
    ]
    
    for cmd in commands:
        print(f"\n📝 {cmd['description']}:")
        print(f"   {cmd['command']}")

if __name__ == "__main__":
    print("🚀 ЗАПУСК ДЕМОНСТРАЦИИ СИСТЕМЫ")
    print("🧠 RAG система с DeepSeek R1 для лизобактерий")
    print()
    
    success = demo_system_features()
    
    if success:
        demo_web_interface()
        demo_command_examples()
    
    print(f"\n{'='*60}")
    print("🎯 ИТОГ:", "✅ СИСТЕМА ГОТОВА К РАБОТЕ" if success else "❌ ТРЕБУЕТСЯ НАСТРОЙКА")
    print("🧬 Используйте веб-интерфейс для интерактивного тестирования!")
    
    sys.exit(0 if success else 1) 