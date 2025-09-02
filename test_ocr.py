#!/usr/bin/env python3
"""
Test script to debug OCR issues
"""

import cv2
import pytesseract
import os

def test_ocr_methods(image_path):
    """Test different OCR preprocessing methods"""
    print(f"Testing OCR on: {image_path}")
    print("=" * 50)
    
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Could not read image")
        return
    
    print(f"Image shape: {img.shape}")
    
    # Method 1: Original image
    print("\n1️⃣ Original Image:")
    text = pytesseract.image_to_string(img)
    print(f"Text: {repr(text)}")
    
    # Method 2: Grayscale
    print("\n2️⃣ Grayscale:")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    print(f"Text: {repr(text)}")
    
    # Method 3: Denoised
    print("\n3️⃣ Denoised:")
    denoised = cv2.medianBlur(gray, 5)
    text = pytesseract.image_to_string(denoised)
    print(f"Text: {repr(text)}")
    
    # Method 4: Thresholded
    print("\n4️⃣ Thresholded:")
    thresholded = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(thresholded)
    print(f"Text: {repr(text)}")
    
    # Method 5: Adaptive threshold
    print("\n5️⃣ Adaptive Threshold:")
    adaptive_thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    text = pytesseract.image_to_string(adaptive_thresh)
    print(f"Text: {repr(text)}")
    
    # Method 6: Different PSM modes
    print("\n6️⃣ PSM Mode 6 (Uniform Block):")
    text = pytesseract.image_to_string(thresholded, config='--psm 6')
    print(f"Text: {repr(text)}")
    
    print("\n7️⃣ PSM Mode 8 (Single Word):")
    text = pytesseract.image_to_string(thresholded, config='--psm 8')
    print(f"Text: {repr(text)}")
    
    print("\n8️⃣ PSM Mode 13 (Raw Line):")
    text = pytesseract.image_to_string(thresholded, config='--psm 13')
    print(f"Text: {repr(text)}")

if __name__ == "__main__":
    # Test with the receipt image from the demo
    receipt_path = "demo_output/PHOTO-2025-07-21-11-44-46 2_receipt.jpg"
    
    if os.path.exists(receipt_path):
        test_ocr_methods(receipt_path)
    else:
        print(f"Receipt image not found: {receipt_path}")
        print("Available images:")
        for file in os.listdir("demo_output"):
            if "receipt" in file:
                print(f"  - demo_output/{file}") 