# 🚀 Руководство по установке Lysobacter RAG System

Это подробное руководство по установке и настройке системы на новом компьютере.

## 📋 Системные требования

### Минимальные требования:
- **ОС:** Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python:** 3.9+ (рекомендуется 3.10+)
- **RAM:** 8 GB (рекомендуется 16 GB)
- **Диск:** 10 GB свободного места
- **Интернет:** Для загрузки моделей и API

### Рекомендуемые требования:
- **RAM:** 16+ GB для полной производительности
- **GPU:** Опционально, для ускорения эмбеддингов
- **SSD:** Для быстрого доступа к векторной БД

## 🛠️ Пошаговая установка

### Шаг 1: Установка Python и зависимостей системы

#### На Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

#### На macOS:
```bash
# Установите Homebrew если нет: https://brew.sh
brew install python git
```

#### На Windows:
1. Скачайте Python с https://python.org/downloads/
2. Установите Git с https://git-scm.com/download/win

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/ksushanik/lysobacter-rag-system.git
cd lysobacter-rag-system
```

### Шаг 3: Создание виртуального окружения

```bash
# Создание окружения
python3 -m venv lysobacter_rag_env

# Активация (Linux/macOS)
source lysobacter_rag_env/bin/activate

# Активация (Windows)
lysobacter_rag_env\Scripts\activate
```

### Шаг 4: Установка зависимостей

```bash
# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt
```

**Примечание:** Установка может занять 10-15 минут из-за загрузки ML библиотек.

### Шаг 5: Настройка переменных окружения

```bash
# Копирование шаблона конфигурации
cp .env.example .env

# Редактирование файла .env
nano .env  # или любой текстовый редактор
```

**Обязательно настройте:**
```env
# Получите ключ на https://openrouter.ai/keys
OPENROUTER_API_KEY=your_actual_api_key_here

# Выберите модель (рекомендуется)
OPENROUTER_MODEL=deepseek/deepseek-chat
```

### Шаг 6: Получение данных

Система работает с PDF документами о лизобактериях. У вас есть несколько вариантов:

#### Вариант A: Собственные PDF файлы
```bash
# Создайте папку для данных
mkdir -p data

# Добавьте ваши PDF файлы в папку data/
# Поддерживаются: научные статьи, описания штаммов, etc.
```

#### Вариант B: Тестовые данные
```bash
# Создайте небольшую коллекцию для тестирования
mkdir -p data
echo "Добавьте сюда ваши PDF файлы о лизобактериях" > data/README.txt
```

### Шаг 7: Инициализация системы

```bash
# Первый запуск и создание индекса
python run.py index --create

# Проверка статуса
python run.py index --status
```

### Шаг 8: Тестирование установки

```bash
# Тест базовой функциональности
python run.py test --quick

# Тест с простым запросом
python run.py chat
# Введите: "Что такое лизобактерии?"
```

### Шаг 9: Запуск веб-интерфейса

```bash
# Запуск Streamlit приложения
python run.py web

# Откройте браузер: http://localhost:8501
```

## 🔧 Дополнительная настройка

### Настройка для производства

1. **Оптимизация производительности:**
```env
# В .env файле
CHUNK_SIZE=1500
RAG_TOP_K=10
ENABLE_CACHING=true
```

2. **Настройка логирования:**
```env
LOG_LEVEL=WARNING  # Меньше логов в production
```

### Настройка для разработки

1. **Режим отладки:**
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

2. **Быстрая перезагрузка:**
```bash
# Автоматическая перезагрузка при изменениях
streamlit run examples/streamlit_app.py --server.runOnSave true
```

## 📊 Управление данными

### Добавление новых документов

```bash
# Добавьте PDF файлы в папку data/
cp /path/to/new/papers/*.pdf data/

# Переиндексация
python run.py index --rebuild
```

### Резервное копирование

```bash
# Создание бэкапа векторной БД
tar -czf backup_$(date +%Y%m%d).tar.gz storage/

# Восстановление
tar -xzf backup_20250108.tar.gz
```

### Очистка и сброс

```bash
# Полная очистка индекса
python run.py index --reset

# Удаление кэша
rm -rf __pycache__ logs/
```

## 🚨 Устранение проблем

### Проблема: "ModuleNotFoundError"
```bash
# Убедитесь что виртуальное окружение активно
source lysobacter_rag_env/bin/activate

# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

### Проблема: "OpenRouter API Error"
```bash
# Проверьте API ключ
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key:', os.getenv('OPENROUTER_API_KEY')[:10] + '...')"

# Тест подключения
python tests/test_openrouter.py
```

### Проблема: "ChromaDB Error"
```bash
# Пересоздание БД
rm -rf storage/chroma_db
python run.py index --create
```

### Проблема: Медленная работа
1. **Проверьте RAM:** Система нуждается в 8+ GB
2. **Оптимизируйте настройки:**
```env
CHUNK_SIZE=800  # Меньше размер чанков
RAG_TOP_K=3     # Меньше результатов поиска
```

### Проблема: Ошибки с PDF
```bash
# Установка дополнительных зависимостей для PDF
pip install pymupdf[extras] pdfplumber[dev]

# На Ubuntu может потребоваться:
sudo apt install poppler-utils
```

## 📱 Альтернативные способы запуска

### Docker (опционально)

```bash
# Если у вас есть Docker
docker build -t lysobacter-rag .
docker run -p 8501:8501 -v $(pwd)/data:/app/data lysobacter-rag
```

### Jupyter Notebook

```bash
# Запуск в Jupyter
pip install jupyter
jupyter notebook examples/demo_notebook.ipynb
```

### Google Colab

1. Загрузите `examples/colab_setup.ipynb`
2. Запустите в Google Colab
3. Загрузите свои PDF файлы

## 🔗 Полезные ссылки

- **GitHub Issues:** Сообщения об ошибках
- **OpenRouter:** https://openrouter.ai/keys (API ключи)
- **Документация:** `docs/` папка в репозитории
- **Примеры:** `examples/` папка

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте логи:** `logs/lysobacter_rag.log`
2. **Запустите диагностику:** `python run.py diagnose`
3. **Создайте issue** на GitHub с логами и описанием проблемы

---

**Установка готова!** 🎉 Теперь у вас есть полнофункциональная RAG система для анализа литературы о лизобактериях. 