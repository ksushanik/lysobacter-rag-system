#!/usr/bin/env python3
"""
🌐 Простой тест доступности веб-интерфейса
"""
import requests
import time
import sys

def test_web_interface(port=8501):
    """Тестирует доступность веб-интерфейса"""
    
    url = f"http://localhost:{port}"
    
    print(f"🌐 Тестирую доступность веб-интерфейса: {url}")
    print("⏳ Ожидание запуска сервера...")
    
    # Ждем до 30 секунд
    for attempt in range(30):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ Веб-интерфейс доступен!")
                print(f"🔗 Откройте браузер по адресу: {url}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Попытка {attempt + 1}/30...")
        time.sleep(1)
    
    print(f"❌ Веб-интерфейс недоступен по адресу {url}")
    print("💡 Попробуйте:")
    print("   1. Проверить, запущен ли процесс: ps aux | grep streamlit")
    print("   2. Перезапустить: make web")
    print("   3. Проверить логи")
    return False

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    test_web_interface(port) 