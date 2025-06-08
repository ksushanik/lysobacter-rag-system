# Lysobacter RAG System - Docker Image
FROM python:3.10-slim

# Метаданные
LABEL maintainer="ksushanik <ksushanik@gmail.com>"
LABEL description="Professional RAG system for Lysobacter scientific literature analysis"
LABEL version="1.0"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    git \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-rus \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p data logs storage

# Создание пользователя без root привилегий
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Переменные окружения
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Экспозиция порта
EXPOSE 8501

# Создание точек монтирования
VOLUME ["/app/data", "/app/storage", "/app/logs"]

# Команда по умолчанию
CMD ["python", "run.py", "web"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1 