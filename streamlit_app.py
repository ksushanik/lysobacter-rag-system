"""
RAG-система для анализа научной литературы о лизобактериях
Облачная версия для Streamlit Cloud
"""

import streamlit as st
import sys
import os
import tempfile
import requests
from pathlib import Path
import json

# Настройка страницы
st.set_page_config(
    page_title="Lysobacter RAG System - Cloud Demo",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок
st.title("🔬 RAG-система для анализа научной литературы о лизобактериях")
st.subheader("Облачная демонстрационная версия")

# Предупреждение о демо версии
st.warning("""
**Демонстрационная версия**
Это упрощенная версия системы для демонстрации. 
Полная версия с векторной базой данных (8000+ фрагментов) доступна в локальной установке.
""")

def load_demo_data():
    """Загружает демонстрационные данные"""
    demo_docs = [
        {
            "title": "Lysobacter capsici sp. nov.",
            "content": "Штамм GW1-59T представляет новый вид Lysobacter capsici. Клетки палочковидные, 0.5-0.8 × 1.5-3.0 мкм. Грамотрицательные, подвижные. Оптимальная температура роста 28°C, pH 7.0-7.5.",
            "metadata": {"source": "Demo", "type": "taxonomic"}
        },
        {
            "title": "Lysobacter antibioticus YC5194",
            "content": "Штамм YC5194 выделен из почвы. Обладает антибактериальной активностью против патогенов растений. Производит β-лактамные антибиотики и другие биоактивные соединения.",
            "metadata": {"source": "Demo", "type": "bioactivity"}
        },
        {
            "title": "Морфологические характеристики лизобактерий",
            "content": "Лизобактерии - палочковидные бактерии размером 0.3-0.8 × 1.2-5.0 мкм. Клетки подвижные благодаря полярным жгутикам. Образуют желтые колонии на питательных средах.",
            "metadata": {"source": "Demo", "type": "morphology"}
        }
    ]
    return demo_docs

def demo_rag_query(query, docs):
    """Простой демо-поиск по документам"""
    query_lower = query.lower()
    results = []
    
    # Простой поиск по ключевым словам
    for doc in docs:
        score = 0
        content_lower = doc['content'].lower()
        
        # Проверка релевантности
        if 'gw1-59t' in query_lower and 'gw1-59t' in content_lower:
            score += 0.9
        elif 'yc5194' in query_lower and 'yc5194' in content_lower:
            score += 0.9
        elif 'морфолог' in query_lower and ('морфолог' in content_lower or 'размер' in content_lower):
            score += 0.8
        elif any(word in content_lower for word in query_lower.split() if len(word) > 3):
            score += 0.5
        
        if score > 0:
            results.append((doc, score))
    
    # Сортировка по релевантности
    results.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in results[:3]]

def generate_demo_answer(query, relevant_docs):
    """Генерирует демо-ответ на основе найденных документов"""
    if not relevant_docs:
        return "К сожалению, в демонстрационной версии не найдена релевантная информация по вашему запросу."
    
    # Базовые шаблоны ответов
    if 'gw1-59t' in query.lower():
        return """
        **Штамм GW1-59T (Lysobacter capsici sp. nov.)**
        
        🔬 **Морфология:**
        - Палочковидные клетки размером 0.5-0.8 × 1.5-3.0 мкм
        - Грамотрицательные бактерии
        - Подвижные (наличие жгутиков)
        
        🌡️ **Условия роста:**
        - Оптимальная температура: 28°C
        - Оптимальный pH: 7.0-7.5
        
        📚 **Источник:** Демонстрационные данные
        """
    
    elif 'yc5194' in query.lower():
        return """
        **Штамм YC5194 (Lysobacter antibioticus)**
        
        🌱 **Происхождение:** Выделен из почвы
        
        💊 **Биологическая активность:**
        - Антибактериальная активность против патогенов растений
        - Производство β-лактамных антибиотиков
        - Синтез других биоактивных соединений
        
        🎯 **Применение:** Биоконтроль в сельском хозяйстве
        
        📚 **Источник:** Демонстрационные данные
        """
    
    else:
        return f"""
        **Результаты поиска**
        
        Найдено {len(relevant_docs)} релевантных документов:
        
        {chr(10).join([f"• {doc['title']}: {doc['content'][:200]}..." for doc in relevant_docs])}
        
        📚 **Источник:** Демонстрационные данные
        """

# Боковая панель с информацией
with st.sidebar:
    st.header("ℹ️ О системе")
    st.info("""
    **Демо версия включает:**
    - 3 образца документов
    - Базовый поиск по ключевым словам
    - Простую генерацию ответов
    
    **Полная версия содержит:**
    - 8000+ фрагментов из 87 PDF
    - Векторный семантический поиск
    - Интеграцию с LLM моделями
    - Сравнительный анализ видов
    """)
    
    st.header("🎯 Примеры запросов")
    st.code("""
    • Что известно о штамме GW1-59T?
    • Расскажи о штамме YC5194
    • Какие морфологические характеристики у лизобактерий?
    """)
    
    st.header("🔗 Полная версия")
    st.markdown("""
    [GitHub Repository](https://github.com/ksushanik/lysobacter-rag-system)
    
    Для полнофункциональной версии см. инструкции по установке в README.
    """)

# Основной интерфейс
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Задайте вопрос")
    
    # Поле ввода
    query = st.text_area(
        "Введите ваш вопрос о лизобактериях:",
        placeholder="Например: Что известно о штамме GW1-59T?",
        height=100
    )
    
    # Кнопки
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        search_btn = st.button("🔍 Поиск", type="primary", use_container_width=True)
    with col_btn2:
        clear_btn = st.button("🗑️ Очистить", use_container_width=True)

with col2:
    st.header("📊 Статистика демо")
    st.metric("Документов", "3")
    st.metric("Типов данных", "3")
    st.metric("Штаммов", "2")

# Обработка запроса
if search_btn and query:
    with st.spinner("Обрабатываю запрос..."):
        # Загрузка демо данных
        demo_docs = load_demo_data()
        
        # Поиск релевантных документов
        relevant_docs = demo_rag_query(query, demo_docs)
        
        # Генерация ответа
        answer = generate_demo_answer(query, relevant_docs)
        
        # Отображение результатов
        st.header("📋 Результат анализа")
        st.markdown(answer)
        
        # Дополнительная информация
        if relevant_docs:
            with st.expander("📚 Использованные источники"):
                for i, doc in enumerate(relevant_docs, 1):
                    st.write(f"**{i}. {doc['title']}**")
                    st.write(doc['content'])
                    st.write(f"*Тип: {doc['metadata']['type']}*")
                    st.divider()

elif clear_btn:
    st.rerun()

# Подвал
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Lysobacter RAG System</strong> - Демонстрационная версия</p>
    <p>Система анализа научной литературы о лизобактериях</p>
    <p>© 2025 ksushanik | MIT License</p>
</div>
""", unsafe_allow_html=True) 