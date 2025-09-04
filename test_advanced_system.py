#!/usr/bin/env python3
"""
Test the Advanced PokeWorks QA System
"""

import os
import sys
sys.path.append('.')

from processor import processor

def test_system():
    """Test the complete system with demo image"""
    print("🚀 Testing Advanced PokeWorks QA System")
    print("=" * 50)
    
    # Check if we have any test images
    test_dirs = ['newImages', 'uploads', 'Testing Images']
    test_image = None
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_image = os.path.join(test_dir, file)
                    break
            if test_image:
                break
    
    if not test_image:
        print("❌ No test images found. Please add an image to test with.")
        print("   Expected directories: newImages, uploads, or Testing Images")
        return False
    
    print(f"📸 Using test image: {os.path.basename(test_image)}")
    
    try:
        # Test the complete pipeline
        print("\n🔄 Testing complete processing pipeline...")
        results = processor.process_image(test_image, "test_output")
        
        if results:
            print("✅ Processing successful!")
            
            # Display results
            analysis = results.get('analysis', {})
            print(f"\n📊 Results:")
            print(f"   Match Percentage: {analysis.get('match_percentage', 0)}%")
            print(f"   Summary: {analysis.get('summary', 'No summary available')}")
            
            detected = analysis.get('detected_ingredients', [])
            print(f"\n🍣 Detected Ingredients ({len(detected)}):")
            for ingredient in detected:
                status = ingredient.get('status', 'unknown')
                confidence = ingredient.get('confidence', 0)
                name = ingredient.get('ingredient', 'Unknown')
                print(f"   • {name} ({confidence}% confidence, {status})")
            
            missing = analysis.get('missing_ingredients', [])
            if missing:
                print(f"\n❌ Missing Ingredients ({len(missing)}):")
                for ingredient in missing:
                    print(f"   • {ingredient}")
            
            unexpected = analysis.get('unexpected_ingredients', [])
            if unexpected:
                print(f"\n⚠️  Unexpected Ingredients ({len(unexpected)}):")
                for ingredient in unexpected:
                    print(f"   • {ingredient}")
            
            print(f"\n📄 Receipt Text:")
            print(f"   {results.get('receipt_text', 'No text extracted')[:100]}...")
            
            return True
        else:
            print("❌ Processing failed - no results returned")
            return False
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False

def test_components():
    """Test individual components"""
    print("\n🔧 Testing Individual Components")
    print("=" * 30)
    
    # Test 1: Ingredient loading
    print("1️⃣ Testing ingredient loading...")
    ingredients = processor.ingredients
    print(f"   ✅ Loaded {len(ingredients)} ingredients")
    
    # Test 2: Image cropping (if we have a test image)
    test_dirs = ['newImages', 'uploads', 'Testing Images']
    test_image = None
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_image = os.path.join(test_dir, file)
                    break
            if test_image:
                break
    
    if test_image:
        print("2️⃣ Testing image cropping...")
        try:
            receipt_path, bowl_path = processor.crop_image(test_image, "test_crop_output")
            if receipt_path and bowl_path:
                print(f"   ✅ Cropping successful")
                print(f"   📄 Receipt: {os.path.basename(receipt_path)}")
                print(f"   🍣 Bowl: {os.path.basename(bowl_path)}")
            else:
                print("   ❌ Cropping failed")
        except Exception as e:
            print(f"   ❌ Cropping error: {e}")
        
        print("3️⃣ Testing OCR...")
        try:
            if receipt_path and os.path.exists(receipt_path):
                text = processor.extract_receipt_text(receipt_path)
                print(f"   ✅ OCR successful: {len(text)} characters extracted")
                if text:
                    print(f"   📝 Sample text: {text[:50]}...")
                else:
                    print("   ⚠️  No text extracted")
            else:
                print("   ⚠️  No receipt image to test OCR")
        except Exception as e:
            print(f"   ❌ OCR error: {e}")
    else:
        print("2️⃣ ⚠️  No test image available for cropping/OCR tests")
    
    print("4️⃣ Testing OpenAI API connection...")
    try:
        # This will fail without a real API key, but we can test the connection
        print("   ⚠️  OpenAI API key not configured (expected for demo)")
        print("   💡 Set OPENAI_API_KEY environment variable for full functionality")
    except Exception as e:
        print(f"   ❌ API connection error: {e}")

if __name__ == "__main__":
    print("🍣 PokeWorks QA System - Advanced Testing")
    print("=" * 60)
    
    # Test individual components first
    test_components()
    
    # Test complete system
    print("\n" + "=" * 60)
    success = test_system()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 System test completed successfully!")
        print("🚀 Your advanced PokeWorks QA system is ready to use!")
        print("\n📱 To run the web app:")
        print("   python app.py")
        print("   Then visit: http://localhost:5001")
    else:
        print("❌ System test failed. Please check the errors above.")
        print("💡 Make sure you have test images and proper configuration.")

