#!/usr/bin/env python3
"""
Демо тест RAG-системы с реальным штаммом из обработанных файлов
"""

import os
from pathlib import Path
from config import config
from src.lysobacter_rag.data_processor import DataProcessor
from src.lysobacter_rag.indexer import Indexer
from src.lysobacter_rag.rag_pipeline import RAGPipeline

def create_demo_data():
    """Создаем демо данные из текста, который мы знаем"""
    
    # Создаем класс для эмуляции ExtractedDocument
    class DemoDoc:
        def __init__(self, text, doc_type, metadata):
            self.text = text
            self.text_content = text  # Это ожидает процессор
            self.doc_type = doc_type
            self.metadata = metadata
            self.tables = []  # Пустой список таблиц
            self.total_pages = 1  # Указываем одну страницу
            self.source_pdf = metadata.get('source_pdf', 'demo.pdf')
    
    # Эмулируем извлеченные данные о штаммах, которые мы видели в логах
    demo_docs = [
        DemoDoc(
            text='''
            Lysobacter daejeonensis sp. nov. strain GH1-9T and strain GH19-3T
            
            Phenotypic characteristics of strains GH1-9T, GH19-3T and other Lysobacter species.
            The strain GH1-9T was isolated from greenhouse soil and shows typical characteristics 
            of the genus Lysobacter. The cells are rod-shaped, Gram-negative, and motile.
            
            Growth occurs at temperatures from 15-42°C, with optimal growth at 28-30°C.
            The strain is positive for catalase and oxidase activities.
            
            Table 1. Phenotypic characteristics of strains GH1-9T, GH19-3T
            Characteristic     GH1-9T    GH19-3T    L. enzymogenes
            Temperature range  15-42°C   15-40°C    10-35°C
            Optimal temp      28-30°C   25-28°C    25-28°C
            pH range          6.0-9.0   6.5-8.5    6.0-8.0
            Catalase          +         +          +
            Oxidase           +         +          -
            ''',
            doc_type='text',
            metadata={
                'source_pdf': 'Lysobacter daejeonensis_sp_nov_a.pdf',
                'page_number': 1
            }
        ),
        DemoDoc(
            text='''
            Lysobacter mobilis sp. nov. strain 9NM-14T
            
            The characteristics of strain 9NM-14T are summarized in Table 1.
            Differential phenotypic characteristics of strain 9NM-14T compared to closely 
            related Lysobacter species.
            
            Strain 9NM-14T was isolated from rhizosphere soil and represents a novel species
            within the genus Lysobacter. The strain shows unique biochemical properties
            that distinguish it from other known species.
            
            Growth temperature: 15-40°C (optimum 25-30°C)
            pH range: 5.5-8.5 (optimum 7.0-7.5)
            NaCl tolerance: 0-3% (w/v)
            ''',
            doc_type='text',
            metadata={
                'source_pdf': 'Lysobacter mobilis.pdf',
                'page_number': 2
            }
        ),
        DemoDoc(
            text='''
            Lysobacter korlensis sp. nov. strains ZLD-17T and ZLD-29T
            
            Phenotypic characteristics of strains ZLD-17T and ZLD-29T and type strains 
            of species of the genus Lysobacter.
            
            Both strains were isolated from desert soil samples and show adaptations
            to arid environments. The strains are halotolerant and can grow in the
            presence of elevated salt concentrations.
            
            Key characteristics:
            - Cell morphology: Rod-shaped, 0.4-0.6 × 1.2-3.0 μm
            - Gram reaction: Negative
            - Motility: Positive (gliding motility)
            - Pigmentation: Yellow colonies on nutrient agar
            ''',
            doc_type='text',
            metadata={
                'source_pdf': 'Lysobacter korlensis.pdf', 
                'page_number': 1
            }
        )
    ]
    
    return demo_docs

