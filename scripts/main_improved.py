#!/usr/bin/env python3
"""
Улучшенная RAG-система для работы с документами о лизобактериях
Работает как NotebookLM - один раз индексируем, многократно используем
"""

import os
from pathlib import Path
from config import config
from index_manager import IndexManager
from src.lysobacter_rag.rag_pipeline import RAGPipeline
from loguru import logger

def check_environment():
    """Проверяет готовность окружения"""
    
    print("🔍 ПРОВЕРКА СИСТЕМЫ")
    print("=" * 40)
    
    # Проверяем API ключи
    if not config.OPENROUTER_API_KEY and not config.OPENAI_API_KEY:
        print("❌ Не настроен API ключ для LLM")
        print("💡 Добавьте OPENROUTER_API_KEY или OPENAI_API_KEY в .env файл")
        return False
    else:
        if config.OPENROUTER_API_KEY:
            print(f"✅ API ключ настроен (OpenRouter)")
            print(f"   Модель: {config.OPENROUTER_MODEL}")
        else:
            print(f"✅ API ключ настроен (OpenAI)")
            print(f"   Модель: {config.OPENAI_MODEL}")
    
    # Проверяем папку с данными
    data_dir = Path(config.DATA_DIR)
    if not data_dir.exists():
        print(f"❌ Папка с данными не найдена: {data_dir}")
        return False
    
    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ PDF файлы не найдены в папке: {data_dir}")
        return False
    
    print(f"✅ Найдено PDF файлов: {len(pdf_files)}")
    
    # Проверяем папку хранения
    storage_dir = config.STORAGE_DIR
    storage_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Папка хранения: {storage_dir}")
    
    return True

def initialize_index():
    """Инициализирует индекс знаний"""
    
    print("\n🗃️ ИНИЦИАЛИЗАЦИЯ ИНДЕКСА ЗНАНИЙ")
    print("=" * 50)
    
    manager = IndexManager()
    status = manager.get_index_status()
    
    if status['exists'] and status['status'] == 'ready':
        print("✅ Индекс уже создан и готов к использованию")
        print(f"   📊 PDF файлов: {status['pdf_count']}")
        print(f"   📚 Чанков: {status['chunk_count']}")
        print(f"   🕒 Создан: {status['created_at']}")
        return True
    
    elif status['exists'] and status['status'] == 'outdated':
        print("⚠️ Индекс устарел (изменилось количество PDF файлов)")
        choice = input("🔄 Обновить индекс? (y/n): ").strip().lower()
        
        if choice in ['y', 'yes', 'да', 'д']:
            return manager.create_index(force_rebuild=True)
        else:
            print("❌ Работа с устаревшим индексом может быть неточной")
            return True
    
    else:
        print("📝 Индекс не найден, создаю новый...")
        choice = input("🚀 Создать индекс? (y/n): ").strip().lower()
        
        if choice in ['y', 'yes', 'да', 'д']:
            return manager.create_index()
        else:
            print("❌ Без индекса система не может работать")
            return False

