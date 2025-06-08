"""
Streamlit интерфейс для RAG-системы лизобактерий
Профессиональная система поиска и анализа научной информации
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Добавляем пути для корректного импорта
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from config import config
from lysobacter_rag.indexer import Indexer

# Добавляем для работы с улучшенной системой
try:
    from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False


def get_quality_info(relevance):
    """Возвращает информацию о качестве релевантности"""
    if relevance >= 0.9:
        return {"label": "Отличное", "color": "green"}
    elif relevance >= 0.7:
        return {"label": "Хорошее", "color": "blue"}
    elif relevance >= 0.5:
        return {"label": "Среднее", "color": "orange"}
    elif relevance >= 0.3:
        return {"label": "Слабое", "color": "red"}
    else:
        return {"label": "Очень слабое", "color": "red"}


def update_model_config(selected_model):
    """Обновляет конфигурацию модели"""
    try:
        # Обновляем переменную окружения
        os.environ['OPENROUTER_MODEL'] = selected_model
        
        # Обновляем .env файл если он существует
        env_file = Path(".env")
        if env_file.exists():
            lines = []
            found = False
            
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('OPENROUTER_MODEL='):
                        lines.append(f'OPENROUTER_MODEL={selected_model}\n')
                        found = True
                    else:
                        lines.append(line)
            
            if not found:
                lines.append(f'OPENROUTER_MODEL={selected_model}\n')
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        
        # Важно: обновляем глобальный объект config
        config.OPENAI_MODEL = selected_model
        
        # Сохраняем в session_state для отслеживания
        st.session_state.current_model = selected_model
        
    except Exception as e:
        st.sidebar.error(f"Ошибка обновления модели: {e}")
        raise e


def model_selector():
    """Виджет выбора модели в боковой панели"""
    st.sidebar.markdown("---")
    st.sidebar.header("Языковая модель")
    
    # Список доступных моделей с описаниями
    model_options = {
        "google/gemini-2.5-flash-preview-05-20": "Gemini 2.5 Flash - Высокопроизводительная модель",
        "deepseek/deepseek-r1-0528-qwen3-8b": "R1 Qwen3 8B - Экономичная модель ($0.05/$0.10)",
        "deepseek/deepseek-r1-0528-qwen3-8b:free": "R1 Qwen3 8B - Бесплатная версия",
        "deepseek/deepseek-r1:free": "R1 - Модель рассуждений",
        "deepseek/deepseek-chat": "Chat - Базовая модель",
        "deepseek/deepseek-v3-base:free": "V3 Base - Сбалансированная модель",
        "deepseek/deepseek-chat-v3-0324:free": "V3 Chat - Диалоговая модель",
        "google/gemini-2.0-flash-exp:free": "Gemini 2.0 - Экспериментальная версия"
    }
    
    # Получаем текущую модель (приоритет у session_state)
    current_model = st.session_state.get('current_model', config.OPENAI_MODEL)
    
    # Создаем selectbox с описаниями
    model_labels = list(model_options.values())
    model_keys = list(model_options.keys())
    
    try:
        current_index = model_keys.index(current_model)
    except ValueError:
        current_index = 0
    
    selected_label = st.sidebar.selectbox(
        "Выберите модель:",
        model_labels,
        index=current_index,
        key="model_selector"
    )
    
    # Получаем выбранную модель
    selected_model = model_keys[model_labels.index(selected_label)]
    
    # Если модель изменилась, обновляем конфигурацию
    if selected_model != current_model:
        try:
            update_model_config(selected_model)
            st.sidebar.success(f"Модель изменена на: {selected_model}")
            # Сбрасываем кэш enhanced RAG если он есть
            if 'enhanced_rag' in st.session_state:
                del st.session_state.enhanced_rag
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Ошибка переключения модели: {str(e)}")
            # Откатываемся к предыдущей модели
            st.session_state.current_model = current_model
    
    # Показываем информацию о текущей модели
    st.sidebar.info(f"**Текущая модель:** {selected_model}")
    
    # Отладочная информация (можно убрать в продакшене)
    with st.sidebar.expander("Отладочная информация"):
        st.write(f"Config model: {config.OPENAI_MODEL}")
        st.write(f"Session model: {st.session_state.get('current_model', 'не установлена')}")
        st.write(f"Env model: {os.environ.get('OPENROUTER_MODEL', 'не установлена')}")
        st.write(f"Selected: {selected_model}")
        st.write(f"Current: {current_model}")
    
    # Рекомендации по использованию
    with st.sidebar.expander("Рекомендации по выбору модели"):
        st.write("**Gemini 2.5 Flash:**")
        st.write("• Высокое качество анализа")
        st.write("• Подходит для сложных задач")
        st.write("• Рекомендуется для исследований")
        st.write("")
        st.write("**R1 Qwen3 8B (экономичная):**")
        st.write("• Оптимальное соотношение цена/качество")
        st.write("• Хорошие возможности рассуждений")
        st.write("• Подходит для регулярного использования")
        st.write("")
        st.write("**R1 Qwen3 8B (бесплатная):**")
        st.write("• Без ограничений по стоимости")
        st.write("• Подходит для экспериментов")
        st.write("• Базовые аналитические возможности")


def init_indexer():
    """Инициализация индексера"""
    if 'indexer' not in st.session_state:
        with st.spinner('Загрузка базы знаний...'):
            try:
                indexer = Indexer()
                stats = indexer.get_collection_stats()
                
                if stats.get('total_chunks', 0) == 0:
                    st.error("База знаний пуста. Необходимо выполнить индексацию данных.")
                    st.stop()
                
                st.session_state.indexer = indexer
                st.session_state.stats = stats
                st.success(f"База знаний загружена: {stats['total_chunks']} фрагментов")
                
            except Exception as e:
                st.error(f"Ошибка загрузки базы знаний: {e}")
                st.stop()


def init_enhanced_rag():
    """Инициализация улучшенной RAG системы"""
    if ENHANCED_AVAILABLE and 'enhanced_rag' not in st.session_state:
        with st.spinner('Инициализация RAG системы...'):
            try:
                # Используем обновленный RAGPipeline
                enhanced_rag = RAGPipeline()
                st.session_state.enhanced_rag = enhanced_rag
                st.sidebar.success("RAG система инициализирована")
                st.sidebar.info("Используется обновленная база данных")
            except Exception as e:
                st.sidebar.error(f"Ошибка инициализации RAG: {e}")
                # Показываем подробности ошибки для отладки
                with st.sidebar.expander("Подробности ошибки"):
                    st.code(str(e))
                # Устанавливаем флаг что система недоступна
                st.session_state.enhanced_rag = None


def search_interface():
    """Интерфейс поиска"""
    st.title("RAG-система для анализа научной литературы о лизобактериях")
    
    # Показываем информацию о системе
    if ENHANCED_AVAILABLE:
        st.info("**Система автоматического анализа активна** - структурированные ответы с использованием специализированных алгоритмов обработки запросов")
        
        st.markdown("""
        **Доступные режимы работы:**
        - **Структурированный анализ** - для получения развернутых ответов с детальным анализом
        - **Поиск источников** - для быстрого поиска релевантных документов
        """)
    else:
        st.warning("Расширенная система анализа недоступна - используется базовый поиск")
    
    # Боковая панель со статистикой и выбором модели
    with st.sidebar:
        # Селектор модели
        model_selector()
        
        st.header("Статистика базы знаний")
        stats = st.session_state.stats
        
        st.metric("Всего фрагментов", stats.get('total_chunks', 0))
        
        chunk_types = stats.get('chunk_types', {})
        if chunk_types:
            st.write("**Типы фрагментов:**")
            for chunk_type, count in chunk_types.items():
                st.write(f"- {chunk_type}: {count}")
        
        st.metric("Документов-источников", stats.get('unique_sources', 0))
        
        st.write("---")
        st.write("**Настройки поиска:**")
        top_k = st.slider("Количество результатов", 1, 10, 5)
        
        search_type = st.selectbox(
            "Тип поиска",
            ["Все типы", "Только текст", "Только таблицы"],
            index=0
        )
        
        # Переключатель режимов
        if ENHANCED_AVAILABLE:
            use_enhanced = st.checkbox("Использовать расширенную RAG систему", value=True,
                                     help="Включает специализированные алгоритмы анализа и обработки запросов")
        else:
            use_enhanced = False
            st.warning("Расширенная RAG система недоступна")
        
        # Информация о релевантности
        with st.expander("Информация о релевантности"):
            st.write("**Шкала качества совпадения:**")
            st.write("90-100% = Отличное соответствие")
            st.write("70-90% = Хорошее соответствие")
            st.write("50-70% = Среднее соответствие")
            st.write("30-50% = Слабое соответствие")
            st.write("0-30% = Очень слабое соответствие")
            st.write("---")
            st.caption("Релевантность показывает степень соответствия найденного фрагмента вашему запросу.")
    
    # Основной интерфейс
    st.write("**Введите научный запрос о лизобактериях:**")
    
    # Примеры вопросов для разных типов анализа
    with st.expander("Примеры научных запросов"):
        st.write("**Анализ штаммов:**")
        example_queries_strain = [
            "Что известно о штамме GW1-59T?",
            "Какие характеристики штамма Lysobacter capsici YC5194?",
            "Дайте детальный анализ штамма с морфологическими данными"
        ]
        
        st.write("**Сравнительный анализ:**")
        example_queries_compare = [
            "Сравните морфологические характеристики различных лизобактерий",
            "В чем различия между штаммами по биохимическим свойствам?",
            "Какие дифференциальные признаки отличают виды?"
        ]
        
        st.write("**Методология:**")
        example_queries_methods = [
            "Объясните методы выделения лизобактерий",
            "Какие методы используются для идентификации?",
            "Как проводится анализ жирных кислот?"
        ]
        
        st.write("**Анализ данных:**")
        example_queries_tables = [
            "Проанализируйте данные дифференциальных таблиц",
            "Какие таблицы содержат биохимические характеристики?",
            "Интерпретируйте результаты сравнительных таблиц"
        ]
        
        # Кнопки для примеров
        all_examples = example_queries_strain + example_queries_compare + example_queries_methods + example_queries_tables
        
        for query in all_examples:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.query = query
    
    # Поле ввода запроса
    query = st.text_input(
        "Ваш запрос:",
        value=st.session_state.get('query', ''),
        placeholder="Введите научный запрос здесь...",
        key="search_input"
    )
    
    # Кнопки поиска
    col1, col2 = st.columns(2)
    
    with col1:
        if ENHANCED_AVAILABLE and use_enhanced:
            answer_clicked = st.button("Выполнить структурированный анализ", type="primary")
        else:
            answer_clicked = False
    
    with col2:
        search_clicked = st.button("Найти источники", type="secondary")
    
    # Выполняем поиск или генерацию ответа
    if (search_clicked or answer_clicked) and query.strip():
        if answer_clicked and use_enhanced:
            generate_enhanced_answer(query.strip())
        else:
            perform_search(query.strip(), top_k, search_type)
    elif (search_clicked or answer_clicked):
        st.warning("Пожалуйста, введите запрос")


def generate_enhanced_answer(query):
    """Генерирует развернутый ответ с помощью улучшенной RAG системы"""
    
    # Инициализируем enhanced RAG если нужно
    init_enhanced_rag()
    
    if 'enhanced_rag' not in st.session_state or st.session_state.enhanced_rag is None:
        st.error("Расширенная RAG система недоступна")
        st.info("Проверьте боковую панель для просмотра деталей ошибки")
        return
    
    with st.spinner('Выполняется структурированный анализ запроса...'):
        try:
            result = st.session_state.enhanced_rag.ask_question(query)
            
            # Отображаем результат
            st.success("Структурированный анализ завершен")
            
            # Информация о запросе
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Уверенность", f"{result.get('confidence', 0):.3f}")
            
            with col2:
                st.metric("Источников", result.get('num_sources_used', 0))
            
            with col3:
                st.metric("Режим", "Enhanced RAG")
            
            # Основной ответ
            st.markdown("### Результат анализа:")
            st.markdown(result.get('answer', 'Ответ не найден'))
            
            # Источники
            sources = result.get('sources', [])
            if sources:
                with st.expander(f"Источники информации ({len(sources)})"):
                    for i, source in enumerate(sources, 1):
                        metadata = source.get('metadata', {})
                        st.write(f"**{i}.** {metadata.get('source_pdf', 'Неизвестный документ')} "
                               f"(стр. {metadata.get('page_number', 'N/A')})")
                        
                        if metadata.get('chunk_type') == 'table':
                            st.write("   *Табличные данные*")
                        
                        # Показываем превью контента
                        content = source.get('text', '')
                        if len(content) > 200:
                            st.write(f"   {content[:200]}...")
                        else:
                            st.write(f"   {content}")
                        
                        st.write("---")
                        
        except Exception as e:
            st.error(f"Ошибка при выполнении анализа: {e}")
            
            # Показываем детали ошибки для отладки
            with st.expander("Детали ошибки"):
                st.code(str(e))


def perform_search(query, top_k, search_type):
    """Выполняет поиск и отображает результаты"""
    
    # Определяем тип чанков для поиска
    chunk_type = None
    if search_type == "Только текст":
        chunk_type = "text"
    elif search_type == "Только таблицы":
        chunk_type = "table"
    
    # Выполняем поиск
    with st.spinner('Поиск релевантной информации...'):
        try:
            results = st.session_state.indexer.search(
                query, 
                top_k=top_k, 
                chunk_type=chunk_type
            )
            
            if not results:
                st.warning("Релевантная информация для данного запроса не найдена")
                return
            
            # Отображаем результаты
            st.success(f"Найдено {len(results)} релевантных результатов:")
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                text = result['text']
                score = result['relevance_score']
                
                # Карточка результата
                with st.container():
                    st.markdown(f"### Результат {i}")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Документ:** {metadata.get('source_pdf', 'Неизвестен')}")
                    
                    with col2:
                        st.write(f"**Страница:** {metadata.get('page_number', 'Неизвестна')}")
                    
                    with col3:
                        # Определяем качество по релевантности
                        quality_info = get_quality_info(score)
                        st.write(f"**Релевантность:** {score*100:.1f}%")
                        st.write(f"*{quality_info['label']}*")
                    
                    # Дополнительная информация для таблиц
                    if metadata.get('chunk_type') == 'table':
                        st.write(f"**Таблица:** {metadata.get('original_table_title', 'Без названия')}")
                        if metadata.get('table_description'):
                            st.write(f"**Описание:** {metadata['table_description']}")
                    
                    # Содержимое
                    st.write("**Содержание:**")
                    
                    # Для таблиц показываем в expandable секции
                    if metadata.get('chunk_type') == 'table':
                        with st.expander("Показать содержимое таблицы", expanded=False):
                            st.text(text)
                    else:
                        # Для текста показываем превью и полную версию в expander
                        preview = text[:300] + "..." if len(text) > 300 else text
                        st.write(preview)
                        
                        if len(text) > 300:
                            with st.expander("Показать полный текст"):
                                st.text(text)
                    
                    st.markdown("---")
                    
        except Exception as e:
            st.error(f"Ошибка при поиске: {e}")


def main():
    """Главная функция приложения"""
    st.set_page_config(
        page_title="Lysobacter RAG System",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Инициализация
    init_indexer()
    
    # Основной интерфейс
    search_interface()
    
    # Информация в футере
    st.markdown("---")
    st.markdown(
        "**Lysobacter RAG System** | "
        "Система анализа научной литературы с поддержкой различных языковых моделей"
    )


if __name__ == "__main__":
    main() 