#!/usr/bin/env python3
"""
РЕВОЛЮЦИОННАЯ СТРАТЕГИЯ: Умный чанкинг для научных текстов
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import nltk
from sentence_transformers import SentenceTransformer

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent / "src"))

class ScientificTextChunker:
    """Умный чанкер для научных текстов о Lysobacter"""
    
    def __init__(self, target_chunk_size: int = 400, overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap
        
        # Научные паттерны для Lysobacter
        self.section_patterns = [
            r"(Description|Morphology|Physiology|Biochemical characteristics)",
            r"(Growth conditions|Temperature range|pH range)",
            r"(Type strain|Strain|Isolate)",
            r"(G\+C content|DNA composition)",
            r"(16S rRNA|Phylogen|Taxonomy)",
            r"(Etymology|Diagnosis)"
        ]
        
        # Ключевые научные термины
        self.key_terms = [
            "Lysobacter", "sp. nov.", "type strain", "isolate",
            "G+C content", "16S rRNA", "phylogenetic",
            "temperature", "pH", "growth", "morphology",
            "catalase", "oxidase", "gram-negative",
            "antibiotic", "antimicrobial", "biocontrol"
        ]
        
    def split_into_smart_chunks(self, text: str, source_pdf: str = "") -> List[Dict]:
        """Умная разбивка текста на семантически связанные чанки"""
        
        # 1. Предварительная очистка
        text = self._clean_text(text)
        
        # 2. Поиск секций
        sections = self._identify_sections(text)
        
        # 3. Разбивка на предложения
        sentences = self._split_sentences(text)
        
        # 4. Создание умных чанков
        chunks = self._create_semantic_chunks(sentences, sections)
        
        # 5. Оптимизация размера чанков
        optimized_chunks = self._optimize_chunk_sizes(chunks)
        
        # 6. Добавление метаданных
        result = []
        for i, chunk in enumerate(optimized_chunks):
            result.append({
                'text': chunk['text'],
                'metadata': {
                    'source_pdf': source_pdf,
                    'chunk_type': chunk['type'],
                    'chunk_index': i,
                    'section': chunk.get('section', ''),
                    'key_terms': chunk.get('key_terms', []),
                    'scientific_importance': chunk.get('importance', 'medium')
                }
            })
            
        return result
    
    def _clean_text(self, text: str) -> str:
        """Очистка и нормализация научного текста"""
        
        # Исправляем разорванные слова
        text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
        
        # Исправляем разорванные числа и единицы
        text = re.sub(r'(\d+)\s*°\s*C', r'\1°C', text)
        text = re.sub(r'(\d+)\s*%', r'\1%', text)
        text = re.sub(r'pH\s+(\d+)', r'pH \1', text)
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Исправляем научные сокращения
        text = re.sub(r'\bsp\.\s*nov\.\s*', 'sp. nov. ', text)
        text = re.sub(r'\bgen\.\s*nov\.\s*', 'gen. nov. ', text)
        
        return text.strip()
    
    def _identify_sections(self, text: str) -> List[Dict]:
        """Определение семантических секций в тексте"""
        sections = []
        
        for pattern in self.section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                sections.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': match.group(1),
                    'importance': 'high'
                })
        
        # Сортируем по позиции
        sections.sort(key=lambda x: x['start'])
        return sections
    
    def _split_sentences(self, text: str) -> List[Dict]:
        """Разбивка на предложения с анализом важности"""
        
        # Простая разбивка по предложениям
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        result = []
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:  # Пропускаем очень короткие
                continue
                
            # Анализируем важность предложения
            importance = self._analyze_sentence_importance(sentence)
            key_terms = self._extract_key_terms(sentence)
            
            result.append({
                'text': sentence.strip(),
                'index': i,
                'importance': importance,
                'key_terms': key_terms,
                'length': len(sentence)
            })
            
        return result
    
    def _analyze_sentence_importance(self, sentence: str) -> str:
        """Анализ важности предложения для научного описания"""
        
        # Высокая важность
        high_indicators = [
            r'type strain', r'sp\. nov\.', r'isolate', r'strain.*isolated',
            r'G\+C content', r'DNA.*mol%', r'16S rRNA',
            r'temperature.*range', r'pH.*range', r'growth.*temperature',
            r'gram-negative', r'gram-positive', r'cell.*morphology',
            r'catalase.*positive', r'oxidase.*positive'
        ]
        
        # Средняя важность  
        medium_indicators = [
            r'phylogenetic', r'sequence', r'similarity',
            r'antibiotic', r'antimicrobial', r'biocontrol',
            r'enzyme', r'activity', r'substrate'
        ]
        
        sentence_lower = sentence.lower()
        
        for pattern in high_indicators:
            if re.search(pattern, sentence_lower):
                return 'high'
        
        for pattern in medium_indicators:
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
        
        # Дополнительный поиск числовых данных
        numbers = re.findall(r'\d+(?:\.\d+)?°C|\d+(?:\.\d+)?%|pH\s+\d+(?:\.\d+)?', sentence)
        found_terms.extend(numbers)
        
        return found_terms
    
    def _create_semantic_chunks(self, sentences: List[Dict], sections: List[Dict]) -> List[Dict]:
        """Создание семантически связанных чанков"""
        chunks = []
        current_chunk = {
            'sentences': [],
            'total_length': 0,
            'type': 'text',
            'section': '',
            'importance': 'medium',
            'key_terms': []
        }
        
        for sentence in sentences:
            # Проверяем, не превысим ли размер
            potential_length = current_chunk['total_length'] + sentence['length']
            
            if potential_length > self.target_chunk_size and current_chunk['sentences']:
                # Сохраняем текущий чанк
                chunks.append(self._finalize_chunk(current_chunk))
                
                # Начинаем новый с перекрытием
                current_chunk = self._start_new_chunk_with_overlap(current_chunk, sentence)
            else:
                # Добавляем предложение в текущий чанк
                current_chunk['sentences'].append(sentence)
                current_chunk['total_length'] += sentence['length']
                current_chunk['key_terms'].extend(sentence['key_terms'])
                
                # Обновляем важность чанка
                if sentence['importance'] == 'high':
                    current_chunk['importance'] = 'high'
                elif sentence['importance'] == 'medium' and current_chunk['importance'] == 'low':
                    current_chunk['importance'] = 'medium'
        
        # Не забываем последний чанк
        if current_chunk['sentences']:
            chunks.append(self._finalize_chunk(current_chunk))
        
        return chunks
    
    def _finalize_chunk(self, chunk: Dict) -> Dict:
        """Финализация чанка"""
        text = ' '.join([s['text'] for s in chunk['sentences']])
        
        return {
            'text': text,
            'type': chunk['type'],
            'section': chunk['section'],
            'importance': chunk['importance'],
            'key_terms': list(set(chunk['key_terms'])),  # Убираем дубликаты
            'sentence_count': len(chunk['sentences'])
        }
    
    def _start_new_chunk_with_overlap(self, prev_chunk: Dict, new_sentence: Dict) -> Dict:
        """Начинаем новый чанк с умным перекрытием"""
        
        # Берем последние важные предложения для перекрытия
        overlap_sentences = []
        overlap_length = 0
        
        for sentence in reversed(prev_chunk['sentences']):
            if overlap_length + sentence['length'] <= self.overlap:
                overlap_sentences.insert(0, sentence)
                overlap_length += sentence['length']
            else:
                break
        
        return {
            'sentences': overlap_sentences + [new_sentence],
            'total_length': overlap_length + new_sentence['length'],
            'type': 'text',
            'section': '',
            'importance': new_sentence['importance'],
            'key_terms': new_sentence['key_terms'].copy()
        }
    
    def _optimize_chunk_sizes(self, chunks: List[Dict]) -> List[Dict]:
        """Оптимизация размеров чанков"""
        optimized = []
        
        for chunk in chunks:
            # Слишком короткие чанки объединяем с соседними
            if len(chunk['text']) < 100 and optimized:
                # Объединяем с предыдущим
                prev_chunk = optimized[-1]
                prev_chunk['text'] += ' ' + chunk['text']
                prev_chunk['key_terms'].extend(chunk['key_terms'])
                prev_chunk['key_terms'] = list(set(prev_chunk['key_terms']))
                
                # Обновляем важность
                if chunk['importance'] == 'high':
                    prev_chunk['importance'] = 'high'
            else:
                optimized.append(chunk)
        
        return optimized

# Тестирование умного чанкера
if __name__ == "__main__":
    # Тестовый научный текст
    test_text = """
    Lysobacter capsici sp. nov. is a gram-negative, aerobic bacterium isolated from the rhizosphere of pepper plants. 
    The type strain YC5194T was isolated from soil samples collected in South Korea. 
    Cells are rod-shaped, measuring 0.3-0.5 × 2.0-20 μm, and are motile by means of a polar flagellum.
    
    The temperature range for growth is 15-37°C, with optimal growth at 28°C. 
    The pH range is 5.5-8.5, with optimal growth at pH 7.0. 
    The strain is catalase-positive and oxidase-positive.
    
    The G+C content of the genomic DNA is 65.4 mol%. 
    16S rRNA gene sequence analysis showed highest similarity to Lysobacter gummosus with 97.8% identity.
    
    Phylogenetic analysis based on 16S rRNA sequences placed the strain in the genus Lysobacter.
    The strain shows antimicrobial activity against various plant pathogens.
    """
    
    chunker = ScientificTextChunker(target_chunk_size=300, overlap=50)
    chunks = chunker.split_into_smart_chunks(test_text, "test.pdf")
    
    print("🧬 ТЕСТ УМНОГО ЧАНКИНГА")
    print("=" * 50)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n📝 Чанк {i}:")
        print(f"   Длина: {len(chunk['text'])} символов")
        print(f"   Важность: {chunk['metadata']['scientific_importance']}")
        print(f"   Ключевые термины: {', '.join(chunk['metadata']['key_terms'][:5])}")
        print(f"   Текст: {chunk['text'][:100]}...")
    
    print(f"\n✅ Создано {len(chunks)} умных чанков")
    avg_length = sum(len(c['text']) for c in chunks) / len(chunks)
    print(f"📊 Средняя длина: {avg_length:.0f} символов") 