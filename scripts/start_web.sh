#!/bin/bash

# Скрипт для запуска веб-интерфейса Streamlit
# Использование: ./scripts/start_web.sh [PORT]

set -e

# Определяем порт (по умолчанию 8501)
PORT=${1:-8501}

# Определяем корневую папку проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🌐 Запуск веб-интерфейса Streamlit..."
echo "📁 Рабочая папка: $PROJECT_ROOT"
echo "🔌 Порт: $PORT"

# Проверяем наличие виртуального окружения
if [ ! -d "lysobacter_rag_env" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "💡 Запустите: make setup"
    exit 1
fi

# Проверяем наличие файла приложения
if [ ! -f "examples/streamlit_app.py" ]; then
    echo "❌ Файл examples/streamlit_app.py не найден!"
    exit 1
fi

# Останавливаем существующие процессы на этом порту
echo "📝 Остановка существующих процессов на порту $PORT..."
pkill -f "streamlit.*$PORT" 2>/dev/null || true
sleep 1

# Активируем виртуальное окружение и запускаем Streamlit
echo "🚀 Запуск Streamlit..."
echo "🌐 Веб-интерфейс будет доступен по адресу: http://localhost:$PORT"

source lysobacter_rag_env/bin/activate
exec streamlit run examples/streamlit_app.py --server.port "$PORT" --server.headless true 