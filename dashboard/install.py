#!/usr/bin/env python3
"""
Dashboard Installation Script
============================

Installation and setup script for the AI Retail Intelligence web dashboard.
This script handles dependency installation and initial configuration.

Usage:
    python dashboard/install.py [--dev] [--force]
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def print_header():
    """Print installation header."""
    print("🛒 AI Retail Intelligence Dashboard Installer")
    print("=" * 50)

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_main_platform():
    """Check if main platform is available."""
    print("🔍 Checking main platform...")
    
    project_root = Path(__file__).parent.parent
    
    # Check if main files exist
    required_files = [
        "main.py",
        "requirements.txt",
        "src/competitive_pricing.py",
        "src/forecasting_model.py",
        "src/market_copilot.py"
    ]
    
    for file_path in required_files:
        if not (project_root / file_path).exists():
            print(f"❌ Missing required file: {file_path}")
            return False
    
    print("✅ Main platform files found")
    return True

def install_main_dependencies():
    """Install main platform dependencies."""
    print("📦 Installing main platform dependencies...")
    
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Main platform dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install main dependencies: {e}")
        return False

def install_dashboard_dependencies(dev_mode=False):
    """Install dashboard-specific dependencies."""
    print("🎨 Installing dashboard dependencies...")
    
    dashboard_dir = Path(__file__).parent
    requirements_file = dashboard_dir / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dashboard dependencies installed")
        
        # Install development dependencies if requested
        if dev_mode:
            dev_packages = [
                "pytest>=7.0.0",
                "black>=22.0.0",
                "flake8>=4.0.0",
                "mypy>=0.950"
            ]
            
            for package in dev_packages:
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", package
                    ])
                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to install dev package: {package}")
            
            print("✅ Development dependencies installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dashboard dependencies: {e}")
        return False

def verify_installation():
    """Verify that installation was successful."""
    print("🔬 Verifying installation...")
    
    # Test imports
    test_imports = [
        ("streamlit", "Streamlit web framework"),
        ("plotly", "Plotly visualization library"),
        ("requests", "HTTP requests library"),
        ("pandas", "Data manipulation library"),
        ("numpy", "Numerical computing library")
    ]
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - Import failed")
            return False
    
    # Test main platform imports
    try:
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from src.competitive_pricing import CompetitivePricingEngine
        from src.forecasting_model import PriceForecastingEngine
        from src.market_copilot import MarketCopilot
        
        print("✅ Main platform modules")
        
    except ImportError as e:
        print(f"❌ Main platform modules - {e}")
        return False
    
    print("✅ Installation verification successful")
    return True

def create_config_files():
    """Create configuration files if they don't exist."""
    print("⚙️ Creating configuration files...")
    
    dashboard_dir = Path(__file__).parent
    project_root = dashboard_dir.parent
    
    # Create .env file if it doesn't exist
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
        except Exception as e:
            print(f"⚠️ Could not create .env file: {e}")
    
    print("✅ Configuration setup complete")

def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 Installation Complete!")
    print("=" * 30)
    print("\nNext steps:")
    print("1. Start the main platform API:")
    print("   python main.py --mode server")
    print("\n2. In a new terminal, start the dashboard:")
    print("   cd dashboard")
    print("   streamlit run app.py")
    print("\n3. Or use the convenient launcher:")
    print("   python dashboard/run_dashboard.py")
    print("\n4. Access the dashboard:")
    print("   Dashboard: http://localhost:8501")
    print("   API Docs:  http://localhost:8000/docs")
    print("\n5. Try the demo:")
    print("   python demo_dashboard.py")
    
    print("\n📚 Documentation:")
    print("   Dashboard: dashboard/README.md")
    print("   Main Platform: README.md")

def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install AI Retail Intelligence Dashboard")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    parser.add_argument("--force", action="store_true", help="Force reinstallation")
    args = parser.parse_args()
    
    print_header()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check main platform
    if not check_main_platform():
        print("\n❌ Main platform not found or incomplete.")
        print("Please ensure you're running this from the project root directory.")
        return 1
    
    # Install dependencies
    if not install_main_dependencies():
        return 1
    
    if not install_dashboard_dependencies(dev_mode=args.dev):
        return 1
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed.")
        print("Please check the error messages above and try again.")
        return 1
    
    # Create config files
    create_config_files()
    
    # Print next steps
    print_next_steps()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())