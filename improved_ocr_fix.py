#!/usr/bin/env python3
"""
Improved OCR script specifically for the user's image layout
"""

import cv2
import pytesseract
import numpy as np
import os

def extract_receipt_text_improved(image_path):
    """Improved receipt text extraction for the user's specific image"""
    
    print(f"🔍 Processing: {image_path}")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Failed to load image")
        return ""
    
    h, w = image.shape[:2]
    print(f"📏 Image size: {w}x{h}")
    
    # The receipt is on the left side of the image
    # Let's be more precise about the receipt location
    left_portion = image[:, :w//2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(left_portion, cv2.COLOR_BGR2GRAY)
    
    # Apply multiple preprocessing techniques
    results = []
    
    # Method 1: Simple threshold
    _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text1 = pytesseract.image_to_string(thresh1, config='--psm 6')
    results.append(("Simple threshold", text1))
    
    # Method 2: Adaptive threshold
    thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    text2 = pytesseract.image_to_string(thresh2, config='--psm 6')
    results.append(("Adaptive threshold", text2))
    
    # Method 3: Denoise + adaptive threshold
    denoised = cv2.fastNlMeansDenoising(gray)
    thresh3 = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    text3 = pytesseract.image_to_string(thresh3, config='--psm 6')
    results.append(("Denoised + adaptive", text3))
    
    # Method 4: Try to isolate just the white receipt paper
    # Create a mask for white regions
    lower_white = np.array([200, 200, 200])
    upper_white = np.array([255, 255, 255])
    
    # Apply mask to original left portion (which is already BGR)
    white_mask = cv2.inRange(left_portion, lower_white, upper_white)
    
    # Apply mask to original
    masked = cv2.bitwise_and(left_portion, left_portion, mask=white_mask)
    masked_gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to masked image
    _, thresh4 = cv2.threshold(masked_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text4 = pytesseract.image_to_string(thresh4, config='--psm 6')
    results.append(("White paper mask", text4))
    
    # Save debug images
    cv2.imwrite("debug_thresh1.jpg", thresh1)
    cv2.imwrite("debug_thresh2.jpg", thresh2)
    cv2.imwrite("debug_thresh3.jpg", thresh3)
    cv2.imwrite("debug_thresh4.jpg", thresh4)
    cv2.imwrite("debug_masked.jpg", masked)
    
    # Print all results
    print("\n📄 OCR Results:")
    for i, (method, text) in enumerate(results, 1):
        print(f"\n{i}. {method}:")
        print(f"Text: {repr(text[:300])}")
        
        # Look for key words that indicate success
        key_words = ["White Rice", "Ahi Tuna", "Salmon", "Cucumber", "Cabbage", "Edamame", "Mango", "Seaweed", "Sesame"]
        found_words = [word for word in key_words if word.lower() in text.lower()]
        if found_words:
            print(f"✅ Found key words: {found_words}")
        else:
            print("❌ No key words found")
    
    # Return the best result (one with most key words)
    best_result = max(results, key=lambda x: len([word for word in key_words if word.lower() in x[1].lower()]))
    print(f"\n🏆 Best result: {best_result[0]}")
    
    return best_result[1]

def extract_ingredients_from_text(text):
    """Extract ingredients from OCR text"""
    
    print(f"\n🍜 Extracting ingredients from text:")
    print(f"Raw text: {repr(text)}")
    
    # Split into lines and clean
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Look for ingredients in the text
    expected_ingredients = [
        "White Rice", "Ahi Tuna", "Salmon", "Cucumber", 
        "Cabbage", "Edamame", "Mango", "Seaweed Salad", 
        "Sesame Seeds", "Pokeworks Classic", "Medium Flavor"
    ]
    
    found_ingredients = []
    
    for line in lines:
        line_lower = line.lower()
        for ingredient in expected_ingredients:
            if ingredient.lower() in line_lower:
                found_ingredients.append(ingredient)
                print(f"✅ Found: {ingredient} in line: {line}")
    
    # Remove duplicates while preserving order
    unique_ingredients = []
    for ingredient in found_ingredients:
        if ingredient not in unique_ingredients:
            unique_ingredients.append(ingredient)
    
    print(f"\n📋 Extracted ingredients: {unique_ingredients}")
    return unique_ingredients

def main():
    """Main function to test improved OCR"""
    
    image_path = "PHOTO-2025-07-21-11-44-48.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print("🚀 Improved OCR Test")
    print("=" * 50)
    
    # Extract text
    text = extract_receipt_text_improved(image_path)
    
    # Extract ingredients
    ingredients = extract_ingredients_from_text(text)
    
    print(f"\n🎯 Final Results:")
    print(f"Found {len(ingredients)} ingredients: {ingredients}")
    
    # Compare with expected
    expected = ["White Rice", "Ahi Tuna", "Salmon", "Cucumber", "Cabbage", "Edamame", "Mango", "Seaweed Salad", "Sesame Seeds"]
    missing = [ing for ing in expected if ing not in ingredients]
    
    if missing:
        print(f"❌ Missing: {missing}")
    else:
        print("✅ All expected ingredients found!")

if __name__ == "__main__":
    main() 