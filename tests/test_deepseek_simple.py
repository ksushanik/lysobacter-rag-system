#!/usr/bin/env python3
"""
Простейший тест для DeepSeek с разными типами запросов
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_different_prompts():
    """Тестируем разные типы промптов"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    test_prompts = [
        "Hello! Can you respond in English?",
        "Что такое бактерии?",
        "2+2=?",
        "Расскажи о лизобактериях кратко",
        "What are lysobacter bacteria?"
    ]
    
    print(f"🧪 Тестирование модели: {model}")
    print("=" * 50)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Тест {i}: {prompt}")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            print(f"📨 Ответ: '{answer}'")
            print(f"📏 Длина: {len(answer) if answer else 0} символов")
            
            if answer and len(answer.strip()) > 0:
                print("✅ Ответ получен")
            else:
                print("⚠️ Пустой ответ")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_different_prompts() 