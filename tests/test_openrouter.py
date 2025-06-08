#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к OpenRouter API
"""

from config import config
from openai import OpenAI

def test_openrouter_connection():
    """Тестирует подключение к OpenRouter API"""
    
    print("=== Тест подключения к OpenRouter API ===")
    
    # Проверяем наличие API ключа
    if not config.OPENAI_API_KEY:
        print("❌ ОШИБКА: API ключ не найден!")
        print("Убедитесь, что в файле .env указан OPENROUTER_API_KEY")
        return False
    
    print(f"✅ API ключ найден (длина: {len(config.OPENAI_API_KEY)} символов)")
    
    # Проверяем модель
    model = config.OPENAI_MODEL
    print(f"🤖 Используемая модель: {model}")
    
    # Инициализируем клиент
    try:
        if hasattr(config, 'OPENROUTER_API_KEY') and config.OPENROUTER_API_KEY and config.OPENROUTER_API_KEY != "your_openrouter_api_key_here":
            client = OpenAI(
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.OPENROUTER_BASE_URL
            )
            print(f"🌐 Подключение к OpenRouter: {config.OPENROUTER_BASE_URL}")
        else:
            if config.OPENAI_API_KEY == "your_openrouter_api_key_here":
                print("⚠️ Обнаружен шаблонный API ключ. Замените на реальный ключ в файле .env")
                return False
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            print("🌐 Подключение к стандартному OpenAI API")
        
        # Отправляем тестовый запрос
        print("\n📤 Отправляю тестовый запрос...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Привет! Это тестовое сообщение. Ответь кратко."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"📨 Ответ получен: {answer}")
        
        # Проверяем информацию об использовании
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"📊 Использование токенов: {usage.prompt_tokens} + {usage.completion_tokens} = {usage.total_tokens}")
        
        print("✅ Тест успешно пройден!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА при подключении: {str(e)}")
        print("\nВозможные причины:")
        print("1. Неверный API ключ")
        print("2. Недостаточно средств на счету")
        print("3. Проблемы с интернет-соединением")
        print("4. Неподдерживаемая модель")
        return False

def show_available_models():
    """Показывает популярные модели, доступные в OpenRouter"""
    
    print("\n=== Популярные модели в OpenRouter ===")
    
    models = [
        ("deepseek/deepseek-r1-0528-qwen3-8b:free", "🆓 DeepSeek R1 - БЕСПЛАТНАЯ мощная модель (рекомендуется!)"),
        ("openai/gpt-3.5-turbo", "OpenAI GPT-3.5 Turbo - быстрая и экономичная"),
        ("openai/gpt-4", "OpenAI GPT-4 - более мощная модель"),
        ("openai/gpt-4-turbo-preview", "OpenAI GPT-4 Turbo - последняя версия"),
        ("anthropic/claude-3-sonnet", "Anthropic Claude 3 Sonnet - отличная для анализа"),
        ("anthropic/claude-3-haiku", "Anthropic Claude 3 Haiku - быстрая"),
        ("meta-llama/llama-2-70b-chat", "Meta Llama 2 70B - мощная open-source модель"),
        ("google/palm-2-chat-bison", "Google PaLM 2 - от Google"),
        ("mistralai/mistral-7b-instruct", "Mistral 7B - экономичная европейская модель"),
        ("deepseek/deepseek-chat", "DeepSeek Chat - продвинутая модель от DeepSeek"),
        ("qwen/qwen-2-72b-instruct", "Qwen 2 72B - мощная китайская модель")
    ]
    
    for model_id, description in models:
        print(f"• {model_id}")
        print(f"  {description}")
        print()
    
    print("Для смены модели измените OPENROUTER_MODEL в файле .env")

if __name__ == "__main__":
    success = test_openrouter_connection()
    
    if success:
        show_available_models()
    
    print(f"\n{'='*50}")
    print("Для запуска основной системы используйте:")
    print("python main.py") 