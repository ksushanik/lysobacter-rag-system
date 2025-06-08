#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_fact_checker():
    """Тест fact_checker"""
    try:
        from lysobacter_rag.rag_pipeline.fact_checker import FactChecker
        print("✅ Импорт fact_checker OK")
        
        fact_checker = FactChecker()
        print("✅ Инициализация fact_checker OK")
        
        # Тестируем простую проверку
        test_chunks = [
            {
                'text': 'temperature range for growth is 15–37°C',
                'metadata': {'source': 'test'}
            }
        ]
        
        result = fact_checker.check_temperature_claim(
            "15-42°C", 
            test_chunks, 
            "YC5194"
        )
        
        print(f"✅ Проверка температуры: {result.fact} -> {'точно' if result.is_accurate else 'неточно'}")
        print(f"   Доказательство: {result.evidence[:100]}...")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fact_checker() 