def demo_rag_test():
    """Демо тест полной RAG-системы"""
    
    print("🧬 ДЕМО ТЕСТ RAG-СИСТЕМЫ ЛИЗОБАКТЕРИЙ")
    print("=" * 60)
    
    # Создаем демо данные
    print("📝 Создание демо данных...")
    demo_docs = create_demo_data()
    print(f"✅ Создано {len(demo_docs)} демо документов")
    
    # Обрабатываем данные
    print(f"\n🔄 Обработка данных...")
    processor = DataProcessor()
    chunks = processor.process_documents(demo_docs)
    print(f"✅ Создано {len(chunks)} чанков")
    
    # Создаем индекс
    print(f"\n🗃️ Создание векторного индекса...")
    indexer = Indexer()
    
    # Удаляем старую коллекцию
    try:
        indexer.delete_collection()
        print("🗑️ Старая коллекция удалена")
    except:
        print("ℹ️ Старой коллекции не было")
    
    indexer.index_chunks(chunks)
    print(f"✅ Индекс создан и загружен")
    
    # Тест поиска
    print(f"\n🔍 ТЕСТ ПОИСКА ПО ШТАММАМ")
    print("-" * 40)
    
    test_queries = [
        "GH1-9T",
        "штамм GH1-9T", 
        "Lysobacter daejeonensis",
        "9NM-14T",
        "ZLD-17T",
        "характеристики штаммов",
        "температура роста",
        "desert soil"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Поиск: '{query}'")
        results = indexer.search(query, top_k=2)
        
        if results:
            for i, result in enumerate(results, 1):
                relevance = result.get('relevance_score', 0)
                source = result.get('metadata', {}).get('source_pdf', 'Unknown')
                text_preview = result.get('text', '')[:150] + '...'
                
                print(f"   {i}. Релевантность: {relevance:.3f}")
                print(f"      Источник: {source}")
                print(f"      Текст: {text_preview}")
        else:
            print("   ❌ Результатов не найдено")
    
    # Тест RAG Q&A
    print(f"\n🤖 ТЕСТ RAG Q&A")
    print("-" * 40)
    
    try:
        rag = RAGPipeline()
        
        questions = [
            "Расскажи о штамме GH1-9T",
            "Какие температурные условия предпочитают штаммы Lysobacter?",
            "Где был выделен штамм 9NM-14T?",
            "Какие морфологические характеристики имеют штаммы ZLD-17T и ZLD-29T?"
        ]
        
        for question in questions:
            print(f"\n❓ Вопрос: {question}")
            
            try:
                response = rag.ask_question(question)
                
                print(f"💬 Ответ:")
                print(f"   {response['answer']}")
                print(f"📊 Источников: {response['num_sources_used']}")
                print(f"⭐ Уверенность: {response['confidence']:.2f}")
                
                if response.get('sources'):
                    print(f"📚 Источники: {', '.join(response['sources'])}")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка инициализации RAG: {e}")
        return False
    
    return True

def interactive_demo():
    """Интерактивный демо режим"""
    
    print(f"\n🎮 ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)
    print("Теперь вы можете задавать свои вопросы!")
    print("Введите 'exit' для выхода")
    print("-" * 40)
    
    try:
        rag = RAGPipeline()
        
        while True:
            question = input("\n❓ Ваш вопрос: ").strip()
            
            if question.lower() in ['exit', 'выход', 'quit']:
                print("👋 До свидания!")
                break
                
            if not question:
                continue
                
            try:
                response = rag.ask_question(question)
                
                print(f"\n💬 Ответ:")
                print(f"{response['answer']}")
                print(f"\n📊 Метрики: источников: {response['num_sources_used']}, уверенность: {response['confidence']:.2f}")
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")

if __name__ == "__main__":
    success = demo_rag_test()
    
    if success:
        print(f"\n🎉 ДЕМО ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        
        start_interactive = input(f"\n🎮 Запустить интерактивный режим? (y/n): ").strip().lower()
        
        if start_interactive in ['y', 'yes', 'да', 'д']:
            interactive_demo()
        else:
            print(f"\n💡 Для интерактивного режима запустите:")
            print(f"   python demo_test.py")
    else:
        print(f"\n❌ Демо тест не прошел. Проверьте конфигурацию.") 