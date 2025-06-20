# РУКОВОДСТВО ПО ТЕСТИРОВАНИЮ ВЕБ-ИНТЕРФЕЙСА

*Версия: 2.0 | Дата: 08.06.2025*

## ЦЕЛЬ ТЕСТИРОВАНИЯ

Демонстрация улучшений в системе сравнительного анализа лизобактерий после Итерации 1.

---

## ПЛАН ТЕСТИРОВАНИЯ

### 1. ОСНОВНОЙ ТЕСТ: Морфологическое сравнение

**Проблемный запрос (который ранее провалился):**
```
Сравните морфологические характеристики различных лизобактерий
```

**Ожидаемые результаты:**
- Анализ 60+ видов Lysobacter
- Сводная таблица с характеристиками
- Структурированный ответ с выводами
- Высокая уверенность (0.8+)

**Старый результат:** "Контекст не содержит информации..."

---

### 2. ДОПОЛНИТЕЛЬНЫЕ СРАВНИТЕЛЬНЫЕ ЗАПРОСЫ

#### A. Физиологическое сравнение:
```
Какие различия в условиях роста существуют между видами Lysobacter?
```

#### B. Экологическое сравнение:
```
Сравните экологические ниши различных лизобактерий
```

#### C. Общее сравнение:
```
Какие общие черты и различия характерны для рода Lysobacter?
```

#### D. Специфичные различия:
```
В чем различия между Lysobacter capsici и Lysobacter antarcticus?
```

---

### 3. КОНТРОЛЬНЫЕ ТЕСТЫ

Убедиться, что стандартная функциональность не пострадала:

#### Специфичные запросы о штаммах:
```
Что известно о штамме YC5194?
Какова морфология штамма GW1-59T?
```

#### Табличные данные:
```
Покажите биохимические характеристики лизобактерий
```

---

## КРИТЕРИИ ОЦЕНКИ

### Успешное тестирование:
1. **Определение типа запроса**: Система правильно распознает сравнительные запросы
2. **Множественные виды**: Анализируется 10+ видов
3. **Структурированный ответ**: Есть заголовки, таблицы, выводы
4. **Высокое качество**: Уверенность 0.5+
5. **Скорость**: Ответ в течение 15-30 секунд

### Проблемы для внимания:
- Ответ "нет данных" на сравнительные запросы
- Анализ менее 5 видов
- Отсутствие структуры в ответе
- Низкая уверенность (<0.3)
- Слишком долгий ответ (>60 сек)

---

## СЦЕНАРИИ ТЕСТИРОВАНИЯ

### Сценарий 1: Демонстрация главного улучшения
1. Откройте веб-интерфейс: `http://localhost:8501`
2. Введите: `Сравните морфологические характеристики различных лизобактерий`
3. Нажмите "Выполнить структурированный анализ"
4. **Ожидайте**: Детальный анализ 60+ видов с таблицей

### Сценарий 2: Тестирование различных типов сравнения
1. Протестируйте каждый из дополнительных запросов
2. Обратите внимание на:
   - Тип определяемого анализа
   - Количество анализируемых видов
   - Качество структурирования

### Сценарий 3: Проверка стабильности
1. Протестируйте контрольные запросы
2. Убедитесь, что стандартная функциональность работает
3. Проверьте время ответа

---

## ОЖИДАЕМЫЕ УЛУЧШЕНИЯ

### ДО (Старая система):
```
Запрос: "Сравните морфологические характеристики различных лизобактерий"
Ответ: "Предоставленный контекст не содержит информации о морфологических характеристиках различных видов лизобактерий."
Видов проанализировано: 0
Качество: 0%
```

### ПОСЛЕ (Новая система):
```
Запрос: "Сравните морфологические характеристики различных лизобактерий"
Ответ: Детальный сравнительный анализ с таблицами и выводами
Видов проанализировано: 63
Качество: 100%
Уверенность: 0.80
Структурированный формат с заголовками
```

---

## ДЕТАЛИ ДЛЯ ПРОВЕРКИ

### В сравнительном ответе должны быть:
1. **Заголовок**: "СРАВНИТЕЛЬНЫЙ АНАЛИЗ..."
2. **Общие черты**: Секция с характеристиками рода
3. **Видовые различия**: Список видов с их особенностями
4. **Сводная таблица**: Markdown таблица с характеристиками
5. **Выводы**: Резюме с таксономическим значением

### Технические индикаторы:
- Тип анализа: `comparative`
- Количество видов: 50+
- Источников: 20+
- Время ответа: 15-30 сек

---

## ДЕМОНСТРАЦИЯ РЕЗУЛЬТАТОВ

После тестирования вы увидите:

1. **Значительное улучшение**: От "нет данных" к анализу 60+ видов
2. **Новая функциональность**: Сравнительный анализ с таблицами
3. **Высокое качество**: Структурированные, информативные ответы
4. **Стабильность**: Все старые функции работают как прежде

**Система демонстрирует высокое качество сравнительного анализа научной литературы.**

---

## ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ

- **URL**: http://localhost:8501
- **Порт**: 8501
- **Модель**: GPT-4 через OpenRouter
- **База данных**: ChromaDB с 8042 чанками
- **Время работы**: 24/7 режим

## ГОТОВНОСТЬ К ТЕСТИРОВАНИЮ

Система запущена и готова продемонстрировать улучшения в сравнительном анализе лизобактерий. 