def interactive_chat():
    """Интерактивный чат с системой"""
    
    print("\n🤖 ИНТЕРАКТИВНЫЙ ЧАТ С СИСТЕМОЙ")
    print("=" * 50)
    print("Теперь вы можете задавать вопросы о лизобактериях!")
    print("Примеры вопросов:")
    print("  • Расскажи о штамме GH1-9T")
    print("  • Какие температурные условия предпочитают лизобактерии?")
    print("  • Где был выделен штамм ZLD-17T?")
    print("  • Сравни характеристики разных штаммов")
    print("\nВведите 'exit' для выхода, 'stats' для статистики")
    print("-" * 50)
    
    try:
        # Инициализируем RAG-пайплайн
        rag = RAGPipeline()
        print("✅ RAG-система готова к работе\n")
        
        while True:
            try:
                question = input("❓ Ваш вопрос: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['exit', 'выход', 'quit', 'q']:
                    print("👋 До свидания!")
                    break
                
                if question.lower() in ['stats', 'статистика']:
                    # Показываем статистику индекса
                    from src.lysobacter_rag.indexer import Indexer
                    indexer = Indexer()
                    stats = indexer.get_collection_stats()
                    
                    print("\n📊 СТАТИСТИКА ИНДЕКСА:")
                    print(f"   📚 Всего чанков: {stats['total_chunks']}")
                    print(f"   📝 Текстовых: {stats['chunk_types'].get('text', 0)}")
                    print(f"   📊 Табличных: {stats['chunk_types'].get('table', 0)}")
                    print(f"   📄 Источников: {len(stats['sources'])}")
                    print("=" * 30)
                    continue
                
                # Обрабатываем вопрос
                print("🔍 Ищу информацию...")
                
                response = rag.ask_question(question)
                
                print(f"\n💬 Ответ:")
                print(f"{response['answer']}")
                
                print(f"\n📊 Метрики:")
                print(f"   🎯 Источников использовано: {response.get('num_sources_used', 0)}")
                print(f"   ⭐ Уверенность: {response.get('confidence', 0):.2f}")
                
                if response.get('sources'):
                    print(f"   📚 Источники: {', '.join(response['sources'])}")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка при обработке вопроса: {e}")
                logger.error(f"Ошибка в интерактивном чате: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка инициализации RAG-системы: {e}")
        logger.error(f"Ошибка инициализации RAG: {e}")

def quick_test():
    """Быстрый тест системы"""
    
    print("\n⚡ БЫСТРЫЙ ТЕСТ СИСТЕМЫ")
    print("=" * 40)
    
    try:
        rag = RAGPipeline()
        
        test_questions = [
            "Расскажи о Lysobacter daejeonensis",
            "Какие штаммы описаны в документах?",
            "Температурные условия роста лизобактерий"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Тест вопрос: {question}")
            
            try:
                response = rag.ask_question(question)
                
                if response['answer'] and "не смог найти" not in response['answer'].lower():
                    print(f"   ✅ Ответ получен ({len(response['answer'])} символов)")
                    print(f"   📊 Источников: {response.get('num_sources_used', 0)}")
                else:
                    print(f"   ⚠️ Информация не найдена")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        print(f"\n✅ Быстрый тест завершен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def main():
    """Основная функция"""
    
    print("🧬 RAG-СИСТЕМА ДЛЯ АНАЛИЗА ЛИЗОБАКТЕРИЙ")
    print("🎯 Версия 2.0 с персистентным индексом (как NotebookLM)")
    print("=" * 60)
    
    # Проверяем окружение
    if not check_environment():
        print("\n❌ Система не готова к работе")
        return
    
    # Инициализируем индекс
    if not initialize_index():
        print("\n❌ Не удалось инициализировать индекс")
        return
    
    # Предлагаем варианты работы
    print("\n🚀 СИСТЕМА ГОТОВА К РАБОТЕ!")
    print("Выберите режим работы:")
    print("1. 💬 Интерактивный чат")
    print("2. ⚡ Быстрый тест")
    print("3. 📊 Статистика индекса")
    print("4. 🌐 Запустить веб-интерфейс")
    
    try:
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == '1':
            interactive_chat()
        
        elif choice == '2':
            quick_test()
        
        elif choice == '3':
            manager = IndexManager()
            status = manager.get_index_status()
            
            print("\n📊 СТАТИСТИКА ИНДЕКСА:")
            print("=" * 30)
            print(f"Статус: {status.get('status', 'неизвестно')}")
            print(f"PDF файлов: {status.get('pdf_count', 0)}")
            print(f"Чанков: {status.get('chunk_count', 0)}")
            print(f"Создан: {status.get('created_at', 'неизвестно')}")
            
            if status.get('sources'):
                print(f"Источники: {len(status['sources'])}")
        
        elif choice == '4':
            print("\n🌐 Для запуска веб-интерфейса выполните:")
            print("streamlit run streamlit_app.py")
            
        else:
            print("❌ Неверный выбор")
    
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logger.error(f"Ошибка в main: {e}")

if __name__ == "__main__":
    main() 