#!/usr/bin/env python3
"""
Простой тест модели DeepSeek через OpenRouter
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

def test_deepseek():
    """Простой тест DeepSeek модели"""
    
    print("🧪 Тест модели DeepSeek R1")
    print("=" * 40)
    
    # Получаем настройки
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-0528-qwen3-8b:free")
    base_url = "https://openrouter.ai/api/v1"
    
    if not api_key:
        print("❌ API ключ не найден в .env файле")
        return False
    
    print(f"✅ API ключ найден (длина: {len(api_key)})")
    print(f"🤖 Модель: {model}")
    print(f"🌐 URL: {base_url}")
    
    try:
        # Создаем клиент OpenAI для OpenRouter
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("\n📤 Отправляю тестовый запрос...")
        
        # Простой тестовый запрос
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user", 
                    "content": "Привет! Ответь кратко на русском языке: что такое лизобактерии?"
                }
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        answer = response.choices[0].message.content.strip()
        
        print("✅ Запрос выполнен успешно!")
        print(f"📨 Ответ модели:")
        print("-" * 40)
        print(answer)
        print("-" * 40)
        
        # Проверяем информацию об использовании
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            print(f"📊 Использовано токенов: {usage.total_tokens}")
            print(f"   - Запрос: {usage.prompt_tokens}")
            print(f"   - Ответ: {usage.completion_tokens}")
        
        # Простая оценка качества
        score = 0
        if len(answer) > 20:
            score += 1
        if 'лизобактер' in answer.lower() or 'бактер' in answer.lower():
            score += 1
        if any(c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for c in answer.lower()):
            score += 1
        
        print(f"⭐ Оценка качества: {score}/3")
        
        if score >= 2:
            print("🎉 Модель работает отлично для RAG-системы!")
        else:
            print("⚠️ Модель работает, но качество ответов требует проверки")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        
        # Дополнительная диагностика
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg:
            print("💡 Возможно, неверный API ключ")
        elif "403" in error_msg or "forbidden" in error_msg:
            print("💡 Возможно, недостаточно прав или средств")
        elif "404" in error_msg or "not found" in error_msg:
            print("💡 Возможно, модель не найдена или недоступна")
        elif "rate" in error_msg or "limit" in error_msg:
            print("💡 Превышен лимит запросов")
        else:
            print("💡 Проверьте интернет-соединение и настройки")
        
        return False

if __name__ == "__main__":
    success = test_deepseek()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Тест пройден! Модель готова к использованию.")
        print("\n🚀 Следующие шаги:")
        print("1. python main.py - для обработки PDF и запуска RAG")
        print("2. streamlit run streamlit_app.py - для веб-интерфейса")
    else:
        print("❌ Тест не пройден. Проверьте настройки.") 