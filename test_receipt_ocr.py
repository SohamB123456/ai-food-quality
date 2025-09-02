#!/usr/bin/env python3
"""
Test Receipt OCR - Simple OCR test using the same logic as ocr_fuzzy_simple.py
"""

import cv2
import pytesseract
import os
from rapidfuzz import fuzz, process

def ocr_core(img):
    """Simple OCR function from ocr_fuzzy_simple.py"""
    text = pytesseract.image_to_string(img)
    return text

def test_receipt_ocr(image_path):
    """Test OCR on a receipt image"""
    print(f"🔍 Testing OCR on: {os.path.basename(image_path)}")
    print("=" * 60)
    
    # Read ingredients
    ingredients_file = 'Ingredients.txt'
    with open(ingredients_file, 'r') as f:
        ingredients = [line.strip() for line in f if line.strip()]
    
    print(f"📋 Loaded {len(ingredients)} ingredients for matching")
    
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Could not read {image_path}")
        return
    
    print(f"📏 Image size: {img.shape[1]}x{img.shape[0]}")
    
    # Perform OCR on original image only (same as ocr_fuzzy_simple.py)
    print("\n📄 OCR Result:")
    print("-" * 40)
    text = ocr_core(img)
    print(text)
    print("-" * 40)
    
    # Fuzzy matching (same logic as ocr_fuzzy_simple.py)
    print(f"\n🔍 Fuzzy Matching Results:")
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    matches = []
    
    for line in lines:
        if len(line) > 2:  # Only process lines with meaningful content
            match, score, _ = process.extractOne(line, ingredients, scorer=fuzz.ratio)
            matches.append((line, match, score))
            print(f"'{line}' -> '{match}' (score: {score})")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"   Total lines in OCR: {len(lines)}")
    print(f"   Lines processed: {len(matches)}")
    
    # Show matched ingredients
    if matches:
        print(f"\n✅ Matched Ingredients:")
        for i, (orig, ing, score) in enumerate(matches, 1):
            print(f"   {i}. {ing} (from '{orig}')")
    else:
        print(f"\n❌ No ingredients matched")
    
    return text, matches

def main():
    """Main function"""
    print("🔍 Receipt OCR Test Tool")
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
    text, matches = test_receipt_ocr(image_path)
    
    # Ask if user wants to test more
    if len(images) > 1:
        print(f"\n💡 Want to test another image? Run:")
        print(f"   python3 test_receipt_ocr.py <image_number>")
        print(f"   Example: python3 test_receipt_ocr.py 2")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Test specific image by number
        try:
            image_num = int(sys.argv[1]) - 1
            images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if 0 <= image_num < len(images):
                image_path = os.path.join('newImages', images[image_num])
                test_receipt_ocr(image_path)
            else:
                print(f"❌ Invalid image number. Choose 1-{len(images)}")
        except ValueError:
            print("❌ Please provide a number")
    else:
        main() 