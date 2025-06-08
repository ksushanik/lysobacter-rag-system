#!/usr/bin/env python3
"""
Менеджер индексов для системы лизобактерий
Подобно NotebookLM - индексируем данные один раз, используем много раз
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from config import config
from src.lysobacter_rag.pdf_extractor import PDFExtractor
from src.lysobacter_rag.data_processor import DataProcessor
from src.lysobacter_rag.indexer import Indexer
from loguru import logger

class IndexManager:
    """Менеджер для создания и управления персистентными индексами"""
    
    def __init__(self):
        self.storage_dir = config.STORAGE_DIR
        self.index_metadata_file = self.storage_dir / "index_metadata.json"
        self.data_dir = config.DATA_DIR
        
        # Создаем необходимые директории
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def get_index_status(self) -> Dict:
        """Получает статус текущего индекса"""
        
        if not self.index_metadata_file.exists():
            return {
                'exists': False,
                'created_at': None,
                'pdf_count': 0,
                'chunk_count': 0,
                'last_updated': None,
                'status': 'not_created'
            }
        
        try:
            with open(self.index_metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Проверяем, существует ли физический индекс
            chroma_path = Path(config.CHROMA_DB_PATH)
            if not chroma_path.exists():
                return {
                    'exists': False,
                    'status': 'metadata_only',
                    **metadata
                }
            
            # Проверяем актуальность индекса
            pdf_files = list(self.data_dir.glob("*.pdf"))
            current_pdf_count = len(pdf_files)
            
            if current_pdf_count != metadata.get('pdf_count', 0):
                metadata['status'] = 'outdated'
                metadata['current_pdf_count'] = current_pdf_count
            else:
                metadata['status'] = 'ready'
            
            return {
                'exists': True,
                **metadata
            }
            
        except Exception as e:
            logger.error(f"Ошибка при чтении метаданных индекса: {e}")
            return {
                'exists': False,
                'status': 'error',
                'error': str(e)
            }
    
    def create_index(self, force_rebuild: bool = False) -> bool:
        """
        Создает индекс из PDF файлов
        
        Args:
            force_rebuild: Принудительно пересоздать индекс
            
        Returns:
            bool: True если индекс создан успешно
        """
        
        print("🏗️ СОЗДАНИЕ ИНДЕКСА ЗНАНИЙ О ЛИЗОБАКТЕРИЯХ")
        print("=" * 60)
        
        # Проверяем статус существующего индекса
        status = self.get_index_status()
        
        if status['exists'] and status['status'] == 'ready' and not force_rebuild:
            print(f"✅ Индекс уже существует и актуален")
            print(f"   📊 PDF файлов: {status['pdf_count']}")
            print(f"   📚 Чанков: {status['chunk_count']}")
            print(f"   🕒 Создан: {status['created_at']}")
            return True
        
        # Находим PDF файлы
        pdf_files = list(self.data_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ PDF файлы не найдены в папке {self.data_dir}")
            return False
        
        print(f"📁 Найдено PDF файлов: {len(pdf_files)}")
        print(f"📂 Папка данных: {self.data_dir}")
        print(f"🗄️ Индекс будет сохранен в: {config.CHROMA_DB_PATH}")
        
        if force_rebuild:
            print("🔄 Принудительное пересоздание индекса...")
        
        try:
            # Шаг 1: Извлечение данных из PDF
            print(f"\n📤 ШАГ 1: Извлечение данных из PDF...")
            extractor = PDFExtractor()
            
            all_docs = []
            success_count = 0
            
            for pdf_file in pdf_files:
                print(f"   📄 Обрабатываю: {pdf_file.name}")
                doc = extractor.extract_from_pdf(str(pdf_file))
                
                if doc:
                    all_docs.append(doc)
                    success_count += 1
                    print(f"      ✅ Извлечен документ: {doc.total_pages} страниц, {len(doc.tables)} таблиц")
                else:
                    print(f"      ⚠️ Не удалось обработать")
            
            print(f"\n📊 Результаты извлечения:")
            print(f"   ✅ Успешно обработано файлов: {success_count}/{len(pdf_files)}")
            print(f"   📋 Всего извлечено документов: {len(all_docs)}")
            
            if not all_docs:
                print(f"❌ Не удалось извлечь данные из PDF файлов")
                return False
            
            # Шаг 2: Обработка данных в чанки
            print(f"\n🔄 ШАГ 2: Обработка данных...")
            processor = DataProcessor()
            chunks = processor.process_documents(all_docs)
            
            print(f"   📚 Создано чанков: {len(chunks)}")
            
            # Показываем статистику
            stats = processor.get_statistics(chunks)
            print(f"   📝 Текстовые чанки: {stats['text_chunks']}")
            print(f"   📊 Табличные чанки: {stats['table_chunks']}")
            print(f"   📏 Средняя длина чанка: {stats['avg_chunk_length']:.0f} символов")
            
            # Шаг 3: Создание векторного индекса
            print(f"\n🗃️ ШАГ 3: Создание векторного индекса...")
            
            # Удаляем старый индекс если нужно
            if force_rebuild:
                try:
                    indexer = Indexer()
                    indexer.delete_collection()
                    print("   🗑️ Старый индекс удален")
                except:
                    pass
            
            # Создаем новый индекс
            indexer = Indexer()
            success = indexer.index_chunks(chunks)
            
            if not success:
                print(f"❌ Ошибка при создании индекса")
                return False
            
            # Шаг 4: Сохранение метаданных
            print(f"\n💾 ШАГ 4: Сохранение метаданных...")
            
            metadata = {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'pdf_count': len(pdf_files),
                'chunk_count': len(chunks),
                'text_chunks': stats['text_chunks'],
                'table_chunks': stats['table_chunks'],
                'sources': stats['sources'],
                'embedding_model': config.EMBEDDING_MODEL,
                'chunk_size': config.CHUNK_SIZE,
                'chunk_overlap': config.CHUNK_OVERLAP
            }
            
            with open(self.index_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Метаданные сохранены")
            
            # Проверяем созданный индекс
            collection_stats = indexer.get_collection_stats()
            
            print(f"\n🎉 ИНДЕКС УСПЕШНО СОЗДАН!")
            print(f"📊 Статистика индекса:")
            print(f"   📚 Всего чанков в БД: {collection_stats['total_chunks']}")
            print(f"   📝 Текстовых чанков: {collection_stats['chunk_types'].get('text', 0)}")
            print(f"   📊 Табличных чанков: {collection_stats['chunk_types'].get('table', 0)}")
            print(f"   📄 Источников: {len(collection_stats['sources'])}")
            print(f"   🗄️ Расположение: {config.CHROMA_DB_PATH}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при создании индекса: {e}")
            print(f"❌ Ошибка при создании индекса: {e}")
            return False

def main():
    """Интерфейс командной строки для управления индексом"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Менеджер индексов для системы лизобактерий")
    parser.add_argument('action', choices=['status', 'create', 'rebuild'],
                       help='Действие с индексом')
    parser.add_argument('--force', action='store_true',
                       help='Принудительное выполнение действия')
    
    args = parser.parse_args()
    
    manager = IndexManager()
    
    if args.action == 'status':
        status = manager.get_index_status()
        print("📊 СТАТУС ИНДЕКСА")
        print("=" * 40)
        
        if status['exists']:
            print(f"✅ Статус: {status['status']}")
            print(f"📅 Создан: {status.get('created_at', 'Неизвестно')}")
            print(f"📄 PDF файлов: {status.get('pdf_count', 0)}")
            print(f"📚 Чанков: {status.get('chunk_count', 0)}")
        else:
            print("❌ Индекс не создан")
            print("💡 Создайте индекс: python index_manager.py create")
    
    elif args.action == 'create':
        manager.create_index(force_rebuild=args.force)
    
    elif args.action == 'rebuild':
        manager.create_index(force_rebuild=True)

if __name__ == "__main__":
    main() 