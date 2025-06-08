#!/usr/bin/env python3
"""
Простой тест улучшенной RAG системы
"""
import sys
from pathlib import Path

# Добавляем пути для импорта из корня проекта  
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_enhanced_system():
    """Простой тест улучшенной системы"""
    
    print("🧬 ТЕСТ УЛУЧШЕННОЙ RAG СИСТЕМЫ")
    print("=" * 50)
    
    try:
        # Импорт и инициализация
        from lysobacter_rag.rag_pipeline.enhanced_rag import EnhancedRAGPipeline
        
        print("📦 Инициализация системы...")
        enhanced_rag = EnhancedRAGPipeline()
        print("✅ Система инициализирована")
        
        # Тест определения типа запроса
        print("\n🎯 Тест определения типов запросов:")
        test_query = "Что известно о штамме GW1-59T?"
        query_type = enhanced_rag.prompt_system.detect_query_type(test_query)
        print(f"   Запрос: {test_query}")
        print(f"   Определенный тип: {query_type.value}")
        
        # Тест получения ответа
        print("\n💬 Тест генерации ответа:")
        result = enhanced_rag.ask_question(test_query)
        
        print(f"   Тип запроса: {result.query_type}")
        print(f"   Уверенность: {result.confidence:.3f}")
        print(f"   Источников: {result.num_sources_used}")
        print(f"   Длина ответа: {len(result.answer)} символов")
        
        if result.metadata.get('has_tables'):
            print(f"   Найдено таблиц: {result.metadata['table_count']}")
        
        print(f"\n📝 Ответ (первые 300 символов):")
        print(result.answer[:300] + "..." if len(result.answer) > 300 else result.answer)
        
        print("\n✅ Тест завершен успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_system()
    sys.exit(0 if success else 1) 