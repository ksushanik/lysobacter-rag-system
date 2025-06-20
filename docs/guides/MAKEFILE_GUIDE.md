# 🛠️ Руководство по Makefile командам

## 🎯 Makefile - это ваш главный инструмент управления!

Все команды теперь доступны через простые `make` команды. Не нужно запоминать длинные пути к скриптам!

## 🚀 Быстрый старт

```bash
# Показать все доступные команды
make help

# Полная настройка системы (для новых пользователей)
make setup

# Быстрый старт (для уже настроенной системы)
make quickstart
```

## 🤖 Переключение моделей (новое!)

### Показать доступные модели:
```bash
make models
```

### Переключение на модели:
```bash
# 🧠 Лучшее качество - R1 (рекомендуется)
make switch-r1

# ⚡ Быстрые ответы - базовая модель
make switch-chat

# ⚖️ Сбалансированная - V3 модель  
make switch-v3

# 🚀 Экспериментальная - Gemini 2.0
make switch-gemini
```

### Быстрые комбинации:
```bash
# Переключить на R1 и запустить веб-интерфейс
make switch-r1 && make web

# Переключить на базовую модель и протестировать
make switch-chat && make test-enhanced
```

## 🌐 Запуск веб-интерфейса

```bash
# Запуск на порту 8501 (по умолчанию)
make web

# Запуск на другом порту
make web PORT=8502

# Режим разработки с горячей перезагрузкой
make dev
```

## 🧪 Тестирование

### Быстрые тесты:
```bash
# Демонстрация возможностей системы
make demo

# Тест улучшенной RAG системы
make test-enhanced

# Тест конкретной модели
make test MODEL=deepseek/deepseek-chat
```

### Комплексные тесты:
```bash
# Тест всех моделей подряд
make test-all

# Полный бенчмарк
make benchmark

# Просмотр результатов
make results
```

## 📊 Управление индексом

```bash
# Статус индекса
make status

# Создание/проверка индекса
make index

# Пересоздание индекса
make rebuild
```

## 🔍 Диагностика

```bash
# Проверка окружения (покажет текущую модель!)
make check

# Структура проекта
make structure

# Очистка временных файлов
make clean
```

## 💡 Рекомендуемые workflows

### Для ежедневного использования:
```bash
make switch-r1    # Лучшая модель
make web          # Веб-интерфейс
```

### Для разработки:
```bash
make switch-r1    # Настройка модели
make dev          # Режим разработки
```

### Для тестирования:
```bash
make demo         # Быстрая демонстрация
make test-enhanced # Тест системы
make benchmark    # Полный бенчмарк
```

### Для нового проекта:
```bash
make setup        # Полная настройка
make web          # Запуск интерфейса
```

## 🤖 Сравнение способов переключения моделей

### 1. **Makefile (рекомендуется для командной строки)**
```bash
make switch-r1          # Быстро и просто
make models             # Показать все модели
```

### 2. **Веб-интерфейс (рекомендуется для интерактивной работы)**
- Откройте http://localhost:8501
- В боковой панели: "🤖 Модель для ответов"
- Выберите модель из списка

### 3. **Прямые команды**
```bash
python switch_model.py --list
python switch_model.py --switch deepseek/deepseek-r1:free
```

## 🎯 Какой способ выбрать?

- **Makefile** - для быстрого переключения через терминал
- **Веб-интерфейс** - для интерактивной работы с вопросами
- **Прямые команды** - для автоматизации и скриптов

## ⚙️ Полезные алиасы

Можете добавить в ваш `.bashrc` или `.zshrc`:

```bash
# Алиасы для RAG системы
alias rag-web="cd /_geol/projects/nas/lysobacters && make web"
alias rag-r1="cd /_geol/projects/nas/lysobacters && make switch-r1"
alias rag-chat="cd /_geol/projects/nas/lysobacters && make switch-chat"
alias rag-test="cd /_geol/projects/nas/lysobacters && make test-enhanced"
alias rag-models="cd /_geol/projects/nas/lysobacters && make models"
```

Тогда сможете использовать:
```bash
rag-r1       # Переключение на R1
rag-web      # Запуск веб-интерфейса
rag-test     # Быстрый тест
```

## 🔥 Горячие комбинации

```bash
# Лучшая модель + веб-интерфейс
make switch-r1 && make web

# Быстрая проверка работоспособности
make switch-r1 && make demo

# Полная настройка с нуля
make setup && make web

# Тест всех моделей
make test-all && make results
```

## 🎉 Итог

Makefile значительно упрощает работу с системой! 

**Для ежедневного использования:**
1. `make switch-r1` - переключение на лучшую модель
2. `make web` - запуск веб-интерфейса  
3. Работайте в браузере с переключением моделей в интерфейсе

**Максимально просто и эффективно! 🚀** 