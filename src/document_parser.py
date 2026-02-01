"""Document parsing and LLM-based text extraction for AI Retail Intelligence Platform."""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from src.exceptions import DocumentParsingError, LLMServiceError
from src.config import settings


class DocumentType(Enum):
    """Document type classifications."""
    FINANCIAL_REPORT = "financial_report"
    MARKET_ANALYSIS = "market_analysis"
    NEWS_ARTICLE = "news_article"
    RESEARCH_REPORT = "research_report"
    EARNINGS_REPORT = "earnings_report"
    UNKNOWN = "unknown"


@dataclass
class DocumentAnalysis:
    """Data model for document analysis results."""
    document_id: str
    document_type: str
    extracted_entities: List[Dict[str, Any]]
    market_insights: Dict[str, Any]
    confidence_scores: Dict[str, float]
    processing_timestamp: datetime
    
    def get_key_insights(self) -> List[str]:
        """Get high-confidence insights."""
        return [insight for insight, score in self.confidence_scores.items() 
                if score > 0.7]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'document_id': self.document_id,
            'document_type': self.document_type,
            'extracted_entities': self.extracted_entities,
            'market_insights': self.market_insights,
            'confidence_scores': self.confidence_scores,
            'key_insights': self.get_key_insights(),
            'processing_timestamp': self.processing_timestamp.isoformat()
        }


