"""
Улучшенная RAG система для лизобактерий с поддержкой структурированного вывода
"""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
import openai
from openai import OpenAI

from config import config
from ..indexer import Indexer
from .enhanced_prompts import EnhancedPromptSystem, QueryType
from .context_synthesizer import ContextSynthesizer
from .notebooklm_prompts import NotebookLMPrompts
from .fact_checker import FactChecker

logger = logging.getLogger(__name__)

@dataclass
class EnhancedRAGResult:
    """Результат улучшенной RAG системы"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    query: str
    query_type: str
    num_sources_used: int
    metadata: Dict[str, Any]

class EnhancedRAGPipeline:
    """Улучшенная RAG система с специализированными промптами"""
    
    def __init__(self, use_notebooklm_style: bool = True):
        """Инициализация улучшенной RAG системы"""
        # Проверяем наличие API ключа
        if not config.OPENAI_API_KEY:
            raise ValueError("API ключ не установлен. Установите переменную OPENROUTER_API_KEY или OPENAI_API_KEY")
        
        # Инициализируем OpenAI клиент
        if hasattr(config, 'OPENROUTER_API_KEY') and config.OPENROUTER_API_KEY:
            self.openai_client = OpenAI(
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.OPENROUTER_BASE_URL
            )
            logger.info("Инициализирован клиент OpenRouter для улучшенной RAG")
        else:
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("Инициализирован клиент OpenAI для улучшенной RAG")
        
        # Инициализируем компоненты
        self.indexer = Indexer()
        self.prompt_system = EnhancedPromptSystem()
        self.fact_checker = FactChecker()
        self.use_notebooklm_style = use_notebooklm_style
        
        # Инициализируем NotebookLM компоненты если включены
        if self.use_notebooklm_style:
            self.context_synthesizer = ContextSynthesizer()
            logger.info("Включен режим NotebookLM для синтеза контекста")
        
        logger.info("Улучшенная RAG система инициализирована успешно")
    
    def ask_question(
        self, 
        query: str, 
        top_k: int = None, 
        query_type: Optional[QueryType] = None,
        prioritize_tables: bool = True,
        use_notebooklm_style: Optional[bool] = None
    ) -> EnhancedRAGResult:
        """
        Отвечает на вопрос с использованием улучшенной RAG системы
        
        Args:
            query (str): Вопрос пользователя
            top_k (int, optional): Количество релевантных чанков
            query_type (Optional[QueryType]): Тип запроса (определяется автоматически)
            prioritize_tables (bool): Приоритизировать табличные данные
            use_notebooklm_style (Optional[bool]): Использовать стиль NotebookLM
            
        Returns:
            EnhancedRAGResult: Результат обработки
        """
        if top_k is None:
            top_k = config.RAG_TOP_K
        
        # Определяем стиль ответа
        notebooklm_mode = use_notebooklm_style if use_notebooklm_style is not None else self.use_notebooklm_style
        
        logger.info(f"Обрабатываю улучшенный запрос: '{query[:100]}...' (NotebookLM: {notebooklm_mode})")
        
        try:
            # Шаг 1: Определение типа запроса
            if query_type is None:
                query_type = self.prompt_system.detect_query_type(query)
            
            logger.info(f"Определен тип запроса: {query_type.value}")
            
            # Шаг 2: Поиск релевантных документов
            if query_type == QueryType.STRAIN_ANALYSIS:
                # Для анализа штаммов используем расширенный поиск
                strain_name = self._extract_strain_name(query)
                if strain_name:
                    logger.info(f"Обнаружен анализ штамма: {strain_name}")
                    relevant_chunks = self._enhanced_strain_search(query, strain_name)
                else:
                    relevant_chunks = self.indexer.search(query, top_k=top_k * 2)
            else:
                relevant_chunks = self.indexer.search(query, top_k=top_k)
            
            if not relevant_chunks:
                return EnhancedRAGResult(
                    answer="Извините, я не смог найти релевантную информацию для ответа на ваш вопрос.",
                    sources=[],
                    confidence=0.0,
                    query=query,
                    query_type=query_type.value,
                    num_sources_used=0,
                    metadata={}
                )
            
            # Шаг 3: Приоритизация структурированных данных
            if prioritize_tables:
                relevant_chunks = self._prioritize_structured_data(relevant_chunks)
            
            # Шаг 4: Построение контекста
            if notebooklm_mode and hasattr(self, 'context_synthesizer'):
                # NotebookLM стиль - синтез контекста
                context = self._build_notebooklm_context(relevant_chunks, query)
                formatted_prompt = NotebookLMPrompts.format_enhanced_prompt(
                    query=query, 
                    raw_context=context, 
                    strain_name=self._extract_strain_name(query)
                )
            else:
                # Стандартный стиль
                context, table_metadata = self._build_enhanced_context(relevant_chunks)
                
                # Улучшение контекста для таблиц
                if table_metadata:
                    context = self.prompt_system.enhance_context_for_tables(context, table_metadata)
                
                formatted_prompt = self.prompt_system.format_prompt(query, context, query_type)
            
            # Шаг 5: Генерация ответа
            answer = self._generate_enhanced_answer(formatted_prompt)
            
            # Шаг 5.5: Проверка фактов (только для анализа штаммов)
            if query_type == QueryType.STRAIN_ANALYSIS:
                answer = self._validate_facts_in_answer(answer, relevant_chunks, query)
            
            # Шаг 6: Извлечение источников и метаданных
            sources = self._extract_enhanced_sources(relevant_chunks)
            confidence = self._calculate_enhanced_confidence(relevant_chunks, query_type)
            
            # Шаг 7: Создание метаданных результата
            metadata = {
                'prompt_type': query_type.value,
                'notebooklm_mode': notebooklm_mode,
                'context_length': len(context) if isinstance(context, str) else len(str(context)),
                'num_sources': len(relevant_chunks)
            }
            
            result = EnhancedRAGResult(
                answer=answer,
                sources=sources,
                confidence=confidence,
                query=query,
                query_type=query_type.value,
                num_sources_used=len(relevant_chunks),
                metadata=metadata
            )
            
            logger.info(f"Улучшенный ответ сгенерирован (тип: {query_type.value}, уверенность: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка в улучшенной RAG системе: {str(e)}")
            return EnhancedRAGResult(
                answer=f"Произошла ошибка при обработке вашего вопроса: {str(e)}",
                sources=[],
                confidence=0.0,
                query=query,
                query_type=query_type.value if query_type else "unknown",
                num_sources_used=0,
                metadata={}
            )
    
    def _build_notebooklm_context(self, relevant_chunks: List[Dict[str, Any]], query: str) -> str:
        """
        Строит контекст в стиле NotebookLM
        
        Args:
            relevant_chunks (List[Dict[str, Any]]): Релевантные чанки
            query (str): Исходный запрос
            
        Returns:
            str: Синтезированный контекст
        """
        # Извлекаем текстовое содержание чанков
        text_chunks = []
        for chunk in relevant_chunks:
            content = chunk.get('text', '')
            source_info = f"[Источник {chunk.get('id', 'неизвестен')}]"
            text_chunks.append(f"{content}\n{source_info}")
        
        # Используем синтезатор контекста
        synthesized_context = self.context_synthesizer.synthesize_for_notebooklm_style(
            text_chunks=text_chunks,
            query=query
        )
        
        # Добавляем исходные чанки для полноты
        full_context = synthesized_context + "\n\n" + "ИСХОДНЫЕ ДАННЫЕ:\n" + "\n\n".join(text_chunks[:5])
        
        return full_context
    
    def _prioritize_structured_data(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Приоритизирует структурированные данные (таблицы)
        
        Args:
            chunks (List[Dict[str, Any]]): Исходные чанки
            
        Returns:
            List[Dict[str, Any]]: Переупорядоченные чанки
        """
        # Разделяем на таблицы и текст
        tables = [c for c in chunks if c['metadata'].get('chunk_type') == 'table']
        texts = [c for c in chunks if c['metadata'].get('chunk_type') != 'table']
        
        # Сортируем таблицы по релевантности и специальным признакам
        tables.sort(key=lambda x: (
            x.get('relevance_score', 0),
            x['metadata'].get('likely_differential_table', False),
            x['metadata'].get('differential_score', 0)
        ), reverse=True)
        
        # Возвращаем таблицы первыми, затем текст
        return tables + texts
    
    def _build_enhanced_context(self, relevant_chunks: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """
        Создает улучшенный контекст с метаданными
        
        Args:
            relevant_chunks (List[Dict[str, Any]]): Релевантные чанки
            
        Returns:
            tuple[str, List[Dict[str, Any]]]: Контекст и метаданные таблиц
        """
        context_parts = []
        table_metadata = []
        
        for i, chunk in enumerate(relevant_chunks, 1):
            metadata = chunk['metadata']
            text = chunk['text']
            relevance = chunk.get('relevance_score', 0)
            
            # Формируем заголовок источника
            source_header = f"[ИСТОЧНИК {i}]"
            source_info = f"Документ: {metadata.get('source_pdf', 'Неизвестен')}"
            
            if metadata.get('page_number'):
                source_info += f", Страница: {metadata['page_number']}"
            
            # Специальная обработка для таблиц
            if metadata.get('chunk_type') == 'table':
                source_info += " [ТАБЛИЦА]"
                if metadata.get('original_table_title'):
                    source_info += f", Заголовок: {metadata['original_table_title']}"
                
                # Добавляем в метаданные таблиц
                table_metadata.append(metadata)
            
            source_info += f", Релевантность: {relevance:.2f}"
            
            # Специальное форматирование для разных типов элементов
            if metadata.get('element_type') == 'table':
                content_header = "ТАБЛИЧНЫЕ ДАННЫЕ:"
            elif metadata.get('element_type') == 'title':
                content_header = "ЗАГОЛОВОК:"
            else:
                content_header = "СОДЕРЖАНИЕ:"
            
            context_part = f"{source_header}\n{source_info}\n\n{content_header}\n{text}\n"
            context_parts.append(context_part)
        
        context = "\n" + "="*80 + "\n".join(context_parts) + "="*80 + "\n"
        return context, table_metadata
    
    def _generate_enhanced_answer(self, formatted_prompt: Dict[str, str]) -> str:
        """
        Генерирует улучшенный ответ с использованием специализированного промпта
        
        Args:
            formatted_prompt (Dict[str, str]): Отформатированный промпт
            
        Returns:
            str: Сгенерированный ответ
        """
        try:
            messages = [
                {"role": "system", "content": formatted_prompt['system']},
                {"role": "user", "content": formatted_prompt['user']}
            ]
            
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=config.RAG_TEMPERATURE,
                max_tokens=8000  # Существенно увеличиваем лимит для полных ответов в стиле NotebookLM
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при генерации улучшенного ответа: {str(e)}")
            return f"Извините, произошла ошибка при генерации ответа: {str(e)}"
    
    def _extract_enhanced_sources(self, relevant_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Извлекает улучшенную информацию об источниках
        
        Args:
            relevant_chunks (List[Dict[str, Any]]): Релевантные чанки
            
        Returns:
            List[Dict[str, Any]]: Список источников с метаданными
        """
        sources = []
        
        for i, chunk in enumerate(relevant_chunks, 1):
            metadata = chunk['metadata']
            
            source = {
                'id': i,
                'document': metadata.get('source_pdf', 'Неизвестен'),
                'page': metadata.get('page_number'),
                'type': metadata.get('element_type', 'text'),
                'relevance_score': chunk.get('relevance_score', 0),
                'text_preview': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            }
            
            # Дополнительные метаданные для таблиц
            if metadata.get('chunk_type') == 'table':
                source.update({
                    'table_title': metadata.get('original_table_title'),
                    'is_differential_table': metadata.get('likely_differential_table', False),
                    'differential_score': metadata.get('differential_score', 0)
                })
            
            sources.append(source)
        
        return sources
    
    def _calculate_enhanced_confidence(self, relevant_chunks: List[Dict[str, Any]], query_type: QueryType) -> float:
        """
        Рассчитывает улучшенную оценку уверенности
        
        Args:
            relevant_chunks (List[Dict[str, Any]]): Релевантные чанки
            query_type (QueryType): Тип запроса
            
        Returns:
            float: Оценка уверенности
        """
        if not relevant_chunks:
            return 0.0
        
        # Базовая уверенность на основе релевантности
        avg_relevance = sum(chunk.get('relevance_score', 0) for chunk in relevant_chunks) / len(relevant_chunks)
        confidence = avg_relevance
        
        # Бонус за наличие таблиц для соответствующих типов запросов
        table_chunks = [c for c in relevant_chunks if c['metadata'].get('chunk_type') == 'table']
        if table_chunks and query_type in [QueryType.STRAIN_ANALYSIS, QueryType.COMPARATIVE_ANALYSIS, QueryType.TABLE_INTERPRETATION]:
            confidence += 0.1
        
        # Бонус за дифференциальные таблицы
        differential_tables = [c for c in table_chunks if c['metadata'].get('likely_differential_table')]
        if differential_tables:
            confidence += 0.1
        
        # Штраф за слишком мало источников
        if len(relevant_chunks) < 3:
            confidence *= 0.8
        
        return min(confidence, 1.0)
    
    def get_query_types(self) -> List[Dict[str, str]]:
        """
        Возвращает доступные типы запросов
        
        Returns:
            List[Dict[str, str]]: Список типов запросов
        """
        return self.prompt_system.get_available_query_types()
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику улучшенной RAG системы
        
        Returns:
            Dict[str, Any]: Статистика системы
        """
        base_stats = self.indexer.get_collection_stats()
        
        enhanced_stats = {
            'enhanced_features': {
                'specialized_prompts': len(self.prompt_system.prompts),
                'query_types': [qt.value for qt in QueryType],
                'table_prioritization': True,
                'structured_output': True
            },
            'prompt_system': {
                'available_types': self.get_query_types()
            }
        }
        
        return {**base_stats, **enhanced_stats}

    def _enhanced_strain_search(self, query: str, strain_name: str) -> List[Dict[str, Any]]:
        """
        Расширенный поиск информации о конкретном штамме
        """
        search_queries = [
            f"{strain_name}",  # Основной поиск по названию штамма
            f"{strain_name} morphology characteristics",  # Морфология
            f"{strain_name} growth conditions temperature pH",  # Условия роста
            f"{strain_name} biochemical tests enzymes",  # Биохимия
            f"{strain_name} fatty acids lipids",  # Жирные кислоты
            f"{strain_name} genome size genes",  # Геном
            f"{strain_name} isolation source origin",  # Происхождение
        ]
        
        all_results = []
        seen_ids = set()
        
        for search_query in search_queries:
            logger.info(f"Поиск по запросу: {search_query}")
            results = self.indexer.search(search_query, top_k=8)
            
            # Добавляем уникальные результаты
            for result in results:
                chunk_id = result.get('metadata', {}).get('chunk_id', '')
                if chunk_id and chunk_id not in seen_ids:
                    seen_ids.add(chunk_id)
                    all_results.append(result)
        
        # Сортируем по релевантности и берем топ-15
        all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return all_results[:15]

    def _extract_strain_name(self, query: str) -> str:
        """
        Извлекает название штамма из запроса
        """
        import re
        
        # Паттерны для названий штаммов
        patterns = [
            r'штамм[е]?\s+([A-Za-z0-9\-]+[T]?)',  # штамм GW1-59T
            r'([A-Za-z0-9\-]+[T])\s*[\.,]?',      # GW1-59T
            r'([A-Z]{1,3}[0-9]+\-[0-9]+[T]?)',    # GW1-59T
            r'([A-Z]+\-[0-9]+[T]?)',              # GW1-59T
        ]
        
        query_lower = query.lower()
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                strain = match.group(1)
                logger.info(f"Извлечено название штамма: {strain}")
                return strain
        
        return ""
    
    def _validate_facts_in_answer(self, answer: str, relevant_chunks: List[Dict[str, Any]], query: str) -> str:
        """
        Проверяет факты в ответе и добавляет предупреждения о неточностях
        
        Args:
            answer (str): Сгенерированный ответ
            relevant_chunks (List[Dict[str, Any]]): Источники данных
            query (str): Исходный запрос
            
        Returns:
            str: Ответ с предупреждениями о неточностях
        """
        import re
        
        # Извлекаем название штамма
        strain_name = self._extract_strain_name(query)
        if not strain_name:
            return answer
        
        # Преобразуем источники для fact_checker
        evidence_chunks = []
        for chunk in relevant_chunks:
            chunk_data = {
                'text': chunk.get('text', ''),
                'metadata': chunk.get('metadata', {})
            }
            evidence_chunks.append(chunk_data)
        
        warnings = []
        validated_answer = answer
        
        # Проверка температурных данных
        temp_patterns = [
            r'(\d+)\s*[–-]\s*(\d+)\s*°C',
            r'от\s+(\d+)\s*°C\s+до\s+(\d+)\s*°C',
            r'от\s+(\d+)\s+до\s+(\d+)\s*°C',
            r'диапазоне\s+от\s+(\d+)\s+до\s+(\d+)\s*°C',
            r'диапазон.*?от\s+(\d+).*?до\s+(\d+)\s*°C',
        ]
        
        for pattern in temp_patterns:
            matches = re.findall(pattern, answer)
            for match in matches:
                temp_claim = f"{match[0]}-{match[1]}°C"
                fact_check = self.fact_checker.check_temperature_claim(
                    temp_claim, evidence_chunks, strain_name
                )
                
                if not fact_check.is_accurate and fact_check.confidence > 0.3:
                    warning = f"⚠️ **Предупреждение**: Температурный диапазон {temp_claim} может быть неточным. Рекомендуется проверить первоисточники."
                    warnings.append(warning)
        
        # Проверка pH данных
        ph_patterns = [
            r'pH\s+(\d+[.,]\d+)\s*[–-]\s*(\d+[.,]\d+)',
            r'от\s+pH\s+(\d+[.,]\d+)\s+до\s+(\d+[.,]\d+)',
        ]
        
        for pattern in ph_patterns:
            matches = re.findall(pattern, answer)
            for match in matches:
                ph_claim = f"pH {match[0]}-{match[1]}"
                fact_check = self.fact_checker.check_ph_claim(
                    ph_claim, evidence_chunks, strain_name
                )
                
                if not fact_check.is_accurate and fact_check.confidence > 0.3:
                    warning = f"⚠️ **Предупреждение**: pH диапазон {ph_claim} может быть неточным. Рекомендуется проверить первоисточники."
                    warnings.append(warning)
        
        # Добавляем предупреждения в конец ответа
        if warnings:
            validated_answer += "\n\n---\n**🔍 Проверка фактов:**\n\n" + "\n\n".join(warnings)
            validated_answer += "\n\n*Система автоматической проверки фактов обнаружила возможные неточности. Для критически важных данных рекомендуется обращение к первоисточникам.*"
        
        return validated_answer 