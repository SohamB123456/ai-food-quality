#!/usr/bin/env python3
"""
Test the improved OCR function
"""

import sys
import os
sys.path.append('.')

from app import processor

def test_improved_ocr():
    """Test the improved OCR function"""
    receipt_path = "demo_output/PHOTO-2025-07-21-11-44-46 2_receipt.jpg"
    
    if not os.path.exists(receipt_path):
        print(f"Receipt image not found: {receipt_path}")
        return
    
    print("🧪 Testing Improved OCR Function")
    print("=" * 50)
    
    # Test OCR
    print("\n1️⃣ Testing OCR extraction...")
    receipt_text = processor.extract_text_from_receipt(receipt_path)
    print(f"📄 Extracted text: {receipt_text}")
    
    # Test ingredient extraction
    print("\n2️⃣ Testing ingredient extraction...")
    ingredients = processor.extract_ingredients_from_receipt(receipt_text)
    print(f"🔍 Found ingredients: {ingredients}")
    
    if ingredients:
        print("\n✅ Success! Found ingredients in receipt:")
        for ingredient in ingredients:
            print(f"   - {ingredient}")
    else:
        print("\n❌ No ingredients found in receipt text")

if __name__ == "__main__":
    test_improved_ocr() 