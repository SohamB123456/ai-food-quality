#!/usr/bin/env python3
"""
Improved OCR Test - Using the adaptive threshold method that works better
"""

import cv2
import pytesseract
import os
from rapidfuzz import fuzz, process

def improved_ocr_core(img):
    """Improved OCR function with preprocessing (same as app.py)"""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply denoising
    denoised = cv2.medianBlur(gray, 5)
    
    # Apply adaptive threshold (the method that works best)
    adaptive_thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Use OCR on the preprocessed image
    text = pytesseract.image_to_string(adaptive_thresh)
    return text.strip()

def test_improved_ocr(image_path):
    """Test improved OCR on a receipt image"""
    print(f"🔍 Testing IMPROVED OCR on: {os.path.basename(image_path)}")
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
    
    # Compare basic vs improved OCR
    print("\n📄 OCR Comparison:")
    print("-" * 40)
    
    # Basic OCR (like ocr_fuzzy_simple.py)
    basic_text = pytesseract.image_to_string(img)
    print(f"1️⃣ Basic OCR (ocr_fuzzy_simple.py method):")
    print(f"   {basic_text[:100]}...")
    print(f"   Length: {len(basic_text)} characters")
    
    # Improved OCR (like app.py)
    improved_text = improved_ocr_core(img)
    print(f"\n2️⃣ Improved OCR (app.py method):")
    print(f"   {improved_text[:100]}...")
    print(f"   Length: {len(improved_text)} characters")
    
    print("-" * 40)
    
    # Use the better result
    if len(improved_text) > len(basic_text):
        text = improved_text
        method = "Improved"
    else:
        text = basic_text
        method = "Basic"
    
    print(f"\n✅ Using {method} OCR result")
    
    # Fuzzy matching
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
    print(f"   OCR Method: {method}")
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
    print("🔍 Improved OCR Test Tool")
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
    text, matches = test_improved_ocr(image_path)
    
    # Ask if user wants to test more
    if len(images) > 1:
        print(f"\n💡 Want to test another image? Run:")
        print(f"   python3 improved_ocr_test.py <image_number>")
        print(f"   Example: python3 improved_ocr_test.py 2")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Test specific image by number
        try:
            image_num = int(sys.argv[1]) - 1
            images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if 0 <= image_num < len(images):
                image_path = os.path.join('newImages', images[image_num])
                test_improved_ocr(image_path)
            else:
                print(f"❌ Invalid image number. Choose 1-{len(images)}")
        except ValueError:
            print("❌ Please provide a number")
    else:
        main() 