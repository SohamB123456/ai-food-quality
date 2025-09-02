#!/usr/bin/env python3
"""
Quick Test Tool - Easy to use image testing script
"""

import sys
import os
sys.path.append('.')

from app import processor

def quick_test(image_path):
    """Quick test of an image with clear output"""
    print(f"🔍 Testing: {os.path.basename(image_path)}")
    print("=" * 50)
    
    try:
        # Step 1: Crop the image
        print("📷 Cropping image...")
        receipt_path, bowl_path = processor.crop_image(image_path, "quick_test_output")
        
        if not receipt_path or not bowl_path:
            print("❌ Failed to crop image")
            return
        
        # Step 2: Extract text from receipt
        print("📄 Reading receipt...")
        receipt_text = processor.extract_text_from_receipt(receipt_path)
        
        # Step 3: Find ingredients
        print("🔍 Finding ingredients...")
        ingredients = processor.extract_ingredients_from_receipt(receipt_text)
        
        if ingredients:
            print(f"\n✅ Found {len(ingredients)} ingredients:")
            for i, ingredient in enumerate(ingredients, 1):
                print(f"   {i}. {ingredient}")
        else:
            print("\n❌ No ingredients found")
            return
        
        # Step 4: Analyze bowl (optional - might fail due to API)
        print("\n🍽️  Analyzing bowl contents...")
        try:
            bowl_analysis = processor.detect_ingredients_in_bowl(bowl_path, ingredients)
            if bowl_analysis.get('detected_ingredients'):
                print("✅ Bowl analysis successful!")
                match_pct = bowl_analysis.get('match_percentage', 0)
                print(f"📊 Match percentage: {match_pct:.1f}%")
            else:
                print("⚠️  Bowl analysis failed (API issue)")
        except Exception as e:
            print(f"⚠️  Bowl analysis error: {e}")
        
        print(f"\n🎉 Test completed! Check quick_test_output/ for cropped images")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function with simple menu"""
    print("🍜 Poke Bowl Receipt Analyzer")
    print("=" * 30)
    
    # List available images
    images = []
    if os.path.exists('newImages'):
        images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not images:
        print("❌ No images found in newImages/ folder")
        return
    
    print(f"\n📁 Found {len(images)} images:")
    for i, img in enumerate(images, 1):
        print(f"   {i}. {img}")
    
    print(f"\n🚀 Testing first image automatically...")
    image_path = os.path.join('newImages', images[0])
    quick_test(image_path)
    
    # Ask if user wants to test more
    if len(images) > 1:
        print(f"\n💡 Want to test another image? Run:")
        print(f"   python3 quick_test.py <image_number>")
        print(f"   Example: python3 quick_test.py 2")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific image by number
        try:
            image_num = int(sys.argv[1]) - 1
            images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if 0 <= image_num < len(images):
                image_path = os.path.join('newImages', images[image_num])
                quick_test(image_path)
            else:
                print(f"❌ Invalid image number. Choose 1-{len(images)}")
        except ValueError:
            print("❌ Please provide a number")
    else:
        main() 