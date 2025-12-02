#!/usr/bin/env python3
"""
Setup script for Daily Nutrition Analyzer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_environment():
    """Set up the development environment"""
    print("🚀 Setting up Daily Nutrition Analyzer...\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment (optional)
    create_venv = input("📦 Create virtual environment? (y/n): ").lower().strip()
    if create_venv == 'y':
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
        
        # Activate virtual environment
        if sys.platform == "win32":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        print(f"💡 To activate virtual environment, run: {activate_cmd}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
            print("💡 Edit .env file to add your OpenAI API key (optional)")
        else:
            print("⚠️  .env.example not found, skipping .env creation")
    
    # Create necessary directories
    directories = ['models', 'evaluation_logs', 'expert_validation']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Download NLTK data (if needed)
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ Downloaded NLTK data")
    except ImportError:
        print("ℹ️  NLTK not installed, skipping NLTK data download")
    
    # Test installation
    print("\n🧪 Testing installation...")
    try:
        import streamlit
        import pandas
        import numpy
        import sklearn
        print("✅ Core dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file to add your OpenAI API key (optional)")
    print("2. Run the application: streamlit run app.py")
    print("3. Open your browser to http://localhost:8501")
    
    return True

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Daily Nutrition Analyzer Setup Script")
        print("\nUsage:")
        print("  python setup.py          # Interactive setup")
        print("  python setup.py --help   # Show this help")
        return
    
    try:
        setup_environment()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")

if __name__ == "__main__":
    main()