#!/usr/bin/env python3
"""
Сравнение протестированных моделей для RAG-системы
"""

def show_model_comparison():
    """Показывает сравнение протестированных моделей"""
    
    print("🔬 СРАВНЕНИЕ МОДЕЛЕЙ ДЛЯ RAG-СИСТЕМЫ")
    print("=" * 80)
    
    models = [
        {
            "name": "DeepSeek Chat",
            "id": "deepseek/deepseek-chat",
            "cost": "🆓 Бесплатная",
            "russian": "✅ Отлично",
            "english": "✅ Отлично", 
            "science": "✅ Хорошие знания о лизобактериях",
            "structure": "✅ Хорошо структурированные ответы",
            "speed": "🟡 Средняя",
            "limits": "✅ Нет жестких лимитов",
            "reliability": "✅ Стабильная",
            "score": "9/10",
            "recommendation": "🌟 РЕКОМЕНДУЕТСЯ для RAG"
        },
        {
            "name": "Google Gemini 2.0 Flash", 
            "id": "google/gemini-2.0-flash-exp:free",
            "cost": "🆓 Бесплатная",
            "russian": "✅ Отлично",
            "english": "✅ Отлично",
            "science": "✅ Хорошие знания (из протестированного)",
            "structure": "✅ Хорошо структурированные ответы",
            "speed": "🟢 Быстрая",
            "limits": "❌ Жесткие лимиты (3-5 запросов)",
            "reliability": "⚠️ Частые блокировки",
            "score": "6/10",
            "recommendation": "⚠️ НЕ подходит для интенсивного RAG"
        },
        {
            "name": "DeepSeek R1 Qwen",
            "id": "deepseek/deepseek-r1-0528-qwen3-8b:free", 
            "cost": "🆓 Бесплатная",
            "russian": "❌ Пустые ответы",
            "english": "❌ Пустые ответы",
            "science": "❌ Не протестировано",
            "structure": "❌ Нет ответов",
            "speed": "🟡 Средняя",
            "limits": "✅ Нет проблем с лимитами",
            "reliability": "❌ Не работает корректно",
            "score": "2/10",
            "recommendation": "❌ НЕ рекомендуется"
        }
    ]
    
    for model in models:
        print(f"\n📋 **{model['name']}**")
        print(f"   ID: {model['id']}")
        print(f"   💰 Стоимость: {model['cost']}")
        print(f"   🇷🇺 Русский язык: {model['russian']}")
        print(f"   🇺🇸 Английский язык: {model['english']}")
        print(f"   🔬 Научные знания: {model['science']}")
        print(f"   📝 Структурированность: {model['structure']}")
        print(f"   ⚡ Скорость: {model['speed']}")
        print(f"   ⏱️ Лимиты: {model['limits']}")
        print(f"   🔄 Надежность: {model['reliability']}")
        print(f"   ⭐ Общая оценка: {model['score']}")
        print(f"   💡 Рекомендация: {model['recommendation']}")
        print("-" * 80)
    
    print("\n🎯 **ИТОГОВАЯ РЕКОМЕНДАЦИЯ:**")
    print("✅ **DeepSeek Chat** - лучший выбор для вашей RAG-системы!")
    print("   • Стабильная работа без жестких лимитов")
    print("   • Отличное качество ответов на русском и английском")
    print("   • Хорошие знания в области микробиологии")
    print("   • Подходит для интенсивного использования в RAG")
    
    print("\n🔄 **Альтернативы:**")
    print("• Если нужна максимальная скорость - можно попробовать Gemini в периоды низкой нагрузки")
    print("• Для коммерческого использования - рассмотрите платные модели OpenAI или Anthropic")
    
    print("\n🚀 **Следующие шаги:**")
    print("1. Установите DeepSeek Chat как основную модель")
    print("2. Запустите полную RAG-систему: python main.py")
    print("3. Протестируйте на реальных вопросах о лизобактериях")

if __name__ == "__main__":
    show_model_comparison() 