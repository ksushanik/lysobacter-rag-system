
# ПРИМЕР ИНТЕГРАЦИИ УЛУЧШЕННОГО ПОИСКА

def create_enhanced_rag_pipeline():
    """Создает RAG pipeline с улучшенным поиском"""
    
    from lysobacter_rag.rag_pipeline.rag_pipeline import RAGPipeline
    from lysobacter_rag.indexer.indexer import Indexer
    from enhanced_search_final import enhanced_search_with_quality_fixes
    
    # Создаем стандартные компоненты
    pipeline = RAGPipeline()
    indexer = Indexer()
    
    # Создаем улучшенный метод ask_question
    def enhanced_ask_question(query, top_k=10):
        """Задает вопрос с улучшенным поиском"""
        
        # Используем улучшенный поиск
        relevant_chunks = enhanced_search_with_quality_fixes(indexer, query, top_k)
        
        if not relevant_chunks:
            return {
                'answer': "Извините, релевантная информация не найдена.",
                'sources': [],
                'confidence': 0.0,
                'quality_enhanced': False
            }
        
        # Подсчитываем улучшения
        enhanced_count = sum(1 for chunk in relevant_chunks 
                           if chunk.get('quality_enhanced', False))
        
        # Формируем контекст из улучшенных данных
        context_parts = []
        for i, chunk in enumerate(relevant_chunks, 1):
            source_info = f"[ИСТОЧНИК {i}] {chunk['metadata'].get('source_pdf', 'Неизвестен')}"
            if chunk.get('quality_enhanced', False):
                source_info += " (качество улучшено)"
            
            context_parts.append(f"{source_info}\n{chunk['text']}")
        
        context = "\n\n".join(context_parts)
        
        # Генерируем ответ (при наличии API ключа)
        try:
            # Стандартная генерация ответа
            answer = pipeline._generate_answer(query, context)
            confidence = pipeline._calculate_confidence(relevant_chunks)
        except:
            # Fallback: формируем ответ из найденной информации
            answer = f"На основе найденной информации:\n\n{context[:1000]}..."
            confidence = 0.8 if enhanced_count > 0 else 0.6
        
        return {
            'answer': answer,
            'sources': [chunk['metadata'] for chunk in relevant_chunks],
            'confidence': confidence,
            'quality_enhanced': enhanced_count > 0,
            'enhanced_chunks': enhanced_count,
            'total_chunks': len(relevant_chunks)
        }
    
    # Заменяем метод
    pipeline.enhanced_ask_question = enhanced_ask_question
    
    return pipeline

# ИСПОЛЬЗОВАНИЕ:
# pipeline = create_enhanced_rag_pipeline()
# response = pipeline.enhanced_ask_question("Расскажи о штамме GW1-59T")
# print(f"Качество улучшено: {response['quality_enhanced']}")
