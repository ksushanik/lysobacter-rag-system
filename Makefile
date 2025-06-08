# 🧬 Lysobacter RAG System - Makefile
# =====================================
# Удобные команды для управления проектом

.PHONY: help install web chat index test benchmark clean status models switch-r1 switch-chat switch-v3 test-enhanced demo apply-quality-system check-overall-quality quick-quality-improvement full-quality-reindex test-quality-improvements monitor-quality

# Цвета для вывода
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
PURPLE = \033[35m
RESET = \033[0m

# По умолчанию показываем справку
help:
	@echo "$(GREEN)🧬 Lysobacter RAG System - Команды управления$(RESET)"
	@echo "=================================================="
	@echo ""
	@echo "$(BLUE)📋 ОСНОВНЫЕ КОМАНДЫ:$(RESET)"
	@echo "  make install    - Установка зависимостей"
	@echo "  make web        - Запуск веб-интерфейса (Streamlit)"
	@echo "  make web-stop   - Остановка веб-интерфейса"
	@echo "  make web-status - Проверка статуса веб-интерфейса"
	@echo "  make chat       - Интерактивный чат"
	@echo "  make status     - Статус индекса"
	@echo ""
	@echo "$(BLUE)🗂️ УПРАВЛЕНИЕ ИНДЕКСОМ:$(RESET)"
	@echo "  make index      - Создание/проверка индекса"
	@echo "  make rebuild    - Пересоздание индекса"
	@echo ""
	@echo "$(PURPLE)🤖 УПРАВЛЕНИЕ МОДЕЛЯМИ:$(RESET)"
	@echo "  make models           - Показать доступные модели"
	@echo "  make switch-gemini    - Переключить на Gemini 2.5 Flash (качество)"
	@echo "  make switch-r1-qwen3  - Переключить на R1 Qwen3 8B (экономичная)"
	@echo "  make switch-r1-qwen3-free - Переключить на R1 Qwen3 8B (бесплатная)"
	@echo "  make switch-r1        - Переключить на DeepSeek R1 (премиум)"
	@echo "  make switch-chat      - Переключить на базовую модель (быстрая)"
	@echo ""
	@echo "$(BLUE)🧪 ТЕСТИРОВАНИЕ:$(RESET)"
	@echo "  make test-enhanced       - Быстрый тест улучшенной RAG"
	@echo "  make test-integration    - Интеграционные тесты"
	@echo "  make test-system         - Системные тесты"
	@echo "  make test-benchmarks     - Бенчмарки производительности"
	@echo "  make test-interactive    - Интерактивный тест с пользователем"
	@echo "  make test-web-improvements - Проверка улучшений веб-интерфейса"
	@echo "  make test-gw1-strain     - Специальный тест штамма GW1-59T"
	@echo "  make test-gemini-2-5     - Тест новой модели Gemini 2.5 Flash"
	@echo "  make test-r1-qwen3       - Тест экономичных моделей R1 Qwen3 8B"
	@echo "  make fix-extraction      - Переиндексация с исправлением качества"
	@echo "  make check-data-quality  - Быстрая проверка качества данных"
	@echo "  make test-all            - Тест всех моделей"
	@echo "  make demo               - Демонстрация без API вызовов"
	@echo ""
	@echo "$(BLUE)📊 АНАЛИЗ РЕЗУЛЬТАТОВ:$(RESET)"
	@echo "  make results         - Просмотр результатов бенчмарка"
	@echo "  make watch           - Мониторинг в реальном времени"
	@echo ""
	@echo "$(BLUE)🧹 УТИЛИТЫ:$(RESET)"
	@echo "  make clean           - Очистка временных файлов"
	@echo "  make structure       - Показать структуру проекта"
	@echo "  make check           - Проверка окружения"
	@echo "  make check-extraction - Диагностика качества извлечения текста"
	@echo "  make quickstart      - Быстрый старт проекта"
	@echo ""
	@echo "$(YELLOW)💡 Примеры:$(RESET)"
	@echo "  make web                    # Запуск на порту 8501"
	@echo "  make test MODEL=deepseek    # Тест конкретной модели"
	@echo "  make web PORT=8502          # Запуск на другом порту"
	@echo "  make switch-r1 && make web  # R1 + веб-интерфейс"

# Управление моделями
models:
	@echo "$(GREEN)🤖 Доступные модели:$(RESET)"
	python switch_model.py --list

switch-r1:
	@echo "$(GREEN)🧠 Переключение на DeepSeek R1 (модель рассуждений)...$(RESET)"
	python switch_model.py --switch deepseek/deepseek-r1:free
	@echo "$(PURPLE)💡 Рекомендуется для сложных научных вопросов и анализа таблиц$(RESET)"

switch-chat:
	@echo "$(GREEN)⚡ Переключение на базовую модель DeepSeek Chat...$(RESET)"
	python switch_model.py --switch deepseek/deepseek-chat
	@echo "$(PURPLE)💡 Рекомендуется для быстрых ответов и простых вопросов$(RESET)"

switch-v3:
	@echo "$(GREEN)⚖️ Переключение на DeepSeek V3 Base...$(RESET)"
	python switch_model.py --switch deepseek/deepseek-v3-base:free
	@echo "$(PURPLE)💡 Сбалансированная модель - хорошее соотношение скорости и качества$(RESET)"

switch-gemini:
	@echo "$(GREEN)🌟 Переключение на Google Gemini 2.5 Flash Preview...$(RESET)"
	python switch_model.py --switch google/gemini-2.5-flash-preview-05-20
	@echo "$(PURPLE)💡 Новейшая модель Google - рекомендуется по умолчанию$(RESET)"

switch-gemini-old:
	@echo "$(GREEN)🚀 Переключение на Google Gemini 2.0...$(RESET)"
	python switch_model.py --switch google/gemini-2.0-flash-exp:free
	@echo "$(PURPLE)💡 Предыдущая экспериментальная модель Google$(RESET)"

switch-r1-qwen3:
	@echo "$(GREEN)💰 Переключение на DeepSeek R1 Qwen3 8B (экономичная)...$(RESET)"
	python switch_model.py --switch deepseek/deepseek-r1-0528-qwen3-8b
	@echo "$(PURPLE)💡 Модель рассуждений в 3-4 раза дешевле! (\$$0.05/\$$0.10 за 1M токенов)$(RESET)"

switch-r1-qwen3-free:
	@echo "$(GREEN)🆓 Переключение на DeepSeek R1 Qwen3 8B (бесплатная)...$(RESET)"
	python switch_model.py --switch deepseek/deepseek-r1-0528-qwen3-8b:free
	@echo "$(PURPLE)💡 Полностью бесплатная модель с возможностями рассуждений!$(RESET)"

# Тестирование улучшенной системы
test-enhanced:
	@echo "$(GREEN)🧪 Тест улучшенной RAG системы...$(RESET)"
	python tests/integration/test_enhanced_rag_simple.py

# Демонстрация системы
demo:
	@echo "$(GREEN)🎬 Демонстрация возможностей системы...$(RESET)"
	python examples/demos/demo_system.py

# Установка зависимостей
install:
	@echo "$(GREEN)📦 Установка зависимостей...$(RESET)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Зависимости установлены!$(RESET)"

# Запуск веб-интерфейса
web:
	@echo "$(GREEN)🌐 Запуск веб-интерфейса Streamlit...$(RESET)"
	@if [ ! -f "examples/streamlit_app.py" ]; then \
		echo "$(YELLOW)❌ Файл examples/streamlit_app.py не найден!$(RESET)"; \
		exit 1; \
	fi
	@if [ ! -d "lysobacter_rag_env" ]; then \
		echo "$(YELLOW)❌ Виртуальное окружение не найдено! Запустите: make setup$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)💡 Веб-интерфейс будет доступен по адресу: http://localhost:$(or $(PORT),8501)$(RESET)"
	@echo "$(PURPLE)🤖 Переключение моделей доступно в боковой панели интерфейса$(RESET)"
	./scripts/start_web.sh $(or $(PORT),8501)

# Остановка веб-интерфейса
web-stop:
	@echo "$(GREEN)🛑 Остановка веб-интерфейса...$(RESET)"
	@pkill -f "streamlit.*$(or $(PORT),8501)" 2>/dev/null && echo "$(GREEN)✅ Streamlit остановлен$(RESET)" || echo "$(YELLOW)⚠️ Streamlit не был запущен$(RESET)"

# Проверка статуса веб-интерфейса
web-status:
	@echo "$(GREEN)📊 Проверка статуса веб-интерфейса...$(RESET)"
	@if curl -s -I http://localhost:$(or $(PORT),8501) >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Streamlit запущен на порту $(or $(PORT),8501)$(RESET)"; \
		echo "$(BLUE)🌐 Адрес: http://localhost:$(or $(PORT),8501)$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️ Streamlit не запущен$(RESET)"; \
		echo "$(BLUE)💡 Запустите: make web$(RESET)"; \
	fi

# Интерактивный чат
chat:
	@echo "$(GREEN)💬 Запуск интерактивного чата...$(RESET)"
	python scripts/main_improved.py

# Проверка статуса индекса
status:
	@echo "$(GREEN)📊 Проверка статуса индекса...$(RESET)"
	python run.py index --status

# Создание индекса
index:
	@echo "$(GREEN)🗂️ Создание/проверка индекса...$(RESET)"
	python scripts/index_manager.py

# Пересоздание индекса
rebuild:
	@echo "$(YELLOW)🔄 Пересоздание индекса...$(RESET)"
	python scripts/index_manager.py rebuild

# Быстрый тест модели
test:
	@echo "$(GREEN)🧪 Быстрый тест модели...$(RESET)"
	@if [ "$(MODEL)" ]; then \
		python run.py test --model "$(MODEL)" --query "Что известно о штамме GW1-59T?"; \
	else \
		echo "$(YELLOW)💡 Используйте: make test MODEL=deepseek/deepseek-chat$(RESET)"; \
		python run.py test --model "deepseek/deepseek-chat" --query "Что известно о штамме GW1-59T?"; \
	fi

# Полный бенчмарк всех моделей
benchmark:
	@echo "$(GREEN)🏆 Запуск полного бенчмарка моделей...$(RESET)"
	@echo "$(BLUE)⏱️ Это займет около 6-10 минут...$(RESET)"
	python tests/benchmarks/model_benchmark.py

# Просмотр результатов бенчмарка
results:
	@echo "$(GREEN)📊 Просмотр результатов бенчмарка...$(RESET)"
	python benchmarks/view_results.py

# Слежение за прогрессом в реальном времени
watch:
	@echo "$(GREEN)👀 Слежение за прогрессом бенчмарка...$(RESET)"
	@echo "$(BLUE)💡 Нажмите Ctrl+C для выхода$(RESET)"
	python benchmarks/view_results.py --watch

# Показать структуру проекта
structure:
	@echo "$(GREEN)📁 Новая структура проекта:$(RESET)"
	@echo ""
	@echo "$(BLUE)🧪 tests/ - Все тесты проекта:$(RESET)"
	@echo "   🔗 integration/ - Интеграционные тесты"
	@find tests/integration -name "*.py" 2>/dev/null | sed 's|^|     |' || true
	@echo "   🏆 benchmarks/ - Бенчмарки производительности"
	@find tests/benchmarks -name "*.py" 2>/dev/null | sed 's|^|     |' || true
	@echo "   ⚙️ system/ - Системные тесты"
	@find tests/system -name "*.py" 2>/dev/null | sed 's|^|     |' || true
	@echo "   🔧 unit/ - Юнит тесты (планируется)"
	@echo ""
	@echo "$(BLUE)💡 examples/ - Примеры и демо:$(RESET)"
	@echo "   🌐 streamlit_app.py - Веб-интерфейс"
	@echo "   🎬 demos/ - Демонстрации системы"
	@find examples -name "*.py" 2>/dev/null | sed 's|^|     |' || true
	@echo ""
	@echo "$(BLUE)📊 benchmarks/ - Результаты:$(RESET)"
	@find benchmarks -name "*.py" 2>/dev/null | sed 's|^|   |' || true
	@echo ""
	@echo "$(BLUE)📚 src/ - Исходный код:$(RESET)"
	@find src -name "*.py" 2>/dev/null | sed 's|^|   |' || true
	@echo ""
	@echo "$(GREEN)📋 Подробности: PROJECT_STRUCTURE.md$(RESET)"

# Очистка временных файлов
clean:
	@echo "$(GREEN)🧹 Очистка временных файлов...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.orig" -delete 2>/dev/null || true
	find . -type f -name "*~" -delete 2>/dev/null || true
	rm -f benchmark_results.json 2>/dev/null || true
	@echo "$(GREEN)✅ Временные файлы удалены!$(RESET)"

# Полная очистка (включая логи и результаты)
clean-all: clean
	@echo "$(YELLOW)🗑️ Полная очистка (логи, результаты)...$(RESET)"
	rm -rf logs/* 2>/dev/null || true
	rm -f *.log 2>/dev/null || true
	rm -f *.json 2>/dev/null || true
	@echo "$(GREEN)✅ Полная очистка завершена!$(RESET)"

# Проверка окружения
check:
	@echo "$(GREEN)🔍 Проверка окружения...$(RESET)"
	@echo ""
	@echo "$(BLUE)📋 Python версия:$(RESET)"
	python --version
	@echo ""
	@echo "$(BLUE)📦 Ключевые пакеты:$(RESET)"
	@pip list | grep -E "(streamlit|openai|langchain|chromadb|sentence-transformers)" || echo "$(YELLOW)⚠️ Некоторые пакеты не установлены$(RESET)"
	@echo ""
	@echo "$(PURPLE)🤖 Текущая модель:$(RESET)"
	@python -c "from config import config; print(f'   Модель: {config.OPENAI_MODEL}')" 2>/dev/null || echo "   ❌ Не удалось определить модель"
	@echo ""
	@echo "$(BLUE)🗂️ Структура данных:$(RESET)"
	@if [ -d "data" ]; then \
		echo "✅ Папка data: найдена"; \
		echo "   📄 PDF файлов: $$(find data -name "*.pdf" 2>/dev/null | wc -l)"; \
	else \
		echo "❌ Папка data: не найдена"; \
	fi
	@if [ -d "storage/chroma_db" ]; then \
		echo "✅ Индекс ChromaDB: найден"; \
	else \
		echo "❌ Индекс ChromaDB: не найден"; \
	fi
	@echo ""
	@echo "$(BLUE)🔑 Переменные окружения:$(RESET)"
	@if [ -n "$$OPENROUTER_API_KEY" ]; then \
		echo "✅ OPENROUTER_API_KEY: установлен"; \
	else \
		echo "❌ OPENROUTER_API_KEY: не установлен"; \
	fi

# Быстрый старт проекта
quickstart:
	@echo "$(GREEN)🚀 Быстрый старт проекта...$(RESET)"
	@echo ""
	@echo "$(BLUE)1. Проверка окружения...$(RESET)"
	@make check
	@echo ""
	@echo "$(BLUE)2. Создание индекса...$(RESET)"
	@make index
	@echo ""
	@echo "$(BLUE)3. Переключение на лучшую модель (R1)...$(RESET)"
	@make switch-r1
	@echo ""
	@echo "$(BLUE)4. Быстрый тест...$(RESET)"
	@make test-enhanced
	@echo ""
	@echo "$(GREEN)🎉 Проект готов к использованию!$(RESET)"
	@echo "$(YELLOW)💡 Запустите 'make web' для веб-интерфейса$(RESET)"

# Комплексный тест всех моделей
test-all:
	@echo "$(GREEN)🧪 Комплексный тест всех моделей...$(RESET)"
	@echo ""
	@echo "$(BLUE)🧠 Тестирую R1 модель...$(RESET)"
	@make switch-r1 > /dev/null 2>&1
	@make test-enhanced
	@echo ""
	@echo "$(BLUE)⚡ Тестирую базовую модель...$(RESET)"
	@make switch-chat > /dev/null 2>&1
	@make test-enhanced
	@echo ""
	@echo "$(BLUE)⚖️ Тестирую V3 модель...$(RESET)"
	@make switch-v3 > /dev/null 2>&1
	@make test-enhanced
	@echo ""
	@echo "$(GREEN)✅ Тест всех моделей завершен!$(RESET)"

# Интерактивный тест полной RAG системы
test-interactive:
	@echo "$(GREEN)🎮 Интерактивный тест RAG системы...$(RESET)"
	python tests/integration/test_enhanced_rag.py

# Специфичные тесты по категориям
test-integration:
	@echo "$(GREEN)🔗 Интеграционные тесты...$(RESET)"
	python tests/integration/test_enhanced_rag_simple.py

test-benchmarks:
	@echo "$(GREEN)🏆 Бенчмарки производительности...$(RESET)"
	python tests/benchmarks/model_benchmark.py

test-system:
	@echo "$(GREEN)⚙️ Системные тесты...$(RESET)"
	@echo "$(BLUE)Тест R1 модели:$(RESET)"
	python tests/system/test_r1_model.py
	@echo ""
	@echo "$(BLUE)Тест веб-интерфейса:$(RESET)"
	python tests/system/test_web.py

# Проверка качества извлечения текста
check-extraction:
	@echo "$(GREEN)🔍 Проверка качества извлечения текста...$(RESET)"
	python scripts/check_extraction_quality.py

# Тест улучшений веб-интерфейса
test-web-improvements:
	@echo "$(GREEN)🧪 Тестирование улучшений веб-интерфейса...$(RESET)"
	@echo "$(BLUE)Внесенные улучшения:$(RESET)"
	@echo "  ✅ Кнопка 'Получить развернутый ответ' теперь основная"
	@echo "  ✅ Улучшенные промпты на русском языке"
	@echo "  ✅ Структурированные ответы"
	@echo "  ✅ Диагностика качества текста"
	@echo ""
	@echo "$(CYAN)Для проверки:$(RESET)"
	@echo "$(BLUE)1. Откройте веб-интерфейс: http://localhost:8501$(RESET)"
	@echo "$(BLUE)2. Задайте вопрос: 'Что известно о штамме GW1-59T?'$(RESET)"
	@echo "$(BLUE)3. Нажмите '🧠 Получить развернутый ответ'$(RESET)"
	@echo "$(BLUE)4. Убедитесь что ответ на русском и структурированный$(RESET)"

# Тест штамма GW1-59T (без API вызовов)
test-gw1-strain:
	@echo "$(GREEN)🧬 Тест анализа штамма GW1-59T...$(RESET)"
	python scripts/test_gw1_strain.py

test-gemini-2-5:
	@echo "$(GREEN)🌟 Тест Google Gemini 2.5 Flash Preview...$(RESET)"
	python test_gemini_2_5.py
	@echo "$(PURPLE)💡 Проверка работы новейшей модели Google$(RESET)"

test-r1-qwen3:
	@echo "$(GREEN)💰 Тест экономичных моделей DeepSeek R1 Qwen3 8B...$(RESET)"
	python test_r1_qwen3.py
	@echo "$(PURPLE)💡 Проверка экономичной и бесплатной версий$(RESET)"

fix-extraction:
	@echo "$(GREEN)🔧 Переиндексация с исправлением качества данных...$(RESET)"
	python scripts/reindex_with_quality_fix.py
	@echo "$(PURPLE)💡 Исправляет проблемы извлечения текста из PDF$(RESET)"

check-data-quality:
	@echo "$(GREEN)🔍 Проверка качества данных о штамме GW1-59T...$(RESET)"
	python scripts/quick_gw1_check.py
	@echo "$(PURPLE)💡 Быстрая диагностика качества данных$(RESET)"

# Рекомендованный workflow для новых пользователей
setup:
	@echo "$(GREEN)🏗️ Настройка системы для новых пользователей...$(RESET)"
	@echo ""
	@echo "$(BLUE)1. Установка зависимостей...$(RESET)"
	@make install
	@echo ""
	@echo "$(BLUE)2. Создание индекса...$(RESET)"
	@make index
	@echo ""
	@echo "$(BLUE)3. Переключение на лучшую модель...$(RESET)"
	@make switch-r1
	@echo ""
	@echo "$(BLUE)4. Демонстрация возможностей...$(RESET)"
	@make demo
	@echo ""
	@echo "$(GREEN)🎉 Система полностью настроена!$(RESET)"
	@echo "$(PURPLE)🌐 Запустите 'make web' для использования веб-интерфейса$(RESET)"

# Разработка - горячая перезагрузка веб-интерфейса
dev:
	@echo "$(GREEN)🔧 Режим разработки (горячая перезагрузка)...$(RESET)"
	streamlit run examples/streamlit_app.py --server.port $(or $(PORT),8501) --server.runOnSave true

# Запуск в Docker (если понадобится в будущем)
docker-build:
	@echo "$(GREEN)🐳 Сборка Docker образа...$(RESET)"
	docker build -t lysobacter-rag .

docker-run:
	@echo "$(GREEN)🐳 Запуск в Docker...$(RESET)"
	docker run -p 8501:8501 -v $(PWD)/data:/app/data lysobacter-rag 

# Команды качества данных

apply-quality-system:
	@echo "🎯 Применение системы контроля качества..."
	$(PYTHON) scripts/apply_quality_system.py

check-overall-quality:
	@echo "🔍 Комплексная проверка качества всей системы..."
	$(PYTHON) scripts/comprehensive_quality_check.py

quick-quality-improvement:
	@echo "🚀 Быстрое улучшение качества..."
	@echo "1" | $(PYTHON) scripts/apply_quality_system.py

full-quality-reindex:
	@echo "🚀 Полная переиндексация с улучшениями..."
	@echo "2" | $(PYTHON) scripts/apply_quality_system.py

test-quality-improvements:
	@echo "🧪 Тестирование улучшений качества..."
	@echo "3" | $(PYTHON) scripts/apply_quality_system.py

monitor-quality:
	@echo "📊 Мониторинг качества системы..."
	$(PYTHON) scripts/quality_monitor.py

# Прямая переиндексация (исправлено)
direct-quality-reindex:
	@echo "🚀 Прямая переиндексация с улучшениями качества..."
	$(PYTHON) scripts/direct_quality_reindex.py

# Готовое решение для улучшения качества
apply-quality-solution:
	@echo "🎯 Применение готового решения для улучшения качества..."
	$(PYTHON) enhanced_search_final.py

test-quality-solution:
	@echo "🧪 Тестирование решения улучшения качества..."
	$(PYTHON) -c "from enhanced_search_final import test_quality_improvements; test_quality_improvements()" 