
# Enhanced Search Wrapper - автоматическое улучшение качества при поиске

def enhanced_search(indexer, query, top_k=10):
    """Поиск с автоматическим улучшением качества результатов"""
    
    # Стандартный поиск
    results = indexer.search(query, top_k)
    
    # Правила улучшения
    quality_rules = [
        (r'GW\s*1-\s*5\s*9\s*T', 'GW1-59T'),
        (r'(\w+)\s*-\s*(\d+)\s+T', r'\1-\2T'),
        (r'C\s+(\d+)\s*:\s*(\d+)', r'C\1:\2'),
        (r'(\d+)\s*[-–]\s*(\d+)\s*°?\s*C', r'\1–\2°C'),
        (r'pH\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', r'pH \1–\2'),
        (r'Lyso\s*bacter', 'Lysobacter'),
        (r'(\d+)\s*\.\s*(\d+)', r'\1.\2'),
    ]
    
    # Применяем улучшения к результатам
    enhanced_results = []
    for result in results:
        enhanced_text = result['text']
        
        for pattern, replacement in quality_rules:
            enhanced_text = re.sub(pattern, replacement, enhanced_text)
        
        enhanced_result = result.copy()
        enhanced_result['text'] = enhanced_text
        enhanced_result['quality_enhanced'] = enhanced_text != result['text']
        
        enhanced_results.append(enhanced_result)
    
    return enhanced_results
