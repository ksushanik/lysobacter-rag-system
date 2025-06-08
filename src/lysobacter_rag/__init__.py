"""
RAG-система для обработки PDF документов о лизобактериях
"""

from .pdf_extractor import PDFExtractor, ExtractedTable, ExtractedDocument
from .data_processor import DataProcessor, DocumentChunk
from .indexer import Indexer

__version__ = "1.0.0"
__author__ = "AI Assistant"

__all__ = [
    'PDFExtractor', 
    'ExtractedTable', 
    'ExtractedDocument',
    'DataProcessor', 
    'DocumentChunk',
    'Indexer'
] 