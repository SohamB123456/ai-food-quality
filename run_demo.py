#!/usr/bin/env python3
"""
PokeWorks QA System - Complete Demo Runner
This script demonstrates all the capabilities of your advanced system
"""

import os
import sys
import subprocess
import webbrowser
import time
from datetime import datetime

def print_banner():
    """Print the demo banner"""
    print("🍣" + "=" * 58 + "🍣")
    print("🍣" + " " * 20 + "POKEWORKS QA SYSTEM" + " " * 20 + "🍣")
    print("🍣" + " " * 15 + "Advanced AI-Powered Demo" + " " * 15 + "🍣")
    print("🍣" + "=" * 58 + "🍣")
    print()

def check_system():
    """Check if the system is ready"""
    print("🔍 Checking System Status...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check if processor can be imported
    try:
        from processor import processor
        print("✅ Advanced processor loaded")
    except Exception as e:
        print(f"❌ Processor error: {e}")
        return False
    
    # Check if Flask app can be imported
    try:
        from app import app
        print("✅ Flask app loaded")
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False
    
    # Check for test images
    test_dirs = ['newImages', 'uploads', 'Testing Images']
    has_images = False
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            images = [f for f in os.listdir(test_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                print(f"✅ Found {len(images)} test images in {test_dir}")
                has_images = True
                break
    
    if not has_images:
        print("⚠️  No test images found (system will still work)")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "YOUR_OPENAI_API_KEY":
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  OpenAI API key not configured (will use fallback mode)")
    
    print()
    return True

def show_demo_options():
    """Show available demo options"""
    print("🎯 DEMO OPTIONS")
    print("=" * 50)
    print()
    print("1. 🌐 Web Application Demo")
    print("   • Full-featured web interface")
    print("   • Upload images and get real-time analysis")
    print("   • Mobile-responsive design")
    print()
    print("2. 📱 Mobile App Screens Demo")
    print("   • Splash screen")
    print("   • Split preview interface")
    print("   • Detail overlay")
    print("   • Results visualization")
    print()
    print("3. 🔧 Command Line Tools Demo")
    print("   • Advanced processor testing")
    print("   • Batch processing")
    print("   • Individual component testing")
    print()
    print("4. 🚀 Complete System Test")
    print("   • End-to-end processing")
    print("   • Image cropping and OCR")
    print("   • AI analysis (if API key available)")
    print()
    print("5. 📊 Batch Processing Demo")
    print("   • Process multiple images")
    print("   • Generate reports")
    print("   • Export results")
    print()

def run_web_demo():
    """Run the web application demo"""
    print("🌐 Starting Web Application Demo...")
    print("=" * 40)
    print()
    print("🚀 Launching Flask server...")
    print("📱 The web app will open in your browser")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the Flask app
        from app import app
        print("✅ Server starting at http://localhost:5001")
        print("⏳ Opening browser in 3 seconds...")
        
        # Open browser after a delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:5001/demo')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the app
        app.run(debug=False, host='0.0.0.0', port=5001)
        
    except KeyboardInterrupt:
        print("\n👋 Web demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting web demo: {e}")

def run_mobile_demo():
    """Run the mobile screens demo"""
    print("📱 Mobile App Screens Demo")
    print("=" * 30)
    print()
    
    screens = [
        ("Splash Screen", "http://localhost:5001/splash"),
        ("Split Preview", "http://localhost:5001/split-preview"),
        ("Detail Overlay", "http://localhost:5001/detail-overlay"),
        ("Demo Navigation", "http://localhost:5001/demo")
    ]
    
    print("🎨 Available Mobile Screens:")
    for i, (name, url) in enumerate(screens, 1):
        print(f"   {i}. {name}")
    
    print()
    choice = input("Enter screen number (1-4) or 'all' to open all: ").strip()
    
    if choice.lower() == 'all':
        print("🚀 Opening all mobile screens...")
        for name, url in screens:
            print(f"   📱 Opening {name}...")
            webbrowser.open(url)
            time.sleep(1)
    elif choice.isdigit() and 1 <= int(choice) <= len(screens):
        idx = int(choice) - 1
        name, url = screens[idx]
        print(f"🚀 Opening {name}...")
        webbrowser.open(url)
    else:
        print("❌ Invalid choice")

def run_cli_demo():
    """Run command line tools demo"""
    print("🔧 Command Line Tools Demo")
    print("=" * 30)
    print()
    
    tools = [
        ("Advanced System Test", "python test_advanced_system.py"),
        ("Fuzzy Matching Demo", "python fuzzy_matching.py"),
        ("Auto Crop Detection", "python auto_crop_detection.py"),
        ("Comprehensive Demo", "python demo.py"),
        ("Quick Test", "python quick_test.py")
    ]
    
    print("🛠️  Available CLI Tools:")
    for i, (name, command) in enumerate(tools, 1):
        print(f"   {i}. {name}")
    
    print()
    choice = input("Enter tool number (1-5): ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(tools):
        idx = int(choice) - 1
        name, command = tools[idx]
        print(f"🚀 Running {name}...")
        print(f"📝 Command: {command}")
        print()
        
        try:
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {name}: {e}")
        except KeyboardInterrupt:
            print(f"\n⏹️  {name} stopped by user")
    else:
        print("❌ Invalid choice")

def run_system_test():
    """Run complete system test"""
    print("🚀 Complete System Test")
    print("=" * 25)
    print()
    
    try:
        subprocess.run(["python", "test_advanced_system.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ System test failed: {e}")
    except KeyboardInterrupt:
        print("\n⏹️  System test stopped by user")

def run_batch_demo():
    """Run batch processing demo"""
    print("📊 Batch Processing Demo")
    print("=" * 25)
    print()
    
    # Check for input directory
    input_dirs = ['newImages', 'uploads', 'Testing Images']
    input_dir = None
    
    for dir_name in input_dirs:
        if os.path.exists(dir_name):
            images = [f for f in os.listdir(dir_name) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                input_dir = dir_name
                print(f"📁 Found {len(images)} images in {dir_name}")
                break
    
    if not input_dir:
        print("❌ No images found for batch processing")
        print("💡 Add images to newImages, uploads, or Testing Images directory")
        return
    
    print(f"🔄 Processing images from {input_dir}...")
    
    try:
        from processor import processor
        results = processor.batch_process(input_dir, "batch_demo_output")
        
        print(f"✅ Batch processing complete!")
        print(f"📊 Processed {len(results)} images")
        print(f"💾 Results saved to batch_demo_output/")
        
    except Exception as e:
        print(f"❌ Batch processing error: {e}")

def main():
    """Main demo runner"""
    print_banner()
    
    if not check_system():
        print("❌ System check failed. Please fix the issues above.")
        return
    
    while True:
        show_demo_options()
        print("0. 🚪 Exit")
        print()
        
        choice = input("Select demo option (0-5): ").strip()
        print()
        
        if choice == '0':
            print("👋 Thanks for trying the PokeWorks QA System!")
            break
        elif choice == '1':
            run_web_demo()
        elif choice == '2':
            run_mobile_demo()
        elif choice == '3':
            run_cli_demo()
        elif choice == '4':
            run_system_test()
        elif choice == '5':
            run_batch_demo()
        else:
            print("❌ Invalid choice. Please select 0-5.")
        
        print()
        input("Press Enter to continue...")
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your system configuration and try again.")

