"""Custom exceptions for AI Retail Intelligence Platform."""

from typing import Optional, Dict, Any


class AIRetailIntelligenceError(Exception):
    """Base exception for the AI Retail Intelligence platform."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DataLoadingError(AIRetailIntelligenceError):
    """Raised when data loading fails."""
    pass


class DataValidationError(AIRetailIntelligenceError):
    """Raised when data validation fails."""
    pass


class ModelTrainingError(AIRetailIntelligenceError):
    """Raised when model training fails."""
    pass


class ForecastingError(AIRetailIntelligenceError):
    """Raised when forecasting fails."""
    pass


class PricingEngineError(AIRetailIntelligenceError):
    """Raised when pricing engine encounters errors."""
    pass


class DocumentParsingError(AIRetailIntelligenceError):
    """Raised when document parsing fails."""
    pass


class LLMServiceError(AIRetailIntelligenceError):
    """Raised when LLM service encounters errors."""
    pass


class APIError(AIRetailIntelligenceError):
    """Raised when API operations fail."""
    pass


class ConfigurationError(AIRetailIntelligenceError):
    """Raised when configuration is invalid."""
    pass