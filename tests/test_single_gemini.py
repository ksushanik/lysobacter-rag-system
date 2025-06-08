#!/usr/bin/env python3
"""
Одиночный тест для Gemini после паузы
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_single_gemini():
    """Тест одного запроса к Gemini"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    print(f"🧪 Тест восстановления Gemini: {model}")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Кратко расскажи о лизобактериях"}],
            max_tokens=200,
            temperature=0.1
        )
        
        answer = response.choices[0].message.content
        print(f"✅ Ответ получен:")
        print(f"📨 {answer}")
        
        if hasattr(response, 'usage') and response.usage:
            print(f"📊 Токены: {response.usage.total_tokens}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_single_gemini() 