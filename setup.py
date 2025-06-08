#!/usr/bin/env python3
"""
Setup script for Lysobacter RAG System
Автоматическая установка и настройка системы
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True, cwd=None):
    """Выполняет команду в оболочке"""
    print(f"🔧 Выполняю: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, cwd=cwd, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении команды: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_python_version():
    """Проверяет версию Python"""
    print("🐍 Проверяю версию Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Требуется Python 3.9+, у вас {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def create_virtual_env():
    """Создает виртуальное окружение"""
    print("📦 Создаю виртуальное окружение...")
    
    # Проверяем существует ли уже
    if Path("lysobacter_rag_env").exists():
        print("⚠️  Виртуальное окружение уже существует")
        return True
    
    # Создаем новое
    if not run_command(f"{sys.executable} -m venv lysobacter_rag_env"):
        print("❌ Не удалось создать виртуальное окружение")
        return False
    
    print("✅ Виртуальное окружение создано")
    return True

def get_pip_path():
    """Получает путь к pip в виртуальном окружении"""
    if os.name == 'nt':  # Windows
        return "lysobacter_rag_env/Scripts/pip"
    else:  # Linux/macOS
        return "lysobacter_rag_env/bin/pip"

def install_dependencies():
    """Устанавливает зависимости"""
    print("📚 Устанавливаю зависимости...")
    
    pip_path = get_pip_path()
    
    # Обновляем pip
    if not run_command(f"{pip_path} install --upgrade pip"):
        print("⚠️  Не удалось обновить pip")
    
    # Устанавливаем зависимости
    if not run_command(f"{pip_path} install -r requirements.txt"):
        print("❌ Не удалось установить зависимости")
        return False
    
    print("✅ Зависимости установлены")
    return True

def setup_config():
    """Настраивает конфигурацию"""
    print("⚙️  Настраиваю конфигурацию...")
    
    # Копируем .env.example в .env если его нет
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✅ Создан файл .env из шаблона")
        else:
            print("⚠️  Файл .env.example не найден")
    else:
        print("⚠️  Файл .env уже существует")
    
    # Создаем необходимые папки
    dirs_to_create = ["data", "logs", "storage"]
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ Папки созданы")
    return True

def check_installation():
    """Проверяет установку"""
    print("🧪 Проверяю установку...")
    
    # Проверяем что можем импортировать основные модули
    python_path = get_pip_path().replace("pip", "python")
    
    test_imports = [
        "import streamlit",
        "import chromadb", 
        "import sentence_transformers",
        "from src.lysobacter_rag.indexer.indexer import Indexer"
    ]
    
    for test_import in test_imports:
        cmd = f"{python_path} -c \"{test_import}\""
        if not run_command(cmd, check=False):
            print(f"⚠️  Проблема с импортом: {test_import}")
        else:
            print(f"✅ {test_import}")
    
    return True

def print_next_steps():
    """Выводит следующие шаги"""
    print("\n" + "="*60)
    print("🎉 УСТАНОВКА ЗАВЕРШЕНА!")
    print("="*60)
    print()
    
    activation_cmd = "lysobacter_rag_env\\Scripts\\activate" if os.name == 'nt' else "source lysobacter_rag_env/bin/activate"
    
    print("📋 СЛЕДУЮЩИЕ ШАГИ:")
    print()
    print("1. Активируйте виртуальное окружение:")
    print(f"   {activation_cmd}")
    print()
    print("2. Настройте API ключ в файле .env:")
    print("   - Получите ключ на https://openrouter.ai/keys")
    print("   - Отредактируйте .env: OPENROUTER_API_KEY=your_key_here")
    print()
    print("3. Добавьте PDF файлы в папку data/")
    print()
    print("4. Запустите систему:")
    print("   python run.py web")
    print()
    print("📚 Подробная документация: docs/guides/INSTALLATION_GUIDE.md")
    print()

def main():
    """Основная функция установки"""
    print("🚀 УСТАНОВКА LYSOBACTER RAG SYSTEM")
    print("="*50)
    print()
    
    # Проверки
    if not check_python_version():
        sys.exit(1)
    
    # Установка
    steps = [
        ("Создание виртуального окружения", create_virtual_env),
        ("Установка зависимостей", install_dependencies),
        ("Настройка конфигурации", setup_config),
        ("Проверка установки", check_installation),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📍 {step_name}...")
        if not step_func():
            print(f"❌ Ошибка на шаге: {step_name}")
            sys.exit(1)
    
    # Финальные инструкции
    print_next_steps()

if __name__ == "__main__":
    main() 