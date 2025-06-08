"""
Модуль RAG-пайплайна для ответов на вопросы
Интегрирует поиск релевантных документов с генерацией ответов через LLM
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import openai
from openai import OpenAI

from config import config
from ..indexer import Indexer
from .comparative_analyzer import ComparativeAnalyzer


class RAGPipeline:
    """Класс для выполнения RAG-процесса: поиск + генерация ответов"""
    
    def __init__(self):
        """Инициализация RAG-пайплайна"""
        # Проверяем наличие API ключа
        if not config.OPENAI_API_KEY:
            raise ValueError("API ключ не установлен. Установите переменную OPENROUTER_API_KEY или OPENAI_API_KEY")
        
        # Инициализируем OpenAI клиент (совместимый с OpenRouter)
        if hasattr(config, 'OPENROUTER_API_KEY') and config.OPENROUTER_API_KEY:
            # Используем OpenRouter
            self.openai_client = OpenAI(
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.OPENROUTER_BASE_URL
            )
            logger.info("Инициализирован клиент OpenRouter")
        else:
            # Используем стандартный OpenAI
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("Инициализирован клиент OpenAI")
        
        # Инициализируем индексатор для поиска
        self.indexer = Indexer()
        
        # Инициализируем сравнительный анализатор
        self.comparative_analyzer = ComparativeAnalyzer()
        
        logger.info("RAG-пайплайн инициализирован успешно")
    
    def ask_question(self, query: str, top_k: int = None, include_sources: bool = True) -> Dict[str, Any]:
        """
        Отвечает на вопрос пользователя используя RAG-подход
        
        Args:
            query (str): Вопрос пользователя
            top_k (int, optional): Количество релевантных чанков для поиска
            include_sources (bool): Включать ли источники в ответ
            
        Returns:
            Dict[str, Any]: Словарь с ответом и метаданными
        """
        if top_k is None:
            top_k = config.RAG_TOP_K
        
        logger.info(f"Обрабатываю вопрос: '{query[:100]}...'")
        
        try:
            # Проверяем, является ли запрос сравнительным
            if self._is_comparative_query(query):
                logger.info("Определен сравнительный запрос, используем специализированный анализ")
                return self._handle_comparative_query(query, top_k)
            
            # Шаг 1: Поиск релевантных документов с использованием гибридного поиска
            relevant_chunks = self.indexer.hybrid_search(query, top_k=top_k)
            
            if not relevant_chunks:
                return {
                    'answer': "Извините, я не смог найти релевантную информацию для ответа на ваш вопрос.",
                    'sources': [],
                    'confidence': 0.0,
                    'query': query
                }
            
            # Шаг 2: Формирование контекста для LLM
            context = self._build_context(relevant_chunks)
            
            # Шаг 3: Генерация ответа с помощью LLM
            answer = self._generate_answer(query, context)
            
            # Шаг 4: Извлечение источников
            sources = self._extract_sources(relevant_chunks) if include_sources else []
            
            # Шаг 5: Оценка уверенности в ответе
            confidence = self._calculate_confidence(relevant_chunks)
            
            result = {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'query': query,
                'num_sources_used': len(relevant_chunks)
            }
            
            logger.info(f"Ответ сгенерирован успешно (уверенность: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при обработке вопроса: {str(e)}")
            return {
                'answer': f"Произошла ошибка при обработке вашего вопроса: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'query': query
            }
    
    def _build_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Создает контекст для LLM из релевантных чанков
        
        Args:
            relevant_chunks (List[Dict[str, Any]]): Релевантные чанки
            
        Returns:
            str: Сформированный контекст
        """
        context_parts = []
        
        for i, chunk in enumerate(relevant_chunks, 1):
            metadata = chunk['metadata']
            text = chunk['text']
            relevance = chunk.get('relevance_score', 0)
            
            # Формируем заголовок для каждого источника
            source_header = f"[ИСТОЧНИК {i}]"
            source_info = f"Документ: {metadata.get('source_pdf', 'Неизвестен')}"
            
            if metadata.get('page_number'):
                source_info += f", Страница: {metadata['page_number']}"
            
            # Специальная обработка для табличных данных
            if metadata.get('chunk_type') == 'table':
                source_info += " [ТАБЛИЦА]"
                if metadata.get('table_shape'):
                    source_info += f", Размер: {metadata['table_shape']}"
                if metadata.get('extraction_method'):
                    source_info += f", Метод: {metadata['extraction_method']}"
                
                # Добавляем специальный маркер для таблиц
                text = f"📊 ТАБЛИЧНЫЕ ДАННЫЕ:\n{text}"
                
            elif metadata.get('original_table_title'):
                source_info += f", Таблица: {metadata['original_table_title']}"
            
            source_info += f", Релевантность: {relevance:.2f}"
            
            # Специальная обработка для продвинутого экстрактора
            if metadata.get('advanced_extractor'):
                source_info += " [УЛУЧШЕННОЕ ИЗВЛЕЧЕНИЕ]"
            
            context_part = f"{source_header}\n{source_info}\n\nСодержание:\n{text}\n"
            context_parts.append(context_part)
        
        return "\n" + "="*80 + "\n".join(context_parts) + "="*80 + "\n"
    
    def _generate_answer(self, query: str, context: str) -> str:
        """
        Генерирует ответ с помощью OpenAI API
        
        Args:
            query (str): Вопрос пользователя
            context (str): Контекст из релевантных документов
            
        Returns:
            str: Сгенерированный ответ
        """
        # Создаем промпт для LLM
        system_prompt = """Вы - специалист по микробиологии, эксперт по лизобактериям. 
        Ваша задача - отвечать на вопросы пользователей на основе предоставленного контекста из научных публикаций.

        ВАЖНЫЕ ПРАВИЛА:
        1. ОБЯЗАТЕЛЬНО отвечайте на РУССКОМ языке
        2. Отвечайте ТОЛЬКО на основе предоставленного контекста
        3. Если информации недостаточно для ответа, честно об этом скажите
        4. Всегда указывайте источники информации в формате [Источник X]
        5. Используйте научную терминологию, но объясняйте сложные понятия
        6. Если вопрос касается таблиц, детально разберите табличные данные
        7. Будьте точны и объективны в интерпретации данных
        8. Структурируйте ответ с заголовками и списками для лучшей читаемости

        ФОРМАТ ОТВЕТА:
        ## ОСНОВНАЯ ИНФОРМАЦИЯ
        [краткий ответ на вопрос]
        
        ## ДЕТАЛИ
        [подробная информация из источников]
        
        ## ИСТОЧНИКИ
        [указание конкретных источников]

        ВСЕГДА отвечайте на русском языке, используя структурированный формат."""
        
        user_prompt = f"""Контекст из научных публикаций о лизобактериях:
        {context}
        
        Вопрос пользователя: {query}
        
        Пожалуйста, дайте подробный и точный ответ на основе предоставленного контекста, обязательно указывая источники."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config.RAG_TEMPERATURE,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {str(e)}")
            return f"Извините, произошла ошибка при генерации ответа: {str(e)}"
    
    def _extract_sources(self, relevant_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Извлекает информацию об источниках
        
        Args:
            relevant_chunks (List[Dict[str, Any]]): Релевантные чанки
            
        Returns:
            List[Dict[str, Any]]: Список источников
        """
        sources = []
        
        for i, chunk in enumerate(relevant_chunks, 1):
            metadata = chunk['metadata']
            
            source = {
                'source_id': i,
                'document': metadata.get('source_pdf', 'Неизвестен'),
                'page_number': metadata.get('page_number', ''),
                'chunk_type': metadata.get('chunk_type', ''),
                'relevance_score': chunk.get('relevance_score', 0)
            }
            
            # Добавляем специфичную информацию для таблиц
            if metadata.get('chunk_type') == 'table':
                source.update({
                    'table_title': metadata.get('original_table_title', ''),
                    'table_description': metadata.get('table_description', ''),
                    'confidence_score': metadata.get('confidence_score', '')
                })
            
            sources.append(source)
        
        return sources
    
    def _calculate_confidence(self, relevant_chunks: List[Dict[str, Any]]) -> float:
        """
        Вычисляет уверенность в ответе на основе релевантности найденных чанков
        
        Args:
            relevant_chunks (List[Dict[str, Any]]): Релевантные чанки
            
        Returns:
            float: Оценка уверенности от 0 до 1
        """
        if not relevant_chunks:
            return 0.0
        
        # Берем среднюю релевантность чанков
        relevance_scores = [chunk.get('relevance_score', 0) for chunk in relevant_chunks]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Бонус за количество найденных релевантных источников
        quantity_bonus = min(len(relevant_chunks) / 5, 0.2)
        
        # Бонус за наличие табличных данных (они обычно более структурированы)
        table_bonus = 0.1 if any(c['metadata'].get('chunk_type') == 'table' for c in relevant_chunks) else 0
        
        confidence = min(avg_relevance + quantity_bonus + table_bonus, 1.0)
        return round(confidence, 3)
    
    def ask_multiple_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Отвечает на несколько вопросов подряд
        
        Args:
            questions (List[str]): Список вопросов
            
        Returns:
            List[Dict[str, Any]]: Список ответов
        """
        results = []
        
        for i, question in enumerate(questions, 1):
            logger.info(f"Обрабатываю вопрос {i}/{len(questions)}")
            result = self.ask_question(question)
            results.append(result)
        
        return results
    
    def search_tables_only(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Ищет информацию только в табличных данных
        
        Args:
            query (str): Поисковый запрос
            top_k (int): Количество таблиц для поиска
            
        Returns:
            Dict[str, Any]: Результат поиска в таблицах
        """
        # Ищем только в табличных чанках
        table_chunks = self.indexer.search(query, top_k=top_k, chunk_type="table")
        
        if not table_chunks:
            return {
                'answer': "В табличных данных не найдено релевантной информации для вашего запроса.",
                'tables': [],
                'query': query
            }
        
        # Генерируем ответ на основе только табличных данных
        context = self._build_context(table_chunks)
        answer = self._generate_answer(query, context)
        
        # Извлекаем информацию о таблицах
        tables_info = []
        for chunk in table_chunks:
            metadata = chunk['metadata']
            table_info = {
                'document': metadata.get('source_pdf', ''),
                'page_number': metadata.get('page_number', ''),
                'title': metadata.get('original_table_title', ''),
                'description': metadata.get('table_description', ''),
                'shape': metadata.get('table_shape', ''),
                'relevance_score': chunk.get('relevance_score', 0)
            }
            tables_info.append(table_info)
        
        return {
            'answer': answer,
            'tables': tables_info,
            'query': query,
            'num_tables_found': len(table_chunks)
        }
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику RAG-пайплайна
        
        Returns:
            Dict[str, Any]: Статистика пайплайна
        """
        indexer_stats = self.indexer.get_collection_stats()
        
        pipeline_stats = {
            'model_used': config.OPENAI_MODEL,
            'embedding_model': config.EMBEDDING_MODEL,
            'top_k_default': config.RAG_TOP_K,
            'temperature': config.RAG_TEMPERATURE,
            **indexer_stats
        }
        
        return pipeline_stats
    
    def _is_comparative_query(self, query: str) -> bool:
        """Определяет, является ли запрос сравнительным"""
        comparative_keywords = [
            'сравни', 'сравните', 'сравнение', 'различия', 'отличия', 'разности',
            'compare', 'comparison', 'differences', 'distinguish', 'contrast',
            'между', 'among', 'различных', 'different', 'multiple', 'множественн',
            'общие черты', 'common features', 'общность', 'similarity',
            'характеристик различных', 'characteristics of different'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in comparative_keywords)
    
    def _handle_comparative_query(self, query: str, top_k: int) -> Dict[str, Any]:
        """Обрабатывает сравнительный запрос"""
        # Расширяем поиск для получения информации о множественных видах
        extended_top_k = max(top_k * 3, 30)  # Увеличиваем количество для лучшего покрытия
        
        # Модифицируем запрос для лучшего поиска множественных видов
        expanded_query = self._expand_comparative_query(query)
        
        # Поиск с расширенными параметрами
        relevant_chunks = self.indexer.hybrid_search(expanded_query, top_k=extended_top_k)
        
        if not relevant_chunks:
            return {
                'answer': "Извините, я не смог найти достаточно информации для сравнительного анализа.",
                'sources': [],
                'confidence': 0.0,
                'query': query,
                'analysis_type': 'comparative'
            }
        
        # Формируем расширенный контекст
        context = self._build_context(relevant_chunks)
        
        # Используем специализированный сравнительный анализ
        comparative_report = self.comparative_analyzer.analyze_comparative_query(context, query)
        
        # Если сравнительный анализатор нашел данные, используем его результат
        if comparative_report.species_count > 0:
            answer = comparative_report.formatted_response
            confidence = min(0.8, 0.3 + (comparative_report.species_count * 0.1))
        else:
            # Fallback: генерируем ответ через LLM с улучшенным промптом для сравнения
            answer = self._generate_comparative_answer(query, context)
            confidence = self._calculate_confidence(relevant_chunks)
        
        # Извлекаем источники
        sources = self._extract_sources(relevant_chunks)
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence,
            'query': query,
            'analysis_type': 'comparative',
            'species_analyzed': comparative_report.species_count,
            'comparative_features': comparative_report.compared_characteristics,
            'num_sources_used': len(relevant_chunks)
        }
    
    def _expand_comparative_query(self, query: str) -> str:
        """Расширяет сравнительный запрос для лучшего поиска"""
        base_terms = ['Lysobacter', 'лизобактер', 'штамм', 'strain', 'вид', 'species']
        
        # Добавляем термины в зависимости от типа сравнения
        if 'морфолог' in query.lower() or 'morpholog' in query.lower():
            base_terms.extend(['морфология', 'форма', 'размер', 'клетка', 'колони'])
        elif 'физиолог' in query.lower() or 'physiol' in query.lower():
            base_terms.extend(['температура', 'pH', 'рост', 'условия'])
        elif 'биохим' in query.lower() or 'biochem' in query.lower():
            base_terms.extend(['фермент', 'каталаза', 'оксидаза', 'метаболизм'])
        
        # Добавляем общие термины
        base_terms.extend(['характеристики', 'свойства', 'особенности'])
        
        expanded_query = f"{query} {' '.join(base_terms[:10])}"  # Ограничиваем длину
        return expanded_query
    
    def _generate_comparative_answer(self, query: str, context: str) -> str:
        """Генерирует ответ для сравнительного запроса с специальным промптом"""
        system_prompt = """Вы - специалист по микробиологии, эксперт по сравнительному анализу лизобактерий.
        Ваша задача - проводить СРАВНИТЕЛЬНЫЙ АНАЛИЗ различных видов Lysobacter на основе предоставленного контекста.

        ВАЖНЫЕ ПРАВИЛА ДЛЯ СРАВНИТЕЛЬНОГО АНАЛИЗА:
        1. ОБЯЗАТЕЛЬНО отвечайте на РУССКОМ языке
        2. ИЩИТЕ и ИЗВЛЕКАЙТЕ данные о ВСЕХ упомянутых видах Lysobacter
        3. СРАВНИВАЙТЕ характеристики между видами, не ограничивайтесь одним видом
        4. Создавайте ТАБЛИЦЫ сравнения когда это возможно
        5. Выделяйте ОБЩИЕ ЧЕРТЫ и РАЗЛИЧИЯ между видами
        6. Указывайте конкретные ЧИСЛЕННЫЕ ДАННЫЕ (размеры, температуры, pH)
        7. Всегда указывайте источники [Источник X]

        СТРУКТУРА СРАВНИТЕЛЬНОГО ОТВЕТА:
        ## СРАВНИТЕЛЬНЫЙ АНАЛИЗ [название характеристик]
        
        ### 🔄 ОБЩИЕ ЧЕРТЫ РОДА LYSOBACTER:
        [характеристики, общие для всех/большинства видов]
        
        ### 🔍 ВИДОВЫЕ РАЗЛИЧИЯ:
        [конкретные различия между видами с данными]
        
        ### 📊 СВОДНАЯ ТАБЛИЦА:
        [таблица сравнения в markdown формате]
        
        ### 💡 ВЫВОДЫ:
        [обобщение различий и их таксономическое значение]

        НЕ ГОВОРИТЕ что "данных недостаточно" - ИЗВЛЕКАЙТЕ ВСЕ доступные данные о разных видах!"""
        
        user_prompt = f"""Контекст из научных публикаций о различных видах лизобактерий:
        {context}
        
        Сравнительный вопрос: {query}
        
        Проведите детальный СРАВНИТЕЛЬНЫЙ АНАЛИЗ всех видов Lysobacter, упомянутых в контексте. 
        Создайте структурированный ответ с таблицами сравнения."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Более строгий для фактических данных
                max_tokens=4000   # Больше токенов для подробного сравнения
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при генерации сравнительного ответа: {str(e)}")
            return f"Извините, произошла ошибка при генерации сравнительного анализа: {str(e)}"


if __name__ == "__main__":
    # Пример использования
    try:
        rag = RAGPipeline()
        
        # Тестовые вопросы
        test_questions = [
            "Какие фенотипические характеристики отличают разные штаммы лизобактера?",
            "Какие методы используются для идентификации лизобактерий?",
            "В каких условиях растут лизобактерии?"
        ]
        
        for question in test_questions:
            print(f"\n🤔 Вопрос: {question}")
            print("="*80)
            
            result = rag.ask_question(question)
            
            print(f"💬 Ответ: {result['answer']}")
            print(f"🎯 Уверенность: {result['confidence']:.2f}")
            print(f"📚 Использовано источников: {result['num_sources_used']}")
            
            if result['sources']:
                print("\n📖 Источники:")
                for source in result['sources']:
                    print(f"  - {source['document']} (стр. {source['page_number']}, релевантность: {source['relevance_score']:.2f})")
            
            print("\n" + "="*80)
        
        # Показываем статистику
        stats = rag.get_pipeline_stats()
        print("\n📊 Статистика RAG-пайплайна:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Ошибка при запуске RAG-пайплайна: {e}")
        print("Убедитесь, что установлен OpenAI API ключ и данные проиндексированы.") 