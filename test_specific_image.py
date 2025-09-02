#!/usr/bin/env python3
"""
Test script to process a specific image with improved OCR and fuzzy matching
"""

import sys
import os
sys.path.append('.')

from app import processor

def test_specific_image(image_path):
    """Test the full pipeline on a specific image"""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"🧪 Testing Image: {image_path}")
    print("=" * 60)
    
    # Create output directory
    output_dir = "test_specific_output"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Step 1: Auto-crop
        print("\n1️⃣ Auto-cropping image...")
        receipt_path, bowl_path = processor.crop_image(image_path, output_dir)
        
        if receipt_path and bowl_path:
            print(f"✅ Receipt saved: {receipt_path}")
            print(f"✅ Bowl saved: {bowl_path}")
        else:
            print("❌ Cropping failed")
            return
        
        # Step 2: OCR extraction
        print("\n2️⃣ Extracting text from receipt...")
        receipt_text = processor.extract_text_from_receipt(receipt_path)
        print(f"📄 Extracted text: {receipt_text}")
        
        # Step 3: Ingredient extraction
        print("\n3️⃣ Extracting ingredients from receipt...")
        receipt_ingredients = processor.extract_ingredients_from_receipt(receipt_text)
        print(f"🔍 Found ingredients: {receipt_ingredients}")
        
        if receipt_ingredients:
            print("\n✅ Ingredients found in receipt:")
            for ingredient in receipt_ingredients:
                print(f"   - {ingredient}")
        else:
            print("\n❌ No ingredients found in receipt")
        
        # Step 4: Bowl analysis
        print("\n4️⃣ Analyzing bowl contents...")
        detected_ingredients = processor.detect_ingredients_in_bowl(bowl_path, receipt_ingredients)
        
        if detected_ingredients.get('detected_ingredients'):
            print("✅ Bowl analysis completed:")
            for ingredient in detected_ingredients['detected_ingredients'][:5]:
                source = "Receipt" if ingredient.get('from_receipt') else "Additional"
                print(f"   - {ingredient['ingredient']} ({ingredient['confidence']:.1f}%) - {source}")
            
            if detected_ingredients.get('match_percentage'):
                print(f"   📊 Match Percentage: {detected_ingredients['match_percentage']:.1f}%")
        else:
            print("❌ Bowl analysis failed")
        
        # Step 5: Final analysis
        print("\n5️⃣ Final analysis...")
        gpt_analysis = processor.analyze_with_gpt4(image_path, receipt_text, detected_ingredients)
        
        if 'error' in gpt_analysis:
            print(f"⚠️  GPT-4 analysis: {gpt_analysis['error']}")
        else:
            print("✅ GPT-4 analysis completed")
            print(f"📝 Analysis: {gpt_analysis['analysis'][:200]}...")
        
        print(f"\n🎉 Test completed! Check {output_dir}/ for processed images")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def main():
    """Main function"""
    # List available images
    print("Available test images:")
    for i, file in enumerate(os.listdir('newImages'), 1):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"  {i}. newImages/{file}")
    
    print("\nTesting with the first available image...")
    
    # Test with the second image (might have better OCR)
    images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if len(images) > 1:
        image_path = os.path.join('newImages', images[1])  # Try second image
        test_specific_image(image_path)
    else:
        image_path = os.path.join('newImages', images[0])
        test_specific_image(image_path)

if __name__ == "__main__":
    main() 