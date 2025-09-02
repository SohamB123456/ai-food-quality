#!/usr/bin/env python3
"""
OCR Debug Script - Simple script to see what's happening with OCR
"""

import cv2
import pytesseract
import os
import sys
sys.path.append('.')

from app import processor

def debug_ocr(image_path):
    """Debug OCR for a specific image"""
    print(f"🔍 Debugging OCR for: {os.path.basename(image_path)}")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Step 1: Show original image info
    print("\n1️⃣ Original Image Info:")
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Failed to load image")
        return
    
    height, width = img.shape[:2]
    print(f"   📏 Size: {width}x{height}")
    print(f"   📁 Path: {image_path}")
    
    # Step 2: Try auto-cropping
    print("\n2️⃣ Auto-cropping:")
    try:
        receipt_path, bowl_path = processor.crop_image(image_path, "ocr_debug_output")
        if receipt_path and bowl_path:
            print(f"   ✅ Receipt: {os.path.basename(receipt_path)}")
            print(f"   ✅ Bowl: {os.path.basename(bowl_path)}")
        else:
            print("   ❌ Cropping failed")
            return
    except Exception as e:
        print(f"   ❌ Cropping error: {e}")
        return
    
    # Step 3: Test OCR on receipt
    print("\n3️⃣ OCR on Receipt:")
    try:
        receipt_text = processor.extract_text_from_receipt(receipt_path)
        print(f"   📄 Raw OCR text:")
        print(f"   {'-' * 40}")
        print(f"   {receipt_text}")
        print(f"   {'-' * 40}")
    except Exception as e:
        print(f"   ❌ OCR error: {e}")
        return
    
    # Step 4: Extract ingredients
    print("\n4️⃣ Ingredient Extraction:")
    try:
        ingredients = processor.extract_ingredients_from_receipt(receipt_text)
        if ingredients:
            print(f"   ✅ Found {len(ingredients)} ingredients:")
            for i, ingredient in enumerate(ingredients, 1):
                print(f"      {i}. {ingredient}")
        else:
            print("   ❌ No ingredients found")
    except Exception as e:
        print(f"   ❌ Ingredient extraction error: {e}")
    
    # Step 5: Show cropped images info
    print("\n5️⃣ Cropped Images Info:")
    receipt_img = cv2.imread(receipt_path)
    bowl_img = cv2.imread(bowl_path)
    
    if receipt_img is not None:
        r_height, r_width = receipt_img.shape[:2]
        print(f"   📄 Receipt: {r_width}x{r_height}")
    else:
        print("   ❌ Failed to load receipt image")
    
    if bowl_img is not None:
        b_height, b_width = bowl_img.shape[:2]
        print(f"   🍽️  Bowl: {b_width}x{b_height}")
    else:
        print("   ❌ Failed to load bowl image")
    
    print(f"\n🎉 Debug completed! Check ocr_debug_output/ for cropped images")

def main():
    """Main function"""
    print("🔍 OCR Debug Tool")
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
    debug_ocr(image_path)
    
    # Ask if user wants to test more
    if len(images) > 1:
        print(f"\n💡 Want to test another image? Run:")
        print(f"   python3 ocr_debug.py <image_number>")
        print(f"   Example: python3 ocr_debug.py 2")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific image by number
        try:
            image_num = int(sys.argv[1]) - 1
            images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if 0 <= image_num < len(images):
                image_path = os.path.join('newImages', images[image_num])
                debug_ocr(image_path)
            else:
                print(f"❌ Invalid image number. Choose 1-{len(images)}")
        except ValueError:
            print("❌ Please provide a number")
    else:
        main() 