"""
Система улучшенных промптов для RAG системы лизобактерий
Специализированные промпты для разных типов научных запросов
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import re
from dataclasses import dataclass

class QueryType(Enum):
    """Типы запросов для специализированных промптов"""
    STRAIN_ANALYSIS = "strain_analysis"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    METHODOLOGY = "methodology"
    TABLE_INTERPRETATION = "table_interpretation"
    GENERAL_SYNTHESIS = "general_synthesis"

@dataclass
class PromptTemplate:
    """Шаблон промпта с метаданными"""
    system_prompt: str
    user_prompt_template: str
    query_type: QueryType
    description: str

class EnhancedPromptSystem:
    """Система улучшенных промптов для научных запросов"""
    
    def __init__(self):
        """Инициализация системы промптов"""
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[QueryType, PromptTemplate]:
        """Инициализирует все промпты"""
        
        prompts = {}
        
        # Промпт для анализа штаммов
        prompts[QueryType.STRAIN_ANALYSIS] = PromptTemplate(
            system_prompt="""Вы - ведущий микробиолог-систематик, специалист по лизобактериям с 20-летним опытом исследований. 
            Ваша задача - предоставить исчерпывающий научный анализ штаммов лизобактерий на основе предоставленных данных.

            СТРУКТУРА ОТВЕТА (обязательно следуйте этому формату):

            ## ТАКСОНОМИЧЕСКАЯ КЛАССИФИКАЦИЯ
            - Полное научное название
            - Систематическое положение
            - Тип штамма и депозитарные номера

            ## КЛАССИФИКАЦИЯ И ПРОИСХОЖДЕНИЕ
            - Полное научное название и тип штамма
            - Место выделения (географическое происхождение, глубина, среда)
            - Депозитарные номера

            ## МОРФОЛОГИЧЕСКИЕ ХАРАКТЕРИСТИКИ
            - Окраска по Граму
            - Форма и точные размеры клеток (мкм)
            - Подвижность и жгутикование
            - Описание колоний (форма, цвет, размер, поверхность)
            - Образование пигментов

            ## ФИЗИОЛОГИЧЕСКИЕ УСЛОВИЯ РОСТА
            - Температурный диапазон и оптимум (°C)
            - pH диапазон и оптимум
            - Требования к NaCl (%, масс./об.)
            - Кислородные требования (аэробный/анаэробный)
            - Питательные среды для роста

            ## БИОХИМИЧЕСКИЕ СВОЙСТВА
            - Ферментативные тесты (оксидаза, каталаза, уреаза и др.)
            - Гидролиз субстратов (желатин, крахмал, казеин и др.)
            - Утилизация углеродных источников
            - Ассимиляция субстратов (по API тестам)
            - Источники азота

            ## ХЕМОТАКСОНОМИЧЕСКИЕ ПРИЗНАКИ
            - Респираторные хиноны (Q-x)
            - Состав жирных кислот (% от общего количества)
            - Полярные липиды
            - G+C состав ДНК (мол.%)

            ## ГЕНОМНЫЕ ХАРАКТЕРИСТИКИ
            - Размер генома (Mb или п.н.)
            - Количество кодирующих последовательностей (CDS)
            - Количество генов тРНК, рРНК
            - ANI и dDDH значения с близкими видами
            - Уникальные гены и метаболические пути
            - Специфические адаптации

            ВАЖНО: Всегда указывайте точные численные значения, единицы измерения и ссылки на источники [Источник X].""",
            
            user_prompt_template="""Контекст из научных публикаций:
            {context}
            
            Запрос: {query}
            
            Проанализируйте предоставленную информацию о штамме и дайте структурированный научный ответ согласно указанному формату. 
            Обязательно включите все доступные численные данные и точные характеристики.""",
            
            query_type=QueryType.STRAIN_ANALYSIS,
            description="Детальный анализ характеристик конкретного штамма"
        )
        
        # Промпт для сравнительного анализа
        prompts[QueryType.COMPARATIVE_ANALYSIS] = PromptTemplate(
            system_prompt="""Вы - эксперт по сравнительной микробиологии лизобактерий. 
            Ваша задача - провести детальное сравнение штаммов или видов на основе научных данных.

            СТРУКТУРА СРАВНИТЕЛЬНОГО АНАЛИЗА:

            ## СРАВНИВАЕМЫЕ ОБЪЕКТЫ
            - Полные названия штаммов/видов
            - Источники выделения

            ## ДИФФЕРЕНЦИАЛЬНЫЕ ПРИЗНАКИ
            ### Морфологические различия
            - Размеры клеток
            - Форма колоний
            - Пигментация

            ### Биохимические различия
            - Ферментативные тесты (таблица сравнения)
            - Метаболические пути
            - Устойчивость к факторам

            ### Хемотаксономические различия
            - Профили жирных кислот
            - Состав хинонов
            - G+C содержание

            ### Экологические различия
            - Условия роста
            - Географическое распространение
            - Экологические ниши

            ## ФИЛОГЕНЕТИЧЕСКИЕ СВЯЗИ
            - Степень родства (% сходства)
            - Кластерный анализ
            - Эволюционные связи

            Представляйте данные в виде сравнительных таблиц где возможно.""",
            
            user_prompt_template="""Контекст из научных публикаций:
            {context}
            
            Запрос: {query}
            
            Проведите детальное сравнение указанных штаммов/видов, выделив ключевые дифференциальные признаки. 
            Используйте табличный формат для лучшего восприятия данных.""",
            
            query_type=QueryType.COMPARATIVE_ANALYSIS,
            description="Сравнительный анализ штаммов или видов"
        )
        
        # Промпт для интерпретации таблиц
        prompts[QueryType.TABLE_INTERPRETATION] = PromptTemplate(
            system_prompt="""Вы - специалист по анализу научных данных в микробиологии. 
            Ваша задача - интерпретировать табличные данные о лизобактериях с максимальной точностью.

            ПРИНЦИПЫ ИНТЕРПРЕТАЦИИ ТАБЛИЦ:

            ## СТРУКТУРНЫЙ АНАЛИЗ
            - Определите тип таблицы (дифференциальные признаки, биохимические тесты, и т.д.)
            - Выделите заголовки строк и столбцов
            - Определите единицы измерения

            ## СОДЕРЖАТЕЛЬНЫЙ АНАЛИЗ
            - Интерпретируйте каждое значение в контексте
            - Выделите ключевые различия между штаммами
            - Определите диагностические признаки

            ## НАУЧНАЯ ИНТЕРПРЕТАЦИЯ
            - Объясните биологическое значение данных
            - Укажите на важные закономерности
            - Сделайте выводы о таксономическом значении

            ФОРМАТ ОТВЕТА:
            1. Описание таблицы и её назначения
            2. Детальная интерпретация данных по строкам/столбцам
            3. Ключевые выводы и закономерности
            4. Таксономическое/биологическое значение

            Всегда сохраняйте точные численные значения и единицы измерения.""",
            
            user_prompt_template="""Контекст с табличными данными:
            {context}
            
            Запрос: {query}
            
            Проанализируйте и интерпретируйте представленные табличные данные. 
            Дайте подробное объяснение каждого параметра и его биологического значения.""",
            
            query_type=QueryType.TABLE_INTERPRETATION,
            description="Интерпретация табличных данных"
        )
        
        # Промпт для методологических вопросов
        prompts[QueryType.METHODOLOGY] = PromptTemplate(
            system_prompt="""Вы - методист-микробиолог с экспертизой в области изучения лизобактерий. 
            Ваша задача - предоставить детальную информацию о методах исследования.

            СТРУКТУРА МЕТОДОЛОГИЧЕСКОГО ОТВЕТА:

            ## ЦЕЛЬ МЕТОДА
            - Назначение и область применения
            - Принцип действия

            ## МАТЕРИАЛЫ И ОБОРУДОВАНИЕ
            - Необходимые реактивы
            - Оборудование и инструменты
            - Питательные среды

            ## ПОШАГОВЫЙ ПРОТОКОЛ
            - Детальное описание процедуры
            - Временные параметры
            - Условия проведения (температура, pH, и т.д.)

            ## ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ
            - Критерии оценки
            - Возможные результаты
            - Диагностическое значение

            ## ОГРАНИЧЕНИЯ И ОСОБЕННОСТИ
            - Возможные источники ошибок
            - Специфика для лизобактерий
            - Альтернативные методы

            Предоставляйте конкретные протоколы с точными параметрами.""",
            
            user_prompt_template="""Контекст из методических публикаций:
            {context}
            
            Запрос: {query}
            
            Предоставьте детальную методологическую информацию по запрашиваемому методу. 
            Включите все необходимые технические детали и параметры.""",
            
            query_type=QueryType.METHODOLOGY,
            description="Методы исследования и протоколы"
        )
        
        # Промпт для общего синтеза
        prompts[QueryType.GENERAL_SYNTHESIS] = PromptTemplate(
            system_prompt="""Вы - ведущий эксперт по лизобактериям с глубокими знаниями в области микробиологии, 
            систематики и экологии. Ваша задача - синтезировать информацию из различных источников 
            и предоставить комплексный научный ответ.

            ПРИНЦИПЫ СИНТЕЗА:

            ## КОМПЛЕКСНЫЙ ПОДХОД
            - Интегрируйте данные из разных источников
            - Выявляйте связи между различными аспектами
            - Представляйте целостную картину

            ## НАУЧНАЯ ТОЧНОСТЬ
            - Используйте точную научную терминологию
            - Указывайте численные данные с единицами измерения
            - Ссылайтесь на источники информации

            ## СТРУКТУРИРОВАННОСТЬ
            - Организуйте информацию логически
            - Используйте заголовки и подзаголовки
            - Выделяйте ключевые моменты

            ## КРИТИЧЕСКИЙ АНАЛИЗ
            - Оценивайте качество данных
            - Указывайте на противоречия если есть
            - Делайте обоснованные выводы

            Адаптируйте структуру ответа под конкретный запрос, но всегда сохраняйте научную строгость.""",
            
            user_prompt_template="""Контекст из научных публикаций:
            {context}
            
            Запрос: {query}
            
            Синтезируйте предоставленную информацию и дайте комплексный научный ответ. 
            Обязательно указывайте источники и сохраняйте точность данных.""",
            
            query_type=QueryType.GENERAL_SYNTHESIS,
            description="Общий синтез информации"
        )
        
        return prompts
    
    def detect_query_type(self, query: str) -> QueryType:
        """
        Определяет тип запроса на основе ключевых слов
        
        Args:
            query (str): Текст запроса
            
        Returns:
            QueryType: Определенный тип запроса
        """
        query_lower = query.lower()
        
        # Ключевые слова для разных типов запросов
        strain_keywords = [
            'штамм', 'strain', 'характеристик', 'свойств', 'описание',
            'gw1-59t', 'lysobacter', 'что известно о'
        ]
        
        comparative_keywords = [
            'сравн', 'различ', 'отлич', 'compare', 'difference', 'между',
            'vs', 'против', 'дифференциальн'
        ]
        
        table_keywords = [
            'таблиц', 'table', 'данные в таблице', 'табличные данные',
            'интерпретир', 'анализ таблицы'
        ]
        
        methodology_keywords = [
            'метод', 'protocol', 'как определ', 'как провести', 'процедур',
            'техник', 'анализ', 'исследован'
        ]
        
        # Подсчет совпадений для каждого типа
        scores = {
            QueryType.STRAIN_ANALYSIS: sum(1 for kw in strain_keywords if kw in query_lower),
            QueryType.COMPARATIVE_ANALYSIS: sum(1 for kw in comparative_keywords if kw in query_lower),
            QueryType.TABLE_INTERPRETATION: sum(1 for kw in table_keywords if kw in query_lower),
            QueryType.METHODOLOGY: sum(1 for kw in methodology_keywords if kw in query_lower)
        }
        
        # Определяем тип с максимальным счетом
        max_score = max(scores.values())
        if max_score > 0:
            for query_type, score in scores.items():
                if score == max_score:
                    return query_type
        
        # По умолчанию возвращаем общий синтез
        return QueryType.GENERAL_SYNTHESIS
    
    def get_prompt(self, query_type: QueryType) -> PromptTemplate:
        """
        Возвращает промпт для указанного типа запроса
        
        Args:
            query_type (QueryType): Тип запроса
            
        Returns:
            PromptTemplate: Шаблон промпта
        """
        return self.prompts.get(query_type, self.prompts[QueryType.GENERAL_SYNTHESIS])
    
    def format_prompt(self, query: str, context: str, query_type: Optional[QueryType] = None) -> Dict[str, str]:
        """
        Форматирует промпт для конкретного запроса
        
        Args:
            query (str): Запрос пользователя
            context (str): Контекст из документов
            query_type (Optional[QueryType]): Тип запроса (определяется автоматически если не указан)
            
        Returns:
            Dict[str, str]: Отформатированный промпт с system и user частями
        """
        if query_type is None:
            query_type = self.detect_query_type(query)
        
        prompt_template = self.get_prompt(query_type)
        
        return {
            'system': prompt_template.system_prompt,
            'user': prompt_template.user_prompt_template.format(
                query=query,
                context=context
            ),
            'query_type': query_type.value
        }
    
    def enhance_context_for_tables(self, context: str, table_metadata: List[Dict[str, Any]]) -> str:
        """
        Улучшает контекст для лучшей интерпретации таблиц
        
        Args:
            context (str): Исходный контекст
            table_metadata (List[Dict[str, Any]]): Метаданные таблиц
            
        Returns:
            str: Улучшенный контекст
        """
        enhanced_context = context
        
        # Добавляем информацию о структуре таблиц
        for i, metadata in enumerate(table_metadata):
            if metadata.get('element_type') == 'table':
                table_info = f"\n[ТАБЛИЦА {i+1}]"
                
                if metadata.get('table_title'):
                    table_info += f"\nЗаголовок: {metadata['table_title']}"
                
                if metadata.get('estimated_rows'):
                    table_info += f"\nСтрок: {metadata['estimated_rows']}"
                
                if metadata.get('estimated_cols'):
                    table_info += f"\nСтолбцов: {metadata['estimated_cols']}"
                
                if metadata.get('likely_differential_table'):
                    table_info += f"\nТип: Дифференциальные характеристики"
                
                table_info += "\n"
                enhanced_context = table_info + enhanced_context
        
        return enhanced_context
    
    def get_available_query_types(self) -> List[Dict[str, str]]:
        """
        Возвращает список доступных типов запросов с описаниями
        
        Returns:
            List[Dict[str, str]]: Список типов запросов
        """
        return [
            {
                'type': query_type.value,
                'description': prompt.description
            }
            for query_type, prompt in self.prompts.items()
        ] 