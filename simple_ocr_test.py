#!/usr/bin/env python3
"""
Simple OCR Test - Test OCR directly on original images
"""

import cv2
import pytesseract
import os
import sys
sys.path.append('.')

def test_ocr_direct(image_path):
    """Test OCR directly on the original image"""
    print(f"🔍 Testing OCR directly on: {os.path.basename(image_path)}")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Failed to load image")
        return
    
    height, width = img.shape[:2]
    print(f"📏 Image size: {width}x{height}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply denoising
    denoised = cv2.medianBlur(gray, 5)
    
    # Apply adaptive threshold (the method that was working best)
    adaptive_thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Try different OCR methods
    print("\n📄 OCR Results:")
    print("-" * 40)
    
    # Method 1: Original image
    print("1️⃣ Original image:")
    text1 = pytesseract.image_to_string(img)
    print(f"   {text1[:200]}...")
    
    # Method 2: Grayscale
    print("\n2️⃣ Grayscale:")
    text2 = pytesseract.image_to_string(gray)
    print(f"   {text2[:200]}...")
    
    # Method 3: Denoised
    print("\n3️⃣ Denoised:")
    text3 = pytesseract.image_to_string(denoised)
    print(f"   {text3[:200]}...")
    
    # Method 4: Adaptive threshold (best method)
    print("\n4️⃣ Adaptive threshold (best method):")
    text4 = pytesseract.image_to_string(adaptive_thresh)
    print(f"   {text4[:200]}...")
    
    # Save the best preprocessed image for inspection
    output_dir = "ocr_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_preprocessed.jpg")
    cv2.imwrite(output_path, adaptive_thresh)
    print(f"\n💾 Saved preprocessed image: {output_path}")
    
    return text4  # Return the best result

def main():
    """Main function"""
    print("🔍 Simple OCR Test Tool")
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
    best_text = test_ocr_direct(image_path)
    
    # Show full text
    if best_text:
        print(f"\n📄 Full OCR Text:")
        print("=" * 40)
        print(best_text)
        print("=" * 40)
    
    # Ask if user wants to test more
    if len(images) > 1:
        print(f"\n💡 Want to test another image? Run:")
        print(f"   python3 simple_ocr_test.py <image_number>")
        print(f"   Example: python3 simple_ocr_test.py 2")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific image by number
        try:
            image_num = int(sys.argv[1]) - 1
            images = [f for f in os.listdir('newImages') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if 0 <= image_num < len(images):
                image_path = os.path.join('newImages', images[image_num])
                test_ocr_direct(image_path)
            else:
                print(f"❌ Invalid image number. Choose 1-{len(images)}")
        except ValueError:
            print("❌ Please provide a number")
    else:
        main() 