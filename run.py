#!/usr/bin/env python3
"""
Lysobacter RAG System - Главный запускатель
================================================================

Система поиска и анализа информации о лизобактериях с поддержкой:
- Многоязычного поиска (русский/английский)
- Персистентного векторного индекса
- Различных LLM моделей
- Сравнительного анализа

Использование:
    python run.py --help
"""

import argparse
import sys
import os
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def main():
    """Главная функция запуска"""
    
    parser = argparse.ArgumentParser(
        description="Lysobacter RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python run.py chat                    # Интерактивный чат
  python run.py web                     # Веб-интерфейс
  python run.py index --rebuild          # Пересоздать индекс
  python run.py test --model deepseek    # Тест модели
  python run.py benchmark               # Сравнение моделей
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда: chat
    chat_parser = subparsers.add_parser('chat', help='Интерактивный чат')
    chat_parser.add_argument('--model', default='deepseek/deepseek-chat', 
                           help='Модель для использования')
    
    # Команда: web  
    web_parser = subparsers.add_parser('web', help='Запуск веб-интерфейса')
    web_parser.add_argument('--port', type=int, default=8501, 
                          help='Порт для веб-сервера')
    
    # Команда: index
    index_parser = subparsers.add_parser('index', help='Управление индексом')
    index_parser.add_argument('--rebuild', action='store_true',
                            help='Пересоздать индекс')
    index_parser.add_argument('--status', action='store_true',
                            help='Статус индекса')
    
    # Команда: test
    test_parser = subparsers.add_parser('test', help='Тестирование моделей')
    test_parser.add_argument('--model', required=True,
                           help='Модель для тестирования')
    test_parser.add_argument('--query', default='GW1-59T',
                           help='Тестовый запрос')
    
    # Команда: benchmark
    benchmark_parser = subparsers.add_parser('benchmark', help='Сравнение моделей')
    benchmark_parser.add_argument('--models', nargs='+', 
                                default=['deepseek/deepseek-chat', 'deepseek/deepseek-v3-base:free'],
                                help='Список моделей для сравнения')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Выполняем команды
    if args.command == 'chat':
        from main_improved import main as chat_main
        chat_main()
        
    elif args.command == 'web':
        import subprocess
        cmd = f"streamlit run examples/streamlit_app.py --server.port {args.port}"
        subprocess.run(cmd, shell=True)
        
    elif args.command == 'index':
        from index_manager import IndexManager
        manager = IndexManager()
        
        if args.status:
            status = manager.get_index_status()
            print("СТАТУС ИНДЕКСА")
            print("=" * 40)
            if status['exists']:
                print(f"Статус: {status['status']}")
                print(f"Создан: {status.get('created_at', 'Неизвестно')}")
                print(f"PDF файлов: {status.get('pdf_count', 0)}")
                print(f"Чанков: {status.get('chunk_count', 0)}")
            else:
                print("Индекс не создан")
                
        elif args.rebuild:
            manager.create_index(force_rebuild=True)
        else:
            manager.create_index()
            
    elif args.command == 'test':
        from model_tester import test_model
        test_model(args.model, args.query)
        
    elif args.command == 'benchmark':
        from model_comparison import compare_models
        compare_models(args.models)

if __name__ == "__main__":
    main() 