#!/usr/bin/env python3
"""
Test App Pipeline - Test the full app pipeline with improved OCR
"""

import sys
import os
sys.path.append('.')

from app import processor

def test_app_pipeline(image_path):
    """Test the full app pipeline on a specific image"""
    print(f"🔍 Testing App Pipeline on: {os.path.basename(image_path)}")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    try:
        # Step 1: Auto-crop
        print("\n1️⃣ Auto-cropping image...")
        receipt_path, bowl_path = processor.crop_image(image_path, "app_test_output")
        
        if receipt_path and bowl_path:
            print(f"✅ Receipt saved: {os.path.basename(receipt_path)}")
            print(f"✅ Bowl saved: {os.path.basename(bowl_path)}")
        else:
            print("❌ Cropping failed")
            return
        
        # Step 2: OCR extraction (using improved method)
        print("\n2️⃣ Extracting text from receipt (improved OCR)...")
        receipt_text = processor.extract_text_from_receipt(receipt_path)
        print(f"📄 Extracted text length: {len(receipt_text)} characters")
        if receipt_text:
            print(f"📄 First 200 chars: {receipt_text[:200]}...")
        else:
            print("❌ No text extracted")
            return
        
        # Step 3: Ingredient extraction
        print("\n3️⃣ Extracting ingredients from receipt...")
        receipt_ingredients = processor.extract_ingredients_from_receipt(receipt_text)
        print(f"🔍 Found {len(receipt_ingredients)} ingredients:")
        
        if receipt_ingredients:
            for i, ingredient in enumerate(receipt_ingredients, 1):
                print(f"   {i}. {ingredient}")
        else:
            print("❌ No ingredients found")
            return
        
        # Step 4: Bowl analysis (optional - might fail due to API)
        print("\n4️⃣ Analyzing bowl contents...")
        try:
            detected_ingredients = processor.detect_ingredients_in_bowl(bowl_path, receipt_ingredients)
            
            if detected_ingredients.get('detected_ingredients'):
                print("✅ Bowl analysis completed:")
                for ingredient in detected_ingredients['detected_ingredients'][:5]:
                    source = "Receipt" if ingredient.get('from_receipt') else "Additional"
                    print(f"   - {ingredient['ingredient']} ({ingredient['confidence']:.1f}%) - {source}")
                
                if detected_ingredients.get('match_percentage'):
                    print(f"   📊 Match Percentage: {detected_ingredients['match_percentage']:.1f}%")
            else:
                print("⚠️ Bowl analysis failed (API issue)")
        except Exception as e:
            print(f"⚠️ Bowl analysis error: {e}")
        
        # Step 5: Final analysis
        print("\n5️⃣ Final analysis...")
        try:
            gpt_analysis = processor.analyze_with_gpt4(image_path, receipt_text, detected_ingredients)
            
            if 'error' in gpt_analysis:
                print(f"⚠️ GPT-4 analysis: {gpt_analysis['error']}")
            else:
                print("✅ GPT-4 analysis completed")
                print(f"📝 Analysis: {gpt_analysis['analysis'][:200]}...")
        except Exception as e:
            print(f"⚠️ GPT-4 analysis error: {e}")
        
        print(f"\n🎉 App pipeline test completed! Check app_test_output/ for processed images")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def main():
    """Main function"""
    print("🔍 App Pipeline Test Tool")
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
    
    # Test first image
    print(f"\n🚀 Testing first image...")
    image_path = os.path.join('newImages', images[0])
    test_app_pipeline(image_path)
    
    # Ask if user wants to test more
    if len(images) > 1:
        print(f"\n💡 Want to test another image? Run:")
        print(f"   python3 test_app_pipeline.py <image_number>")
        print(f"   Example: python3 test_app_pipeline.py 2")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific image by number
        try:
            image_num = int(sys.argv[1]) - 1
            images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if 0 <= image_num < len(images):
                image_path = os.path.join('newImages', images[image_num])
                test_app_pipeline(image_path)
            else:
                print(f"❌ Invalid image number. Choose 1-{len(images)}")
        except ValueError:
            print("❌ Please provide a number")
    else:
        main() 