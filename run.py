#!/usr/bin/env python3
"""
Startup script for Food Bowl Receipt Analyzer MVP
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'openai', 'cv2', 'PIL', 'pytesseract', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if package == 'cv2':
            spec = importlib.util.find_spec('cv2')
        elif package == 'PIL':
            spec = importlib.util.find_spec('PIL')
        else:
            spec = importlib.util.find_spec(package)
        
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ Tesseract: {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Tesseract OCR not found")
    print("Please install Tesseract:")
    print("  macOS: brew install tesseract")
    print("  Ubuntu: sudo apt-get install tesseract-ocr")
    print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    return False

def check_openai_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != "YOUR_OPENAI_API_KEY":
        print("✅ OpenAI API key is set")
        return True
    else:
        print("⚠️  OpenAI API key not set")
        print("Set it with: export OPENAI_API_KEY='your_key_here'")
        print("GPT-4 analysis will be disabled without the key")
        return True  # Don't block startup, just warn

def check_required_files():
    """Check if required files exist"""
    required_files = ['Ingredients.txt', 'app.py']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 Food Bowl Receipt Analyzer MVP - Startup Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Tesseract OCR", check_tesseract),
        ("OpenAI API Key", check_openai_key),
        ("Required Files", check_required_files)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! Starting the application...")
        print("\n📱 Open your browser and go to: http://localhost:8081")
        print("🛑 Press Ctrl+C to stop the server")
        print("\n" + "=" * 50)
        
        # Start the Flask app
        try:
            from app import app
            app.run(debug=True, host='0.0.0.0', port=8081)
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
        except Exception as e:
            print(f"\n❌ Error starting server: {e}")
    else:
        print("❌ Some checks failed. Please fix the issues above before starting.")
        sys.exit(1)

if __name__ == "__main__":
    main() 