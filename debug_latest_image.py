#!/usr/bin/env python3
"""
Debug the latest uploaded image to understand why results are limited
"""

import os
import sys
sys.path.append('.')

from processor import processor
import cv2
import pytesseract
from PIL import Image

def debug_latest_image():
    """Debug the latest image to understand the limitations"""
    print("🔍 DEBUGGING LATEST COMPLEX BOWL IMAGE")
    print("=" * 60)
    
    latest_image = 'uploads/20250902_114557_aef7fd83_PHOTO-2025-07-21-11-44-42 3.jpg'
    
    if not os.path.exists(latest_image):
        print("❌ Latest image not found")
        return
    
    print(f"📸 Analyzing: {os.path.basename(latest_image)}")
    
    # Step 1: Crop the image
    print("\n1️⃣ CROPPING IMAGE...")
    receipt_path, bowl_path = processor.crop_image(latest_image, "debug_output")
    print(f"   Receipt: {os.path.basename(receipt_path) if receipt_path else 'Failed'}")
    print(f"   Bowl: {os.path.basename(bowl_path) if bowl_path else 'Failed'}")
    
    # Step 2: OCR Analysis
    print("\n2️⃣ OCR ANALYSIS...")
    if receipt_path and os.path.exists(receipt_path):
        receipt_text = processor.extract_receipt_text(receipt_path)
        print(f"   Extracted {len(receipt_text)} characters")
        print(f"   Sample: {receipt_text[:100]}...")
        
        # Try different OCR methods
        print("\n   🔬 TRYING DIFFERENT OCR METHODS:")
        
        # Method 1: Original image
        img = cv2.imread(receipt_path)
        text1 = pytesseract.image_to_string(img)
        print(f"   Method 1 (Original): {len(text1)} chars - {text1[:50]}...")
        
        # Method 2: Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text2 = pytesseract.image_to_string(gray)
        print(f"   Method 2 (Grayscale): {len(text2)} chars - {text2[:50]}...")
        
        # Method 3: Threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text3 = pytesseract.image_to_string(thresh)
        print(f"   Method 3 (Threshold): {len(text3)} chars - {text3[:50]}...")
        
        # Method 4: Different PSM modes
        for psm in [6, 7, 8, 13]:
            try:
                text_psm = pytesseract.image_to_string(gray, config=f'--psm {psm}')
                if len(text_psm) > len(text1):
                    print(f"   Method PSM {psm}: {len(text_psm)} chars - {text_psm[:50]}...")
            except:
                pass
    
    # Step 3: Visual Analysis
    print("\n3️⃣ VISUAL ANALYSIS...")
    if bowl_path and os.path.exists(bowl_path):
        bowl_img = cv2.imread(bowl_path)
        h, w = bowl_img.shape[:2]
        print(f"   Bowl dimensions: {w}x{h}")
        
        # Analyze color distribution
        hsv = cv2.cvtColor(bowl_img, cv2.COLOR_BGR2HSV)
        
        # Check for specific colors
        color_checks = {
            "Orange (Masago)": ([10, 100, 100], [25, 255, 255]),
            "Red (Tuna)": ([0, 50, 50], [10, 255, 255]),
            "Pink (Salmon)": ([160, 50, 50], [180, 255, 255]),
            "Green (Seaweed)": ([35, 50, 50], [85, 255, 255]),
            "White (Rice)": ([0, 0, 200], [180, 30, 255]),
            "Dark (Nori)": ([0, 0, 0], [180, 255, 50])
        }
        
        print("   🎨 COLOR ANALYSIS:")
        for color_name, (lower, upper) in color_checks.items():
            mask = cv2.inRange(hsv, lower, upper)
            pixel_count = cv2.countNonZero(mask)
            percentage = (pixel_count / (h * w)) * 100
            print(f"   {color_name}: {percentage:.1f}% of image")
    
    # Step 4: Full Processing
    print("\n4️⃣ FULL PROCESSING...")
    result = processor.process_image(latest_image, "debug_output")
    
    if result:
        analysis = result.get('analysis', {})
        detected = analysis.get('detected_ingredients', [])
        
        print(f"   Final Results:")
        print(f"   Match: {analysis.get('match_percentage', 0)}%")
        print(f"   Detected: {len(detected)} ingredients")
        print(f"   Missing: {len(analysis.get('missing_ingredients', []))}")
        print(f"   Unexpected: {len(analysis.get('unexpected_ingredients', []))}")
        
        print(f"\n   📋 DETECTED INGREDIENTS:")
        for i, ing in enumerate(detected, 1):
            status = ing.get('status', 'unknown')
            confidence = ing.get('confidence', 0)
            from_receipt = ing.get('from_receipt', False)
            receipt_indicator = "📄" if from_receipt else "👁️"
            print(f"   {i:2d}. {ing.get('ingredient', 'Unknown')} ({confidence}%) {receipt_indicator} [{status}]")
    
    print(f"\n🎯 DIAGNOSIS:")
    print(f"   The system is working but has limitations:")
    print(f"   1. OCR struggles with receipt text quality")
    print(f"   2. Visual detection is basic color-based")
    print(f"   3. Need better ingredient recognition algorithms")
    print(f"   4. Receipt parsing needs improvement")

if __name__ == "__main__":
    debug_latest_image()

