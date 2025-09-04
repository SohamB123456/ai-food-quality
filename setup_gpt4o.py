#!/usr/bin/env python3
"""
Setup script for GPT-4o API configuration
"""

import os
import sys

def setup_api_key():
    """Interactive setup for OpenAI API key"""
    print("🔑 GPT-4o API Setup")
    print("=" * 30)
    
    # Check if API key is already set
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key and current_key != 'your-api-key-here':
        print(f"✅ API key is already set: {current_key[:10]}...")
        return True
    
    print("📋 To get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/account/api-keys")
    print("2. Sign in or create an account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (starts with 'sk-')")
    print()
    
    # Get API key from user
    api_key = input("🔑 Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
        confirm = input("Continue anyway? (y/n): ").lower()
        if confirm != 'y':
            return False
    
    # Update config.py
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder
        updated_content = content.replace(
            "OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')",
            f"OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '{api_key}')"
        )
        
        with open('config.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ API key saved to config.py")
        
        # Set environment variable for current session
        os.environ['OPENAI_API_KEY'] = api_key
        print("✅ API key set for current session")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False

def test_api_connection():
    """Test the API connection"""
    print("\n🧪 Testing API connection...")
    
    try:
        from processor import processor
        
        # Test with a simple image
        test_image = 'Bowls/PHOTO-2025-07-21-11-44-42.jpg'
        if os.path.exists(test_image):
            print(f"📸 Testing with: {test_image}")
            result = processor.process_image(test_image, "test_gpt4o_output")
            
            if result and result.get('analysis', {}).get('match_percentage', 0) > 0:
                print("✅ GPT-4o API is working!")
                print(f"📊 Match percentage: {result['analysis']['match_percentage']}%")
                return True
            else:
                print("⚠️  API connected but no results returned")
                return False
        else:
            print("⚠️  Test image not found")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PokeWorks QA - GPT-4o Setup")
    print("=" * 40)
    
    # Setup API key
    if not setup_api_key():
        print("❌ Setup failed")
        return
    
    # Test connection
    if test_api_connection():
        print("\n🎉 Setup complete! GPT-4o is ready to use.")
        print("💡 You can now run the web app and get much better results!")
    else:
        print("\n⚠️  Setup completed but API test failed.")
        print("💡 Check your API key and try again.")

if __name__ == "__main__":
    main()

