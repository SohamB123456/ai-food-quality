#!/usr/bin/env python3
"""
Debug script for user's specific image to identify OCR and ingredient detection issues
"""

import os
import cv2
import pytesseract
from PIL import Image
import json

def test_ocr_on_user_image():
    """Test OCR on the user's image to see what's going wrong"""
    
    # Check if we have the user's image
    user_image_path = "PHOTO-2025-07-21-11-44-48.jpg"
    
    if not os.path.exists(user_image_path):
        print(f"❌ User image not found: {user_image_path}")
        print("Please place your image in the project directory")
        return
    
    print("🔍 Testing OCR on your image...")
    print(f"📁 Image: {user_image_path}")
    
    # Load image
    image = cv2.imread(user_image_path)
    if image is None:
        print("❌ Failed to load image")
        return
    
    print(f"📏 Image size: {image.shape}")
    
    # Try different OCR approaches
    print("\n📄 Testing different OCR methods:")
    
    # Method 1: Basic OCR
    print("\n1️⃣ Basic OCR (no preprocessing):")
    basic_text = pytesseract.image_to_string(image)
    print(f"Raw text: {repr(basic_text[:200])}")
    
    # Method 2: Grayscale + threshold
    print("\n2️⃣ Grayscale + Adaptive Threshold:")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
    thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Save preprocessed image for inspection
    cv2.imwrite("debug_preprocessed.jpg", thresh)
    print("💾 Saved preprocessed image as 'debug_preprocessed.jpg'")
    
    thresh_text = pytesseract.image_to_string(thresh)
    print(f"Threshold text: {repr(thresh_text[:200])}")
    
    # Method 3: Different PSM modes
    print("\n3️⃣ Different PSM modes:")
    for psm in [6, 7, 8, 9, 10, 11, 12, 13]:
        try:
            psm_text = pytesseract.image_to_string(thresh, config=f'--psm {psm}')
            print(f"PSM {psm}: {repr(psm_text[:100])}")
        except:
            print(f"PSM {psm}: Error")
    
    # Method 4: Try to extract just the receipt area
    print("\n4️⃣ Attempting to crop receipt area:")
    
    # Try to find the receipt (white paper) in the image
    h, w = image.shape[:2]
    
    # Look for the left side where receipt likely is
    left_half = image[:, :w//2]
    cv2.imwrite("debug_left_half.jpg", left_half)
    
    # Convert to grayscale and find white regions
    left_gray = cv2.cvtColor(left_half, cv2.COLOR_BGR2GRAY)
    _, white_mask = cv2.threshold(left_gray, 200, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest white region (likely the receipt)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w_rect, h_rect = cv2.boundingRect(largest_contour)
        
        # Extract receipt region
        receipt_region = left_half[y:y+h_rect, x:x+w_rect]
        cv2.imwrite("debug_receipt_region.jpg", receipt_region)
        
        # OCR on receipt region
        receipt_gray = cv2.cvtColor(receipt_region, cv2.COLOR_BGR2GRAY)
        receipt_denoised = cv2.fastNlMeansDenoising(receipt_gray)
        receipt_thresh = cv2.adaptiveThreshold(receipt_denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        receipt_text = pytesseract.image_to_string(receipt_thresh)
        print(f"Receipt region text: {repr(receipt_text)}")
        
        # Save the thresholded receipt
        cv2.imwrite("debug_receipt_thresh.jpg", receipt_thresh)
        print("💾 Saved receipt threshold image as 'debug_receipt_thresh.jpg'")
    
    print("\n🔍 Analysis complete!")
    print("📁 Check the debug images to see what the OCR is processing")

def test_ingredient_matching():
    """Test the ingredient matching logic"""
    
    print("\n🍜 Testing ingredient matching logic:")
    
    # Load ingredients list
    if os.path.exists("Ingredients.txt"):
        with open("Ingredients.txt", "r") as f:
            ingredients = [line.strip() for line in f.readlines()]
        print(f"📋 Loaded {len(ingredients)} ingredients from Ingredients.txt")
        
        # Test some expected ingredients
        expected_ingredients = [
            "White Rice", "Ahi Tuna", "Salmon", "Cucumber", 
            "Cabbage", "Edamame", "Mango", "Seaweed Salad", 
            "Sesame Seeds", "Pokeworks Classic"
        ]
        
        print("\n🎯 Testing expected ingredients:")
        for ingredient in expected_ingredients:
            if ingredient in ingredients:
                print(f"✅ {ingredient} - Found in list")
            else:
                print(f"❌ {ingredient} - NOT in list")
    else:
        print("❌ Ingredients.txt not found")

if __name__ == "__main__":
    print("🐛 PokeWorks QA Debug Script")
    print("=" * 50)
    
    test_ocr_on_user_image()
    test_ingredient_matching()
    
    print("\n🎯 Next steps:")
    print("1. Check the debug images to see what OCR is processing")
    print("2. Verify Ingredients.txt contains the expected ingredients")
    print("3. Run the app again with improved preprocessing") 