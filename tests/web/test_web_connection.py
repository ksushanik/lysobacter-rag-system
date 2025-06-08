#!/usr/bin/env python3

import requests
import time

def test_web_connection():
    """Тестирует подключение к веб-интерфейсу"""
    
    print("🌐 Тестирование веб-интерфейса...")
    
    try:
        # Проверяем доступность
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Веб-интерфейс доступен!")
            print("🔗 Откройте: http://localhost:8501")
            
            # Проверим основную страницу
            main_response = requests.get("http://localhost:8501", timeout=10)
            if main_response.status_code == 200:
                print("✅ Главная страница загружается")
            else:
                print(f"⚠️ Главная страница: статус {main_response.status_code}")
        else:
            print(f"❌ Веб-интерфейс недоступен: статус {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Соединение отклонено - проверьте что Streamlit запущен")
        print("💡 Выполните: make web")
    except requests.exceptions.Timeout:
        print("❌ Тайм-аут соединения")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_web_connection() 