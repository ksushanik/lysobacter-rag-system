"""
Умный чанкинг для научных текстов о Lysobacter
Интегрируется с продвинутым PDF экстрактором
"""

import re
from typing import List, Dict, Tuple
from loguru import logger


class ScientificTextChunker:
    """Умный чанкер для научных текстов о Lysobacter"""
    
    def __init__(self, target_chunk_size: int = 350, overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap
        
        # Научные паттерны для Lysobacter
        self.section_patterns = [
            r"(Description|Morphology|Physiology|Biochemical characteristics)",
            r"(Growth conditions|Temperature range|pH range|Cultivation)",
            r"(Type strain|Strain|Isolate|Culture)",
            r"(G\+C content|DNA composition|Genomic)",
            r"(16S rRNA|Phylogen|Taxonomy|Systematic)",
            r"(Etymology|Diagnosis|Differentiation)"
        ]
        
        # Ключевые научные термины
        self.key_terms = [
            "Lysobacter", "sp. nov.", "type strain", "isolate", "strain",
            "G+C content", "16S rRNA", "phylogenetic", "taxonomy",
            "temperature", "pH", "growth", "morphology", "cell",
            "catalase", "oxidase", "gram-negative", "gram-positive",
            "antibiotic", "antimicrobial", "biocontrol", "enzyme",
            "rhizosphere", "soil", "plant", "pathogen"
        ]
        
        logger.info(f"Инициализирован умный чанкер: размер {target_chunk_size}, перекрытие {overlap}")
        
    def chunk_extracted_elements(self, elements: List[Dict]) -> List[Dict]:
        """
        Умная разбивка извлечённых элементов на оптимальные чанки
        
        Args:
            elements: Список элементов от продвинутого экстрактора
            
        Returns:
            Список оптимизированных чанков
        """
        logger.info(f"🧬 Начинаю умный чанкинг {len(elements)} элементов")
        
        all_chunks = []
        
        for element in elements:
            if element.get('element_type') == 'table':
                # Таблицы обрабатываем отдельно
                table_chunks = self._chunk_table_element(element)
                all_chunks.extend(table_chunks)
            else:
                # Текстовые элементы разбиваем умно
                text_chunks = self._chunk_text_element(element)
                all_chunks.extend(text_chunks)
        
        # Пост-обработка: объединение слишком коротких чанков
        optimized_chunks = self._optimize_chunks(all_chunks)
        
        logger.info(f"✅ Создано {len(optimized_chunks)} умных чанков")
        logger.info(f"   📊 Средний размер: {self._calculate_avg_size(optimized_chunks)} символов")
        
        return optimized_chunks
    
    def _chunk_text_element(self, element: Dict) -> List[Dict]:
        """Умная разбивка текстового элемента"""
        
        text = element.get('content', '')
        if len(text) < 100:  # Очень короткий текст оставляем как есть
            return [self._create_chunk(text, element, 'text_small')]
        
        # 1. Очистка текста
        cleaned_text = self._clean_scientific_text(text)
        
        # 2. Разбивка на предложения
        sentences = self._split_into_sentences(cleaned_text)
        
        # 3. Создание семантических чанков
        chunks = self._create_semantic_chunks(sentences, element)
        
        return chunks
    
    def _chunk_table_element(self, element: Dict) -> List[Dict]:
        """Обработка табличных элементов"""
        
        table_text = element.get('content', '')
        
        # Таблицы обычно содержат концентрированную информацию
        # Разбиваем только если очень большие
        if len(table_text) <= self.target_chunk_size * 1.5:
            return [self._create_chunk(table_text, element, 'table')]
        
        # Разбиваем большие таблицы по строкам
        lines = table_text.split('\n')
        chunks = []
        current_chunk_lines = []
        current_length = 0
        
        for line in lines:
            line_length = len(line)
            
            if current_length + line_length > self.target_chunk_size and current_chunk_lines:
                # Сохраняем текущий чанк
                chunk_text = '\n'.join(current_chunk_lines)
                chunks.append(self._create_chunk(chunk_text, element, 'table_part'))
                
                # Начинаем новый с перекрытием (последние строки)
                overlap_lines = current_chunk_lines[-2:] if len(current_chunk_lines) > 2 else []
                current_chunk_lines = overlap_lines + [line]
                current_length = sum(len(l) for l in current_chunk_lines)
            else:
                current_chunk_lines.append(line)
                current_length += line_length
        
        # Последний чанк
        if current_chunk_lines:
            chunk_text = '\n'.join(current_chunk_lines)
            chunks.append(self._create_chunk(chunk_text, element, 'table_part'))
        
        return chunks
    
    def _clean_scientific_text(self, text: str) -> str:
        """Очистка и нормализация научного текста"""
        
        # Исправляем разорванные слова
        text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
        
        # Исправляем разорванные числа и единицы
        text = re.sub(r'(\d+)\s*°\s*C', r'\1°C', text)
        text = re.sub(r'(\d+)\s*%', r'\1%', text)
        text = re.sub(r'pH\s+(\d+(?:\.\d+)?)', r'pH \1', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*mol\s*%', r'\1 mol%', text)
        
        # Исправляем научные сокращения
        text = re.sub(r'\bsp\.\s*nov\.\s*', 'sp. nov. ', text)
        text = re.sub(r'\bgen\.\s*nov\.\s*', 'gen. nov. ', text)
        text = re.sub(r'\bvar\.\s*', 'var. ', text)
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Исправляем слитные слова (часто в OCR)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[Dict]:
        """Разбивка на предложения с анализом важности"""
        
        # Разбивка по предложениям (учитываем научные сокращения)
        # Избегаем lookbehind переменной длины
        sentences = []
        
        # Сначала разбиваем простым способом
        raw_sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Затем объединяем обратно те, что были разорваны из-за сокращений
        scientific_abbrevs = ['sp.', 'var.', 'gen.', 'cf.', 'Fig.', 'Tab.', 'etc.', 'vs.', 'Dr.', 'Prof.']
        
        current_sentence = ""
        for sentence in raw_sentences:
            current_sentence += sentence
            
            # Проверяем, заканчивается ли на научное сокращение
            is_abbrev = any(current_sentence.strip().endswith(abbrev) for abbrev in scientific_abbrevs)
            
            if not is_abbrev:
                # Это полное предложение
                sentences.append(current_sentence.strip())
                current_sentence = ""
            else:
                # Добавляем пробел и продолжаем
                current_sentence += " "
        
        # Не забываем последнее предложение
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        result = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 10:  # Пропускаем очень короткие
                continue
                
            # Анализируем важность предложения
            importance = self._analyze_sentence_importance(sentence)
            key_terms = self._extract_key_terms(sentence)
            
            result.append({
                'text': sentence,
                'index': i,
                'importance': importance,
                'key_terms': key_terms,
                'length': len(sentence)
            })
            
        return result
    
    def _analyze_sentence_importance(self, sentence: str) -> str:
        """Анализ важности предложения для научного описания"""
        
        sentence_lower = sentence.lower()
        
        # Критически важные паттерны
        critical_patterns = [
            r'type strain.*isolated', r'strain.*isolated from',
            r'g\+c content.*\d+', r'dna.*\d+.*mol%',
            r'temperature.*range.*\d+.*°c', r'growth.*\d+.*°c',
            r'ph.*range.*\d+', r'ph.*\d+.*\d+',
            r'cell.*size.*\d+', r'cells.*\d+.*μm'
        ]
        
        # Высокая важность
        high_patterns = [
            r'sp\.\s*nov\.', r'type strain', r'isolate',
            r'16s rrna', r'phylogenetic', r'taxonomy',
            r'gram-negative', r'gram-positive',
            r'catalase.*positive', r'oxidase.*positive',
            r'morphology', r'biochemical'
        ]
        
        # Средняя важность  
        medium_patterns = [
            r'growth', r'cultivation', r'medium',
            r'antibiotic', r'antimicrobial', r'activity',
            r'sequence', r'similarity', r'identity'
        ]
        
        # Проверяем в порядке важности
        for pattern in critical_patterns:
            if re.search(pattern, sentence_lower):
                return 'critical'
        
        for pattern in high_patterns:
            if re.search(pattern, sentence_lower):
                return 'high'
        
        for pattern in medium_patterns:
            if re.search(pattern, sentence_lower):
                return 'medium'
        
        return 'low'
    
    def _extract_key_terms(self, sentence: str) -> List[str]:
        """Извлечение ключевых терминов из предложения"""
        found_terms = []
        
        sentence_lower = sentence.lower()
        for term in self.key_terms:
            if term.lower() in sentence_lower:
                found_terms.append(term)
        
        # Дополнительный поиск научных данных
        scientific_data = []
        
        # Температуры
        temps = re.findall(r'\d+(?:\.\d+)?°C', sentence)
        scientific_data.extend(temps)
        
        # pH значения
        ph_vals = re.findall(r'pH\s+\d+(?:\.\d+)?', sentence)
        scientific_data.extend(ph_vals)
        
        # G+C содержание
        gc_vals = re.findall(r'\d+(?:\.\d+)?\s*mol%', sentence)
        scientific_data.extend(gc_vals)
        
        # Размеры клеток
        sizes = re.findall(r'\d+(?:\.\d+)?[-×]\d+(?:\.\d+)?\s*μm', sentence)
        scientific_data.extend(sizes)
        
        found_terms.extend(scientific_data)
        
        return found_terms
    
    def _create_semantic_chunks(self, sentences: List[Dict], original_element: Dict) -> List[Dict]:
        """Создание семантически связанных чанков"""
        
        if not sentences:
            return []
        
        chunks = []
        current_chunk = {
            'sentences': [],
            'total_length': 0,
            'importance': 'low',
            'key_terms': []
        }
        
        for sentence in sentences:
            # Проверяем размер
            potential_length = current_chunk['total_length'] + sentence['length']
            
            if potential_length > self.target_chunk_size and current_chunk['sentences']:
                # Сохраняем текущий чанк
                chunks.append(self._finalize_semantic_chunk(current_chunk, original_element))
                
                # Начинаем новый с умным перекрытием
                current_chunk = self._start_new_chunk_with_overlap(current_chunk, sentence)
            else:
                # Добавляем предложение
                current_chunk['sentences'].append(sentence)
                current_chunk['total_length'] += sentence['length']
                current_chunk['key_terms'].extend(sentence['key_terms'])
                
                # Обновляем важность
                if sentence['importance'] in ['critical', 'high']:
                    current_chunk['importance'] = sentence['importance']
                elif sentence['importance'] == 'medium' and current_chunk['importance'] == 'low':
                    current_chunk['importance'] = 'medium'
        
        # Последний чанк
        if current_chunk['sentences']:
            chunks.append(self._finalize_semantic_chunk(current_chunk, original_element))
        
        return chunks
    
    def _finalize_semantic_chunk(self, chunk: Dict, original_element: Dict) -> Dict:
        """Финализация семантического чанка"""
        
        text = ' '.join([s['text'] for s in chunk['sentences']])
        
        # Создаем метаданные
        metadata = original_element.get('metadata', {}).copy()
        metadata.update({
            'chunk_type': 'text',
            'scientific_importance': chunk['importance'],
            'key_terms': list(set(chunk['key_terms'])),  # Убираем дубликаты
            'sentence_count': len(chunk['sentences']),
            'chunking_method': 'semantic'
        })
        
        return {
            'content': text,
            'metadata': metadata,
            'page_number': original_element.get('page_number', 1),
            'confidence': original_element.get('confidence', 0.8)
        }
    
    def _start_new_chunk_with_overlap(self, prev_chunk: Dict, new_sentence: Dict) -> Dict:
        """Начинаем новый чанк с умным перекрытием"""
        
        # Берем важные предложения для перекрытия
        overlap_sentences = []
        overlap_length = 0
        
        # Приоритет важным предложениям
        important_sentences = [s for s in prev_chunk['sentences'] 
                             if s['importance'] in ['critical', 'high']]
        
        if important_sentences:
            # Берем последние важные предложения
            for sentence in reversed(important_sentences[-2:]):
                if overlap_length + sentence['length'] <= self.overlap:
                    overlap_sentences.insert(0, sentence)
                    overlap_length += sentence['length']
        else:
            # Берем последние предложения
            for sentence in reversed(prev_chunk['sentences'][-2:]):
                if overlap_length + sentence['length'] <= self.overlap:
                    overlap_sentences.insert(0, sentence)
                    overlap_length += sentence['length']
        
        return {
            'sentences': overlap_sentences + [new_sentence],
            'total_length': overlap_length + new_sentence['length'],
            'importance': new_sentence['importance'],
            'key_terms': new_sentence['key_terms'].copy()
        }
    
    def _create_chunk(self, text: str, original_element: Dict, chunk_type: str) -> Dict:
        """Создание простого чанка"""
        
        metadata = original_element.get('metadata', {}).copy()
        metadata.update({
            'chunk_type': chunk_type,
            'chunking_method': 'simple'
        })
        
        if chunk_type.startswith('table'):
            metadata['key_terms'] = self._extract_key_terms(text)
            metadata['scientific_importance'] = 'high'  # Таблицы обычно важны
        
        return {
            'content': text,
            'metadata': metadata,
            'page_number': original_element.get('page_number', 1),
            'confidence': original_element.get('confidence', 0.8)
        }
    
    def _optimize_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Пост-обработка: оптимизация размеров чанков"""
        
        if not chunks:
            return chunks
        
        optimized = []
        
        for chunk in chunks:
            text_length = len(chunk['content'])
            
            # Слишком короткие чанки объединяем с предыдущими
            if text_length < 100 and optimized:
                prev_chunk = optimized[-1]
                
                # Проверяем совместимость
                if self._chunks_compatible(prev_chunk, chunk):
                    # Объединяем
                    combined_text = prev_chunk['content'] + ' ' + chunk['content']
                    prev_chunk['content'] = combined_text
                    
                    # Объединяем ключевые термины
                    prev_terms = prev_chunk['metadata'].get('key_terms', [])
                    curr_terms = chunk['metadata'].get('key_terms', [])
                    prev_chunk['metadata']['key_terms'] = list(set(prev_terms + curr_terms))
                    
                    # Обновляем важность
                    prev_importance = prev_chunk['metadata'].get('scientific_importance', 'low')
                    curr_importance = chunk['metadata'].get('scientific_importance', 'low')
                    
                    importance_order = ['low', 'medium', 'high', 'critical']
                    if importance_order.index(curr_importance) > importance_order.index(prev_importance):
                        prev_chunk['metadata']['scientific_importance'] = curr_importance
                    
                    continue
            
            optimized.append(chunk)
        
        return optimized
    
    def _chunks_compatible(self, chunk1: Dict, chunk2: Dict) -> bool:
        """Проверка совместимости чанков для объединения"""
        
        # Совместимы если:
        # 1. С одной страницы
        # 2. Одинаковый тип (текст с текстом, таблица с таблицей)
        # 3. Объединённый размер не превышает лимит
        
        same_page = chunk1.get('page_number') == chunk2.get('page_number')
        
        type1 = chunk1['metadata'].get('chunk_type', 'text')
        type2 = chunk2['metadata'].get('chunk_type', 'text')
        compatible_types = (type1.startswith('text') and type2.startswith('text')) or \
                          (type1.startswith('table') and type2.startswith('table'))
        
        combined_length = len(chunk1['content']) + len(chunk2['content'])
        size_ok = combined_length <= self.target_chunk_size * 1.5
        
        return same_page and compatible_types and size_ok
    
    def _calculate_avg_size(self, chunks: List[Dict]) -> int:
        """Вычисление среднего размера чанков"""
        if not chunks:
            return 0
        
        total_size = sum(len(chunk['content']) for chunk in chunks)
        return int(total_size / len(chunks)) 