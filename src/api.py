"""FastAPI-based REST API for AI Retail Intelligence Platform."""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from src.data_loader import DataLoader
from src.forecasting_model import PriceForecastingEngine
from src.pricing_engine import PricingEngine
from src.document_parser import DocumentParser
from src.market_copilot import MarketCopilot
from src.config import settings
from src.exceptions import (
    AIRetailIntelligenceError, DataLoadingError, ModelTrainingError,
    ForecastingError, PricingEngineError, DocumentParsingError, LLMServiceError
)


# Pydantic models for request/response validation
class ForecastRequest(BaseModel):
    """Request model for price forecasting."""
    symbol: str = Field(..., description="Asset symbol (gold, silver, etf)")
    horizon: int = Field(default=30, ge=1, le=365, description="Forecast horizon in days")
    model_name: str = Field(default="moving_average", description="Model to use for forecasting")


class PricingRequest(BaseModel):
    """Request model for pricing recommendations."""
    symbol: str = Field(..., description="Asset symbol")
    current_price: float = Field(..., gt=0, description="Current price")
    strategy_type: str = Field(default="balanced", description="Pricing strategy (conservative, balanced, aggressive)")


class CopilotQuery(BaseModel):
    """Request model for market copilot queries."""
    query: str = Field(..., min_length=1, description="User query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class DocumentUpload(BaseModel):
    """Request model for document analysis."""
    content: str = Field(..., min_length=1, description="Document content")
    document_id: Optional[str] = Field(default=None, description="Document identifier")


# Response models
class APIResponse(BaseModel):
    """Standard API response model."""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Global instances
data_loader = None
forecasting_engine = None
pricing_engine = None
document_parser = None
market_copilot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global data_loader, forecasting_engine, pricing_engine, document_parser, market_copilot
    
    try:
        # Initialize components
        data_loader = DataLoader()
        forecasting_engine = PriceForecastingEngine()
        pricing_engine = PricingEngine()
        document_parser = DocumentParser()
        market_copilot = MarketCopilot()
        
        # Load initial data
        try:
            all_data = data_loader.load_all_data()
            
            # Train models and update pricing engine with data
            for symbol, data in all_data.items():
                if not data.empty:
                    # Train forecasting models
                    try:
                        forecasting_engine.train_model(data, symbol=symbol.upper())
                    except Exception as e:
                        print(f"Warning: Could not train model for {symbol}: {str(e)}")
                    
                    # Update pricing engine with price history
                    prices = data['close'].tolist()
                    pricing_engine.update_price_history(symbol.upper(), prices)
                    
                    # Update market copilot context
                    price_data = {
                        symbol.upper(): {
                            'current_price': prices[-1],
                            'trend': 'stable',  # Simplified
                            'data_points': len(prices)
                        }
                    }
                    market_copilot.update_context({'price_data': price_data})
            
            print(f"Successfully initialized with data for {len(all_data)} assets")
            
        except Exception as e:
            print(f"Warning: Could not load initial data: {str(e)}")
        
        yield
        
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        yield
    
    # Shutdown
    print("Shutting down AI Retail Intelligence Platform")


# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="AI Retail Intelligence Platform",
        description="AI-powered market intelligence and demand forecasting platform for retail, commerce, and market analysis",
        version=settings.app_version,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = None


def handle_exceptions(func):
    """Decorator to handle exceptions and return appropriate responses."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DataLoadingError as e:
            raise HTTPException(status_code=400, detail=f"Data loading error: {str(e)}")
        except ModelTrainingError as e:
            raise HTTPException(status_code=400, detail=f"Model training error: {str(e)}")
        except ForecastingError as e:
            raise HTTPException(status_code=400, detail=f"Forecasting error: {str(e)}")
        except PricingEngineError as e:
            raise HTTPException(status_code=400, detail=f"Pricing engine error: {str(e)}")
        except DocumentParsingError as e:
            raise HTTPException(status_code=400, detail=f"Document parsing error: {str(e)}")
        except LLMServiceError as e:
            raise HTTPException(status_code=500, detail=f"LLM service error: {str(e)}")
        except AIRetailIntelligenceError as e:
            raise HTTPException(status_code=500, detail=f"Platform error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    return wrapper


if FASTAPI_AVAILABLE:
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return APIResponse(
            success=True,
            message="AI Retail Intelligence Platform is running",
            data={
                "status": "healthy",
                "version": settings.app_version,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    
    # Price Forecasting Endpoints
    @app.post(f"{settings.api_prefix}/forecast/{{asset}}")
    @handle_exceptions
    async def forecast_asset_price(asset: str, request: ForecastRequest):
        """Generate price forecast for specified asset."""
        if not forecasting_engine:
            raise HTTPException(status_code=503, detail="Forecasting engine not available")
        
        # Validate asset
        valid_assets = ['gold', 'silver', 'etf']
        if asset.lower() not in valid_assets:
            raise HTTPException(status_code=400, detail=f"Invalid asset. Must be one of: {valid_assets}")
        
        # Generate forecast
        result = forecasting_engine.predict_prices(
            symbol=asset.upper(),
            horizon=request.horizon,
            model_name=request.model_name
        )
        
        return APIResponse(
            success=True,
            message=f"Forecast generated for {asset}",
            data=result.to_dict()
        )
    
    
    @app.get(f"{settings.api_prefix}/forecast/models")
    async def get_available_models():
        """Get list of available forecasting models."""
        if not forecasting_engine:
            raise HTTPException(status_code=503, detail="Forecasting engine not available")
        
        model_info = forecasting_engine.get_model_info()
        
        return APIResponse(
            success=True,
            message="Available models retrieved",
            data=model_info
        )
    
    
    # Pricing Recommendation Endpoints
    @app.post(f"{settings.api_prefix}/pricing/recommend")
    @handle_exceptions
    async def get_pricing_recommendation(request: PricingRequest):
        """Get pricing recommendation for an asset."""
        if not pricing_engine:
            raise HTTPException(status_code=503, detail="Pricing engine not available")
        
        recommendation = pricing_engine.recommend_pricing(
            current_price=request.current_price,
            strategy_type=request.strategy_type,
            symbol=request.symbol.upper()
        )
        
        return APIResponse(
            success=True,
            message="Pricing recommendation generated",
            data=recommendation.to_dict()
        )
    
    
    @app.get(f"{settings.api_prefix}/pricing/analysis/{{symbol}}")
    @handle_exceptions
    async def get_pricing_analysis(symbol: str):
        """Get detailed pricing analysis for a symbol."""
        if not pricing_engine:
            raise HTTPException(status_code=503, detail="Pricing engine not available")
        
        insights = pricing_engine.get_pricing_insights(symbol.upper())
        
        return APIResponse(
            success=True,
            message=f"Pricing analysis for {symbol}",
            data=insights
        )
    
    
    @app.get(f"{settings.api_prefix}/pricing/report")
    @handle_exceptions
    async def generate_pricing_report(strategy_type: str = "balanced"):
        """Generate comprehensive pricing report."""
        if not pricing_engine:
            raise HTTPException(status_code=503, detail="Pricing engine not available")
        
        report = pricing_engine.generate_pricing_report(strategy_type=strategy_type)
        
        return APIResponse(
            success=True,
            message="Pricing report generated",
            data=report
        )
    
    
    # Document Processing Endpoints
    @app.post(f"{settings.api_prefix}/documents/parse")
    @handle_exceptions
    async def parse_document(request: DocumentUpload):
        """Parse and analyze a document."""
        if not document_parser:
            raise HTTPException(status_code=503, detail="Document parser not available")
        
        analysis = document_parser.parse_document(
            text_content=request.content,
            document_id=request.document_id
        )
        
        return APIResponse(
            success=True,
            message="Document parsed successfully",
            data=analysis.to_dict()
        )
    
    
    @app.post(f"{settings.api_prefix}/documents/upload")
    @handle_exceptions
    async def upload_document(file: UploadFile = File(...)):
        """Upload and parse a document file."""
        if not document_parser:
            raise HTTPException(status_code=503, detail="Document parser not available")
        
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        analysis = document_parser.parse_document(
            text_content=text_content,
            document_id=file.filename
        )
        
        return APIResponse(
            success=True,
            message=f"Document {file.filename} processed successfully",
            data=analysis.to_dict()
        )
    
    
    @app.get(f"{settings.api_prefix}/documents/{{document_id}}")
    async def get_document_analysis(document_id: str):
        """Get previously processed document analysis."""
        if not document_parser:
            raise HTTPException(status_code=503, detail="Document parser not available")
        
        analysis = document_parser.get_processed_document(document_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return APIResponse(
            success=True,
            message="Document analysis retrieved",
            data=analysis.to_dict()
        )
    
    
    # Market Copilot Endpoints
    @app.post(f"{settings.api_prefix}/copilot/query")
    @handle_exceptions
    async def query_market_copilot(request: CopilotQuery):
        """Query the market copilot AI assistant."""
        if not market_copilot:
            raise HTTPException(status_code=503, detail="Market copilot not available")
        
        response = market_copilot.process_query(request.query, request.context)
        
        return APIResponse(
            success=True,
            message="Query processed",
            data={
                "query": request.query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    
    @app.get(f"{settings.api_prefix}/copilot/insights")
    @handle_exceptions
    async def get_copilot_insights(query: str):
        """Get detailed insights for a query."""
        if not market_copilot:
            raise HTTPException(status_code=503, detail="Market copilot not available")
        
        insights = market_copilot.get_financial_insights(query)
        
        return APIResponse(
            success=True,
            message="Insights generated",
            data=insights
        )
    
    
    @app.get(f"{settings.api_prefix}/copilot/history")
    async def get_conversation_history():
        """Get conversation history."""
        if not market_copilot:
            raise HTTPException(status_code=503, detail="Market copilot not available")
        
        history = market_copilot.get_conversation_history()
        
        return APIResponse(
            success=True,
            message="Conversation history retrieved",
            data={"history": history}
        )
    
    
    @app.get(f"{settings.api_prefix}/copilot/suggestions")
    async def get_query_suggestions():
        """Get suggested queries based on available data."""
        if not market_copilot:
            raise HTTPException(status_code=503, detail="Market copilot not available")
        
        suggestions = market_copilot.suggest_queries()
        
        return APIResponse(
            success=True,
            message="Query suggestions generated",
            data={"suggestions": suggestions}
        )
    
    
    # Data Management Endpoints
    @app.get(f"{settings.api_prefix}/data/status")
    async def get_data_status():
        """Get status of loaded data."""
        if not data_loader:
            raise HTTPException(status_code=503, detail="Data loader not available")
        
        status = {
            "data_directory": data_loader.data_dir,
            "available_datasets": [],
            "pricing_engine_symbols": pricing_engine.get_available_symbols() if pricing_engine else [],
            "forecasting_models": forecasting_engine.get_model_info() if forecasting_engine else {}
        }
        
        # Check for available CSV files
        data_files = ['gold_prices.csv', 'silver_prices.csv', 'etf_prices.csv']
        for file in data_files:
            file_path = os.path.join(data_loader.data_dir, file)
            if os.path.exists(file_path):
                status["available_datasets"].append(file)
        
        return APIResponse(
            success=True,
            message="Data status retrieved",
            data=status
        )
    
    
    @app.post(f"{settings.api_prefix}/data/reload")
    @handle_exceptions
    async def reload_data(background_tasks: BackgroundTasks):
        """Reload data and retrain models."""
        if not data_loader or not forecasting_engine or not pricing_engine:
            raise HTTPException(status_code=503, detail="Required services not available")
        
        def reload_task():
            try:
                # Reload data
                all_data = data_loader.load_all_data()
                
                # Retrain models and update engines
                for symbol, data in all_data.items():
                    if not data.empty:
                        # Retrain forecasting models
                        forecasting_engine.train_model(data, symbol=symbol.upper())
                        
                        # Update pricing engine
                        prices = data['close'].tolist()
                        pricing_engine.update_price_history(symbol.upper(), prices)
                
                print(f"Data reloaded successfully for {len(all_data)} assets")
                
            except Exception as e:
                print(f"Error reloading data: {str(e)}")
        
        background_tasks.add_task(reload_task)
        
        return APIResponse(
            success=True,
            message="Data reload initiated in background",
            data={"status": "reloading"}
        )
    
    
    @app.get(f"{settings.api_prefix}/data/summary/{{symbol}}")
    @handle_exceptions
    async def get_data_summary(symbol: str):
        """Get summary statistics for a symbol's data."""
        if not data_loader:
            raise HTTPException(status_code=503, detail="Data loader not available")
        
        # Load data for the symbol
        try:
            if symbol.lower() == 'gold':
                data = data_loader.load_gold_prices()
            elif symbol.lower() == 'silver':
                data = data_loader.load_silver_prices()
            elif symbol.lower() == 'etf':
                data = data_loader.load_etf_prices()
            else:
                raise HTTPException(status_code=400, detail="Invalid symbol. Must be gold, silver, or etf")
            
            summary = data_loader.get_data_summary(data)
            
            return APIResponse(
                success=True,
                message=f"Data summary for {symbol}",
                data=summary
            )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not load data for {symbol}: {str(e)}")
    
    
    # System Information Endpoints
    @app.get(f"{settings.api_prefix}/system/info")
    async def get_system_info():
        """Get system information and component status."""
        info = {
            "platform": "AI Retail Intelligence Platform",
            "version": settings.app_version,
            "components": {
                "data_loader": data_loader is not None,
                "forecasting_engine": forecasting_engine is not None,
                "pricing_engine": pricing_engine is not None,
                "document_parser": document_parser is not None,
                "market_copilot": market_copilot is not None
            },
            "configuration": {
                "api_prefix": settings.api_prefix,
                "data_directory": settings.data_dir,
                "model_directory": settings.model_dir,
                "default_forecast_horizon": settings.default_forecast_horizon
            }
        }
        
        # Add component-specific info
        if forecasting_engine:
            info["forecasting_models"] = forecasting_engine.get_available_models()
        
        if pricing_engine:
            info["available_symbols"] = pricing_engine.get_available_symbols()
        
        if document_parser:
            info["document_parser_info"] = document_parser.get_service_info()
        
        if market_copilot:
            info["copilot_stats"] = market_copilot.get_copilot_stats()
        
        return APIResponse(
            success=True,
            message="System information retrieved",
            data=info
        )


def create_app():
    """Create and configure the FastAPI application."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI and dependencies not available. Please install required packages.")
    
    return app


def run_server(host: str = None, port: int = None, reload: bool = False):
    """Run the FastAPI server."""
    if not FASTAPI_AVAILABLE:
        print("Error: FastAPI not available. Please install required dependencies.")
        return
    
    host = host or settings.api_host
    port = port or settings.api_port
    
    print(f"Starting AI Retail Intelligence Platform API server...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"API documentation: http://{host}:{port}/docs")
    print(f"OpenAPI schema: http://{host}:{port}/openapi.json")
    
    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server(reload=True)