class MockLLMService:
    """Mock LLM service for local development and testing."""
    
    def __init__(self, model_name: str = "mock-llm"):
        """Initialize mock LLM service."""
        self.model_name = model_name
        self.max_tokens = settings.llm_max_tokens
        
        # Predefined responses for different types of queries
        self.response_templates = {
            'entity_extraction': {
                'companies': ['Apple Inc.', 'Microsoft Corp.', 'Amazon.com Inc.'],
                'financial_metrics': ['revenue', 'profit margin', 'market cap'],
                'currencies': ['USD', 'EUR', 'INR'],
                'commodities': ['gold', 'silver', 'oil']
            },
            'sentiment_analysis': {
                'positive': ['growth', 'increase', 'profit', 'bullish', 'optimistic'],
                'negative': ['decline', 'loss', 'bearish', 'pessimistic', 'risk'],
                'neutral': ['stable', 'unchanged', 'maintain', 'steady']
            },
            'market_insights': [
                'Market shows strong upward momentum',
                'Volatility expected to increase in coming weeks',
                'Sector rotation favoring technology stocks',
                'Commodity prices showing seasonal patterns',
                'Interest rate changes affecting market sentiment'
            ]
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial entities from text using pattern matching."""
        try:
            entities = []
            text_lower = text.lower()
            
            # Extract companies (simple pattern matching)
            company_patterns = [
                r'\b([A-Z][a-z]+ (?:Inc\.|Corp\.|Ltd\.|Company))\b',
                r'\b([A-Z]{2,5})\b'  # Stock symbols
            ]
            
            for pattern in company_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    entities.append({
                        'type': 'company',
                        'value': match,
                        'confidence': 0.8
                    })
            
            # Extract financial metrics
            financial_patterns = [
                r'(\$[\d,]+(?:\.\d{2})?)',  # Dollar amounts
                r'([\d,]+(?:\.\d{2})?%)',   # Percentages
                r'(\d+(?:\.\d+)?\s*(?:billion|million|trillion))',  # Large numbers
            ]
            
            for pattern in financial_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    entities.append({
                        'type': 'financial_metric',
                        'value': match,
                        'confidence': 0.7
                    })
            
            # Extract dates
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'type': 'date',
                        'value': match,
                        'confidence': 0.9
                    })
            
            return entities
            
        except Exception as e:
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using keyword matching."""
        try:
            text_lower = text.lower()
            
            positive_score = 0
            negative_score = 0
            neutral_score = 0
            
            # Count positive keywords
            for word in self.response_templates['sentiment_analysis']['positive']:
                positive_score += text_lower.count(word)
            
            # Count negative keywords
            for word in self.response_templates['sentiment_analysis']['negative']:
                negative_score += text_lower.count(word)
            
            # Count neutral keywords
            for word in self.response_templates['sentiment_analysis']['neutral']:
                neutral_score += text_lower.count(word)
            
            # Normalize scores
            total = positive_score + negative_score + neutral_score
            if total == 0:
                return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
            
            return {
                'positive': positive_score / total,
                'negative': negative_score / total,
                'neutral': neutral_score / total
            }
            
        except Exception as e:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
    
    def classify_document(self, text: str) -> Tuple[str, float]:
        """Classify document type based on content."""
        try:
            text_lower = text.lower()
            
            # Define classification keywords
            classification_keywords = {
                'financial_report': ['financial', 'earnings', 'revenue', 'profit', 'balance sheet'],
                'market_analysis': ['market', 'analysis', 'trend', 'forecast', 'outlook'],
                'news_article': ['news', 'breaking', 'reported', 'announced', 'today'],
                'research_report': ['research', 'study', 'analysis', 'recommendation', 'rating'],
                'earnings_report': ['earnings', 'quarterly', 'eps', 'guidance', 'results']
            }
            
            scores = {}
            for doc_type, keywords in classification_keywords.items():
                score = sum(text_lower.count(keyword) for keyword in keywords)
                scores[doc_type] = score
            
            if not scores or max(scores.values()) == 0:
                return DocumentType.UNKNOWN.value, 0.5
            
            best_type = max(scores, key=scores.get)
            confidence = min(0.9, scores[best_type] / 10)  # Normalize confidence
            
            return best_type, confidence
            
        except Exception as e:
            return DocumentType.UNKNOWN.value, 0.5
    
    def generate_insights(self, text: str, entities: List[Dict]) -> Dict[str, Any]:
        """Generate market insights from text and entities."""
        try:
            insights = {}
            
            # Extract key themes
            text_lower = text.lower()
            
            # Market direction insights
            if any(word in text_lower for word in ['growth', 'increase', 'rise', 'up']):
                insights['market_direction'] = 'positive'
            elif any(word in text_lower for word in ['decline', 'decrease', 'fall', 'down']):
                insights['market_direction'] = 'negative'
            else:
                insights['market_direction'] = 'neutral'
            
            # Volatility insights
            if any(word in text_lower for word in ['volatile', 'uncertainty', 'risk']):
                insights['volatility_outlook'] = 'high'
            elif any(word in text_lower for word in ['stable', 'steady', 'consistent']):
                insights['volatility_outlook'] = 'low'
            else:
                insights['volatility_outlook'] = 'moderate'
            
            # Sector insights
            sectors = ['technology', 'healthcare', 'finance', 'energy', 'retail']
            mentioned_sectors = [sector for sector in sectors if sector in text_lower]
            if mentioned_sectors:
                insights['relevant_sectors'] = mentioned_sectors
            
            # Time horizon
            if any(word in text_lower for word in ['short-term', 'immediate', 'near-term']):
                insights['time_horizon'] = 'short-term'
            elif any(word in text_lower for word in ['long-term', 'future', 'years']):
                insights['time_horizon'] = 'long-term'
            else:
                insights['time_horizon'] = 'medium-term'
            
            # Add entity-based insights
            company_entities = [e for e in entities if e.get('type') == 'company']
            if company_entities:
                insights['mentioned_companies'] = [e['value'] for e in company_entities]
            
            financial_entities = [e for e in entities if e.get('type') == 'financial_metric']
            if financial_entities:
                insights['financial_metrics'] = [e['value'] for e in financial_entities]
            
            return insights
            
        except Exception as e:
            return {'error': f'Insight generation failed: {str(e)}'}


class AWSBedrockService:
    """AWS Bedrock-compatible LLM service interface."""
    
    def __init__(self, model_name: str = "anthropic.claude-v2", region: str = None):
        """Initialize AWS Bedrock service."""
        self.model_name = model_name
        self.region = region or settings.aws_region or "us-east-1"
        self.max_tokens = settings.llm_max_tokens
        
        # Note: In production, this would initialize boto3 client
        # For now, fall back to mock service
        self.mock_service = MockLLMService(model_name)
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using AWS Bedrock (fallback to mock)."""
        # In production, this would call AWS Bedrock API
        return self.mock_service.extract_entities(text)
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using AWS Bedrock (fallback to mock)."""
        # In production, this would call AWS Bedrock API
        return self.mock_service.analyze_sentiment(text)
    
    def classify_document(self, text: str) -> Tuple[str, float]:
        """Classify document using AWS Bedrock (fallback to mock)."""
        # In production, this would call AWS Bedrock API
        return self.mock_service.classify_document(text)
    
    def generate_insights(self, text: str, entities: List[Dict]) -> Dict[str, Any]:
        """Generate insights using AWS Bedrock (fallback to mock)."""
        # In production, this would call AWS Bedrock API
        return self.mock_service.generate_insights(text, entities)


class LLMService:
    """Main LLM service with configurable backends."""
    
    def __init__(self, service_type: str = None):
        """Initialize LLM service with specified backend."""
        service_type = service_type or settings.llm_model_name
        
        if service_type == "aws-bedrock":
            self.service = AWSBedrockService()
        else:  # Default to mock
            self.service = MockLLMService()
        
        self.service_type = service_type
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial entities from text."""
        try:
            return self.service.extract_entities(text)
        except Exception as e:
            raise LLMServiceError(f"Entity extraction failed: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text."""
        try:
            return self.service.analyze_sentiment(text)
        except Exception as e:
            raise LLMServiceError(f"Sentiment analysis failed: {str(e)}")
    
    def classify_document(self, text: str) -> Tuple[str, float]:
        """Classify document type."""
        try:
            return self.service.classify_document(text)
        except Exception as e:
            raise LLMServiceError(f"Document classification failed: {str(e)}")
    
    def generate_insights(self, text: str, entities: List[Dict]) -> Dict[str, Any]:
        """Generate market insights."""
        try:
            return self.service.generate_insights(text, entities)
        except Exception as e:
            raise LLMServiceError(f"Insight generation failed: {str(e)}")


class FinancialEntityExtractor:
    """Extract and classify financial entities from text."""
    
    def __init__(self):
        """Initialize entity extractor."""
        self.entity_patterns = {
            'stock_symbol': r'\b[A-Z]{1,5}\b',
            'currency': r'\b(?:USD|EUR|GBP|JPY|INR|CNY)\b',
            'percentage': r'\d+(?:\.\d+)?%',
            'dollar_amount': r'\$[\d,]+(?:\.\d{2})?',
            'market_cap': r'\d+(?:\.\d+)?\s*(?:billion|million|trillion)',
            'date': r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}',
            'company_name': r'\b[A-Z][a-z]+\s+(?:Inc\.|Corp\.|Ltd\.|Company)\b'
        }
    
    def extract_all_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract all financial entities from text."""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append({
                    'type': entity_type,
                    'value': match,
                    'confidence': 0.8
                })
        
        return entities
    
    def extract_specific_entities(self, text: str, entity_types: List[str]) -> List[Dict[str, Any]]:
        """Extract specific types of entities."""
        entities = []
        
        for entity_type in entity_types:
            if entity_type in self.entity_patterns:
                pattern = self.entity_patterns[entity_type]
                matches = re.findall(pattern, text)
                for match in matches:
                    entities.append({
                        'type': entity_type,
                        'value': match,
                        'confidence': 0.8
                    })
        
        return entities


class DocumentParser:
    """Main document processing engine."""
    
    def __init__(self, llm_service_type: str = None):
        """Initialize document parser."""
        self.llm_service = LLMService(llm_service_type)
        self.entity_extractor = FinancialEntityExtractor()
        self.processed_documents = {}
    
    def parse_document(self, document_path: str = None, text_content: str = None, 
                      document_id: str = None) -> DocumentAnalysis:
        """Parse document and extract insights."""
        try:
            # Get document content
            if document_path and os.path.exists(document_path):
                with open(document_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                doc_id = document_id or os.path.basename(document_path)
            elif text_content:
                text = text_content
                doc_id = document_id or f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            else:
                raise DocumentParsingError("No document path or text content provided")
            
            if not text.strip():
                raise DocumentParsingError("Document is empty")
            
            # Extract entities
            entities = self.llm_service.extract_entities(text)
            
            # Classify document
            doc_type, type_confidence = self.llm_service.classify_document(text)
            
            # Analyze sentiment
            sentiment = self.llm_service.analyze_sentiment(text)
            
            # Generate insights
            insights = self.llm_service.generate_insights(text, entities)
            
            # Calculate confidence scores
            confidence_scores = {
                'document_classification': type_confidence,
                'entity_extraction': sum(e.get('confidence', 0) for e in entities) / len(entities) if entities else 0,
                'sentiment_analysis': max(sentiment.values()) if sentiment else 0,
                'insight_generation': 0.7  # Default confidence for insights
            }
            
            # Add sentiment to insights
            insights['sentiment'] = sentiment
            
            # Create analysis result
            analysis = DocumentAnalysis(
                document_id=doc_id,
                document_type=doc_type,
                extracted_entities=entities,
                market_insights=insights,
                confidence_scores=confidence_scores,
                processing_timestamp=datetime.now()
            )
            
            # Store processed document
            self.processed_documents[doc_id] = analysis
            
            return analysis
            
        except Exception as e:
            raise DocumentParsingError(f"Document parsing failed: {str(e)}")
    
    def extract_financial_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial entities from text."""
        try:
            # Use both LLM service and pattern-based extraction
            llm_entities = self.llm_service.extract_entities(text)
            pattern_entities = self.entity_extractor.extract_all_entities(text)
            
            # Combine and deduplicate entities
            all_entities = llm_entities + pattern_entities
            
            # Simple deduplication based on value
            seen_values = set()
            unique_entities = []
            
            for entity in all_entities:
                value = entity.get('value', '').lower()
                if value not in seen_values:
                    seen_values.add(value)
                    unique_entities.append(entity)
            
            return unique_entities
            
        except Exception as e:
            raise DocumentParsingError(f"Entity extraction failed: {str(e)}")
    
    def classify_document_type(self, text: str) -> str:
        """Classify document type."""
        try:
            doc_type, _ = self.llm_service.classify_document(text)
            return doc_type
        except Exception as e:
            return DocumentType.UNKNOWN.value
    
    def extract_market_insights(self, text: str) -> Dict[str, Any]:
        """Extract market insights from text."""
        try:
            entities = self.extract_financial_entities(text)
            insights = self.llm_service.generate_insights(text, entities)
            return insights
        except Exception as e:
            return {'error': f'Market insight extraction failed: {str(e)}'}
    
    def get_processed_document(self, document_id: str) -> Optional[DocumentAnalysis]:
        """Get previously processed document analysis."""
        return self.processed_documents.get(document_id)
    
    def get_all_processed_documents(self) -> Dict[str, DocumentAnalysis]:
        """Get all processed documents."""
        return self.processed_documents.copy()
    
    def analyze_multiple_documents(self, documents: List[Dict[str, str]]) -> List[DocumentAnalysis]:
        """Analyze multiple documents in batch."""
        results = []
        
        for doc in documents:
            try:
                analysis = self.parse_document(
                    document_path=doc.get('path'),
                    text_content=doc.get('content'),
                    document_id=doc.get('id')
                )
                results.append(analysis)
            except Exception as e:
                # Create error result
                error_analysis = DocumentAnalysis(
                    document_id=doc.get('id', 'unknown'),
                    document_type=DocumentType.UNKNOWN.value,
                    extracted_entities=[],
                    market_insights={'error': str(e)},
                    confidence_scores={'error': 0.0},
                    processing_timestamp=datetime.now()
                )
                results.append(error_analysis)
        
        return results
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the LLM service."""
        return {
            'service_type': self.llm_service.service_type,
            'model_name': getattr(self.llm_service.service, 'model_name', 'unknown'),
            'max_tokens': getattr(self.llm_service.service, 'max_tokens', 0),
            'processed_documents': len(self.processed_documents),
            'available_entity_types': list(self.entity_extractor.entity_patterns.keys())
        }