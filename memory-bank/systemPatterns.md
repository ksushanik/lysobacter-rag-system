# Системные паттерны - Lysobacter RAG System

## Архитектурные паттерны

### Модульная архитектура
Система построена по принципу разделения ответственности:

```
src/lysobacter_rag/
├── pdf_extractor/          # Извлечение данных из PDF
│   ├── advanced_pdf_extractor.py  # Продвинутый экстрактор
│   ├── scientific_chunker.py      # Умное разбиение на чанки
│   └── pdf_extractor.py           # Базовый экстрактор
├── indexer/               # Векторная индексация
│   └── indexer.py         # ChromaDB + sentence-transformers
├── rag_pipeline/          # RAG логика
│   └── rag_pipeline.py    # Поиск + генерация ответов
├── data_processor/        # Обработка данных
└── utils/                 # Вспомогательные утилиты
```

### Паттерн "Pipeline"
RAG процесс реализован как пайплайн:
1. **Extract** → извлечение из PDF
2. **Process** → обработка и чанкинг
3. **Index** → создание векторных эмбеддингов
4. **Search** → семантический поиск
5. **Generate** → генерация ответа через LLM

### Паттерн "Strategy"
Множественные стратегии извлечения PDF:
- PyMuPDF4LLM для текста
- pdfplumber для таблиц  
- tabula для дополнительных таблиц
- Автоматический выбор лучшего метода

## Ключевые компоненты

### 1. PDF Extractor
```python
class AdvancedPDFExtractor:
    def extract_document(self, pdf_path):
        # Многоуровневое извлечение
        text_elements = self._extract_with_pymupdf4llm()
        tables = self._extract_tables_pdfplumber()
        additional_tables = self._extract_tables_tabula()
        return combined_elements
```

### 2. Scientific Chunker
```python
class ScientificChunker:
    def chunk_extracted_elements(self, elements):
        # Умное разбиение с учетом научного контекста
        # Сохранение целостности таблиц и разделов
        return smart_chunks
```

### 3. Vector Indexer
```python
class Indexer:
    def __init__(self):
        self.embedding_model = SentenceTransformer()
        self.chroma_client = chromadb.PersistentClient()
        
    def index_chunks(self, chunks):
        # Батчевая индексация с дедупликацией
        embeddings = self.embedding_model.encode(texts)
        self.collection.add(embeddings, metadatas, documents)
```

### 4. RAG Pipeline
```python
class RAGPipeline:
    def ask_question(self, query):
        # 1. Семантический поиск
        relevant_chunks = self.indexer.search(query)
        # 2. Построение контекста
        context = self._build_context(relevant_chunks)
        # 3. Генерация ответа
        answer = self._generate_answer(query, context)
        return result
```

## Паттерны интеграции

### OpenRouter Integration
Единый интерфейс для множества LLM моделей:
```python
self.openai_client = OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_BASE_URL
)
```

### Configuration Pattern
Централизованная конфигурация в `config.py`:
- API ключи и модели
- Пути к данным и хранилищу
- Параметры обработки и поиска

### Command Pattern
Makefile обеспечивает единообразный интерфейс команд:
- `make web` - запуск веб-интерфейса
- `make switch-r1` - переключение модели
- `make test-enhanced` - тестирование

## Паттерны качества

### Resilience Pattern
Система устойчива к сбоям:
- Fallback методы извлечения PDF
- Graceful degradation при недоступности API
- Логирование и мониторинг ошибок

### Caching Pattern  
Векторная база ChromaDB обеспечивает:
- Персистентное хранение эмбеддингов
- Быстрый поиск без пересчета
- Инкрементальное добавление документов

### Factory Pattern
Создание экстракторов и процессоров:
```python
def create_extractor(use_advanced=True):
    if use_advanced:
        return AdvancedPDFExtractor()
    return PDFExtractor()
```

## Паттерны интерфейса

### Facade Pattern
Упрощенный интерфейс через основные классы:
```python
from lysobacter_rag import PDFExtractor, Indexer
# Скрывает сложность внутренней архитектуры
```

### Observer Pattern
Логирование через loguru:
```python
logger.info("Начинаю обработку PDF...")
# Централизованное отслеживание состояния системы
``` 