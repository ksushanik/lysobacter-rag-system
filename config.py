"""
Конфигурационный файл для RAG-системы обработки PDF лизобактов
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config:
    """Класс конфигурации для RAG-системы"""
    
    # Основные пути
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    STORAGE_DIR = PROJECT_ROOT / "storage"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # OpenRouter API (поддерживает совместимость с OpenAI API)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Список доступных моделей для тестирования
    AVAILABLE_MODELS = [
        "google/gemini-2.5-flash-preview-05-20", # Google Gemini 2.5 Flash Preview (качество)
        "deepseek/deepseek-r1-0528-qwen3-8b",    # DeepSeek R1 Qwen3 8B (экономичная!)
        "deepseek/deepseek-r1-0528-qwen3-8b:free", # DeepSeek R1 Qwen3 8B (бесплатная)
        "deepseek/deepseek-r1:free",             # R1 модель для рассуждений
        "deepseek/deepseek-chat",                # Базовая модель DeepSeek
        "deepseek/deepseek-v3-base:free",        # Новая базовая модель v3
        "deepseek/deepseek-chat-v3-0324:free",   # Чат модель v3
        "google/gemini-2.0-flash-exp:free"       # Google Gemini 2.0 Flash
    ]
    
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-preview-05-20")
    
    # Для обратной совместимости
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or OPENROUTER_API_KEY
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "") or OPENROUTER_MODEL
    
    # Настройки для извлечения таблиц
    TARGET_TITLE_PATTERNS = [
        "Differential characteristics among strain",
        "Phenotypic characteristics that differentiate strain", 
        "Phenotypic characteristics of strains",
        "Differential phenotypic characteristics of strain",
        "Characteristics differentiating strains",
        "Differential characteristics of strain",
        "Characteristics that differentiate strain",
        "Different characteristics between strain",
        "Phenotypic characteristics",
        "Differential characteristics",
        "Characteristics of strain"
    ]
    
    # Порог схожести для нечеткого поиска заголовков (в процентах)
    FUZZY_MATCH_THRESHOLD = 80
    
    # Настройки для разделения текста на чанки
    CHUNK_SIZE = 400  # размер чанка в символах
    CHUNK_OVERLAP = 50  # перекрытие между чанками
    
    # Настройки эмбеддингов
    EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # Многоязычная модель для русского и английского
    
    # Настройки ChromaDB
    CHROMA_DB_PATH = str(STORAGE_DIR / "chroma_db")
    CHROMA_COLLECTION_NAME = "lysobacter_knowledge_base"
    CHROMA_PERSIST_DIRECTORY = str(STORAGE_DIR / "chroma_db")
    
    # Настройки RAG
    RAG_TOP_K = 10  # количество релевантных чанков для ответа (увеличено для более полных ответов)
    RAG_TEMPERATURE = 0.1  # температура для генерации ответов
    
    # Настройки PDF экстрактора  
    USE_ENHANCED_EXTRACTOR = True  # Использовать улучшенный экстрактор с unstructured
    
    # Логирование
    LOG_LEVEL = "INFO"
    LOG_FILE = str(LOGS_DIR / "lysobacter_rag.log")
    
    # Создание необходимых директорий
    def __post_init__(self):
        """Создает необходимые директории при инициализации"""
        self.STORAGE_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)

# Создаем экземпляр конфигурации
config = Config()
config.__post_init__() 