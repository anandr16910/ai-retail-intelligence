"""Main application entry point for AI Retail Intelligence Platform."""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.forecasting_model import PriceForecastingEngine
from src.pricing_engine import PricingEngine
from src.document_parser import DocumentParser
from src.market_copilot import MarketCopilot
from src.config import settings
from src.exceptions import AIRetailIntelligenceError


class AIRetailIntelligencePlatform:
    """Main application class that wires all components together."""
    
    def __init__(self):
        """Initialize the platform with all components."""
        self.data_loader = None
        self.forecasting_engine = None
        self.pricing_engine = None
        self.document_parser = None
        self.market_copilot = None
        self.initialized = False
        
    def initialize(self):
        """Initialize all platform components."""
        try:
            print("Initializing AI Retail Intelligence Platform...")
            
            # Initialize core components
            print("- Initializing data loader...")
            self.data_loader = DataLoader()
            
            print("- Initializing forecasting engine...")
            self.forecasting_engine = PriceForecastingEngine()
            
            print("- Initializing pricing engine...")
            self.pricing_engine = PricingEngine()
            
            print("- Initializing document parser...")
            self.document_parser = DocumentParser()
            
            print("- Initializing market copilot...")
            self.market_copilot = MarketCopilot()
            
            # Load and process initial data
            print("- Loading initial data...")
            self._load_initial_data()
            
            self.initialized = True
            print("✓ Platform initialized successfully!")
            
        except Exception as e:
            print(f"✗ Failed to initialize platform: {str(e)}")
            raise AIRetailIntelligenceError(f"Platform initialization failed: {str(e)}")
    
    def _load_initial_data(self):
        """Load initial data and train models."""
        try:
            # Load all available data
            all_data = self.data_loader.load_all_data()
            
            if not all_data:
                print("  Warning: No data loaded. Generating sample data...")
                from src.data_generator import SampleDataGenerator
                generator = SampleDataGenerator()
                generator.save_all_datasets()
                all_data = self.data_loader.load_all_data()
            
            # Process each dataset
            for symbol, data in all_data.items():
                if data.empty:
                    print(f"  Warning: No data for {symbol}")
                    continue
                
                print(f"  Processing {symbol} data ({len(data)} records)...")
                
                # Train forecasting models
                try:
                    self.forecasting_engine.train_model(
                        data=data,
                        symbol=symbol.upper(),
                        model_name='moving_average'
                    )
                    print(f"    ✓ Trained forecasting model for {symbol}")
                except Exception as e:
                    print(f"    Warning: Could not train forecasting model for {symbol}: {str(e)}")
                
                # Update pricing engine with price history
                try:
                    prices = data['close'].tolist()
                    self.pricing_engine.update_price_history(symbol.upper(), prices)
                    print(f"    ✓ Updated pricing engine for {symbol}")
                except Exception as e:
                    print(f"    Warning: Could not update pricing engine for {symbol}: {str(e)}")
                
                # Update market copilot context
                try:
                    current_price = data['close'].iloc[-1]
                    price_data = {
                        symbol.upper(): {
                            'current_price': float(current_price),
                            'trend': 'stable',
                            'data_points': len(data)
                        }
                    }
                    
                    # Get existing context and update
                    existing_context = self.market_copilot.context_data.get('price_data', {})
                    existing_context.update(price_data)
                    self.market_copilot.update_context({'price_data': existing_context})
                    
                    print(f"    ✓ Updated market copilot context for {symbol}")
                except Exception as e:
                    print(f"    Warning: Could not update market copilot for {symbol}: {str(e)}")
            
            print(f"  ✓ Processed data for {len(all_data)} assets")
            
        except Exception as e:
            print(f"  Warning: Data loading encountered issues: {str(e)}")
    
    def run_demo(self):
        """Run a demonstration of platform capabilities."""
        if not self.initialized:
            self.initialize()
        
        print("\n" + "="*60)
        print("AI RETAIL INTELLIGENCE PLATFORM DEMO")
        print("="*60)
        
        # Demo 1: Price Forecasting
        print("\n1. PRICE FORECASTING DEMO")
        print("-" * 30)
        
        try:
            # Get available symbols
            symbols = self.pricing_engine.get_available_symbols()
            if symbols:
                symbol = symbols[0]
                print(f"Generating forecast for {symbol}...")
                
                forecast = self.forecasting_engine.predict_prices(
                    symbol=symbol,
                    horizon=7,
                    model_name='moving_average'
                )
                
                print(f"✓ 7-day forecast for {symbol}:")
                for i, price in enumerate(forecast.predicted_prices[:3]):
                    print(f"  Day {i+1}: ${price:.2f}")
                print(f"  ... (showing first 3 days)")
                print(f"  Model accuracy: {forecast.model_metrics.get('accuracy', 'N/A')}")
            else:
                print("No symbols available for forecasting")
                
        except Exception as e:
            print(f"✗ Forecasting demo failed: {str(e)}")
        
        # Demo 2: Pricing Recommendations
        print("\n2. PRICING RECOMMENDATIONS DEMO")
        print("-" * 35)
        
        try:
            if symbols:
                symbol = symbols[0]
                current_price = self.pricing_engine.price_history[symbol][-1]
                
                print(f"Getting pricing recommendation for {symbol} (current: ${current_price:.2f})...")
                
                recommendation = self.pricing_engine.recommend_pricing(
                    current_price=current_price,
                    strategy_type="balanced",
                    symbol=symbol
                )
                
                print(f"✓ Pricing recommendation:")
                print(f"  Current price: ${recommendation.current_price:.2f}")
                print(f"  Recommended price: ${recommendation.recommended_price:.2f}")
                print(f"  Change: {recommendation.get_price_change_percentage():.2f}%")
                print(f"  Confidence: {recommendation.confidence_score:.2f}")
                print(f"  Strategy: {recommendation.reasoning}")
            else:
                print("No symbols available for pricing recommendations")
                
        except Exception as e:
            print(f"✗ Pricing demo failed: {str(e)}")
        
        # Demo 3: Document Analysis
        print("\n3. DOCUMENT ANALYSIS DEMO")
        print("-" * 30)
        
        try:
            sample_text = """
            Gold prices have shown strong performance this quarter, rising 15% due to increased 
            market volatility and inflation concerns. Silver has also gained 12%, following 
            gold's upward trend. The Federal Reserve's monetary policy decisions continue to 
            impact precious metals markets. Analysts expect continued growth in Q4 2024.
            """
            
            print("Analyzing sample financial document...")
            
            analysis = self.document_parser.parse_document(
                text_content=sample_text,
                document_id="demo_doc"
            )
            
            print(f"✓ Document analysis complete:")
            print(f"  Document type: {analysis.document_type}")
            print(f"  Entities found: {len(analysis.extracted_entities)}")
            print(f"  Key insights: {len(analysis.get_key_insights())}")
            
            if analysis.market_insights:
                print(f"  Market direction: {analysis.market_insights.get('market_direction', 'N/A')}")
                print(f"  Volatility outlook: {analysis.market_insights.get('volatility_outlook', 'N/A')}")
                
        except Exception as e:
            print(f"✗ Document analysis demo failed: {str(e)}")
        
        # Demo 4: Market Copilot
        print("\n4. MARKET COPILOT DEMO")
        print("-" * 25)
        
        try:
            sample_queries = [
                "What is the current gold price?",
                "How is the market trending?",
                "What are the forecasts for silver?"
            ]
            
            for query in sample_queries:
                print(f"\nQuery: {query}")
                response = self.market_copilot.process_query(query)
                print(f"Response: {response}")
                
        except Exception as e:
            print(f"✗ Market copilot demo failed: {str(e)}")
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            'platform_initialized': self.initialized,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'data_loader': self.data_loader is not None,
                'forecasting_engine': self.forecasting_engine is not None,
                'pricing_engine': self.pricing_engine is not None,
                'document_parser': self.document_parser is not None,
                'market_copilot': self.market_copilot is not None
            },
            'data_status': {},
            'model_status': {},
            'configuration': {
                'data_directory': settings.data_dir,
                'model_directory': settings.model_dir,
                'api_host': settings.api_host,
                'api_port': settings.api_port
            }
        }
        
        if self.initialized:
            # Add detailed status information
            if self.pricing_engine:
                status['data_status']['available_symbols'] = self.pricing_engine.get_available_symbols()
            
            if self.forecasting_engine:
                status['model_status'] = self.forecasting_engine.get_model_info()
            
            if self.market_copilot:
                status['copilot_status'] = self.market_copilot.get_copilot_stats()
        
        return status
    
    def start_api_server(self, host: str = None, port: int = None, reload: bool = False):
        """Start the FastAPI server."""
        if not self.initialized:
            self.initialize()
        
        try:
            from src.api import run_server
            run_server(host=host, port=port, reload=reload)
        except ImportError:
            print("Error: FastAPI dependencies not available. Please install required packages.")
            print("Run: pip install fastapi uvicorn")
        except Exception as e:
            print(f"Error starting API server: {str(e)}")


def main():
    """Main entry point with command line interface."""
    parser = argparse.ArgumentParser(description="AI Retail Intelligence Platform")
    parser.add_argument('--mode', choices=['demo', 'server', 'status'], default='demo',
                       help='Run mode: demo, server, or status')
    parser.add_argument('--host', default=None, help='API server host')
    parser.add_argument('--port', type=int, default=None, help='API server port')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    # Create platform instance
    platform = AIRetailIntelligencePlatform()
    
    try:
        if args.mode == 'demo':
            platform.run_demo()
        elif args.mode == 'server':
            platform.start_api_server(host=args.host, port=args.port, reload=args.reload)
        elif args.mode == 'status':
            platform.initialize()
            status = platform.get_system_status()
            print("\nSYSTEM STATUS:")
            print("-" * 20)
            print(f"Platform initialized: {status['platform_initialized']}")
            print(f"Components loaded: {sum(status['components'].values())}/{len(status['components'])}")
            if status['data_status'].get('available_symbols'):
                print(f"Available symbols: {', '.join(status['data_status']['available_symbols'])}")
            print(f"Configuration: {status['configuration']}")
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()