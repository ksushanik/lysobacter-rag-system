# 🔄 Реорганизация проекта Lysobacter RAG

## 📊 Результаты структурной проверки

**Проблема**: 42+ тестовых и отладочных файла загромождали корневую папку проекта

**Решение**: Перемещение 88 файлов в логически организованную структуру

## 🗂️ Новая структура проекта

### 📂 tests/ - Тестирование
```
tests/
├── debugging/          # Отладка проблем (YC5194, поиск)
│   ├── debug_yc5194_*.py
│   ├── test_yc5194_*.py
│   ├── fix_search_system.py
│   └── diagnose_search_issue.py
├── quality/            # Тесты качества данных
│   ├── test_quality_*.py
│   ├── diagnose_*.py
│   └── enhanced_search_*.py
├── models/             # Тестирование ИИ моделей
│   ├── test_gemini_*.py
│   ├── test_r1_*.py
│   └── switch_model.py
├── web/               # Веб-интерфейс тесты
│   ├── test_web_*.py
│   └── test_notebooklm_*.py
└── system/            # Системные тесты
    ├── test_final_integration.py
    └── test_advanced_extractor.py
```

### 🛠️ scripts/ - Утилиты и обслуживание
```
scripts/
├── maintenance/       # Обслуживание системы
│   ├── reindex_*.py
│   ├── complete_reindex_fixed.py
│   └── enhanced_chunking_strategy.py
└── utilities/         # Служебные утилиты
    └── integration_example.py
```

### 📚 docs/ - Документация
```
docs/
├── guides/           # Руководства пользователя
│   ├── HOW_TO_TEST.md
│   ├── WEB_INTERFACE_GUIDE.md
│   ├── ENHANCEMENT_GUIDE.md
│   └── MODEL_SWITCHING_FIX.md
└── reports/          # Отчеты и аналитика
    ├── FINAL_SOLUTION_REPORT.md
    ├── quality_report.json
    └── benchmark_results.json
```

### 🏠 Корневая папка - только необходимое
```
lysobacters/
├── config.py          # Конфигурация системы
├── run.py            # Главный файл запуска
├── README.md         # Основная документация
├── requirements.txt  # Зависимости
└── Makefile         # Автоматизация задач
```

## 📈 Статистика перемещения

- **Перемещено файлов**: 88
- **Освобождена корневая папка**: от 42+ тестовых файлов
- **Создано категорий**: 8 специализированных папок
- **Улучшена навигация**: логическая группировка по назначению

## 🎯 Преимущества новой структуры

1. **Чистая корневая папка** - только ключевые файлы
2. **Логическая группировка** - файлы сгруппированы по назначению
3. **Лучшая навигация** - легко найти нужные тесты или документы
4. **Профессиональный вид** - соответствует стандартам Python проектов
5. **Упрощенная разработка** - разработчики быстрее ориентируются в проекте

## 🔄 Как это влияет на разработку

### Запуск тестов:
```bash
# Тесты отладки YC5194
python tests/debugging/debug_yc5194_search.py

# Тесты качества
python tests/quality/test_quality_before_after.py

# Веб-тесты
python tests/web/test_web_integration.py
```

### Обслуживание:
```bash
# Реиндексация
python scripts/maintenance/reindex_with_smart_chunking.py

# Утилиты
python scripts/utilities/integration_example.py
```

## ✅ Проверка корректности

Все файлы сохранили свою функциональность, изменились только пути. 
Проект стал более профессиональным и удобным для разработки. 