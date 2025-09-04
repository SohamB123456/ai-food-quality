#!/usr/bin/env python3
"""
Test the system with a complex bowl containing many ingredients
Based on the new image with: Salmon, Spicy Salmon, Sweet Corn, Cilantro, 
Green Onion, Garlic Crisps, Onion Crisps, White Rice, etc.
"""

import os
import sys
sys.path.append('.')

from processor import processor

def test_complex_bowl():
    """Test with the complex bowl image"""
    print("🍱 Testing Complex Bowl with Many Ingredients")
    print("=" * 60)
    
    # Expected ingredients from the receipt
    expected_ingredients = [
        "White Rice", "Salmon", "Spicy Salmon", "Sweet Corn", 
        "Cilantro", "Pokeworks Classic", "Shoyu Sauce", 
        "Heavy Flavor", "Green Onion", "Garlic Crisps", "Onion Crisps"
    ]
    
    print("📋 Expected ingredients from receipt:")
    for i, ing in enumerate(expected_ingredients, 1):
        print(f"   {i:2d}. {ing}")
    
    # Find the most recent uploaded image
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.endswith('.jpg') and not f.endswith('_bowl.jpg') and not f.endswith('_receipt.jpg')]
        if files:
            # Get the most recent file
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(uploads_dir, x)))
            image_path = os.path.join(uploads_dir, latest_file)
            
            print(f"\n📸 Testing with: {latest_file}")
            print(f"📁 Full path: {image_path}")
            
            try:
                result = processor.process_image(image_path, "test_complex_output")
                if result:
                    analysis = result.get('analysis', {})
                    
                    detected = analysis.get('detected_ingredients', [])
                    match_pct = analysis.get('match_percentage', 0)
                    missing = analysis.get('missing_ingredients', [])
                    unexpected = analysis.get('unexpected_ingredients', [])
                    
                    print(f"\n✅ ANALYSIS RESULTS:")
                    print(f"   🎯 Match Percentage: {match_pct}%")
                    print(f"   🔍 Detected Ingredients: {len(detected)}")
                    print(f"   ❌ Missing Ingredients: {len(missing)}")
                    print(f"   ⚠️  Unexpected Ingredients: {len(unexpected)}")
                    
                    print(f"\n🔍 DETECTED INGREDIENTS:")
                    for i, ing in enumerate(detected, 1):
                        status = ing.get('status', 'unknown')
                        confidence = ing.get('confidence', 0)
                        from_receipt = ing.get('from_receipt', False)
                        receipt_indicator = "📄" if from_receipt else "👁️"
                        print(f"   {i:2d}. {ing.get('ingredient', 'Unknown')} ({confidence}%) {receipt_indicator} [{status}]")
                    
                    if missing:
                        print(f"\n❌ MISSING INGREDIENTS:")
                        for i, ing in enumerate(missing, 1):
                            print(f"   {i:2d}. {ing}")
                    
                    if unexpected:
                        print(f"\n⚠️  UNEXPECTED INGREDIENTS:")
                        for i, ing in enumerate(unexpected, 1):
                            print(f"   {i:2d}. {ing}")
                    
                    # Receipt text analysis
                    receipt_text = result.get('receipt_text', '')
                    print(f"\n📄 RECEIPT TEXT EXTRACTED:")
                    print(f"   Length: {len(receipt_text)} characters")
                    if receipt_text:
                        # Show first 200 characters
                        preview = receipt_text[:200] + "..." if len(receipt_text) > 200 else receipt_text
                        print(f"   Preview: {preview}")
                    
                    # Summary
                    print(f"\n📊 COMPLEX BOWL ANALYSIS SUMMARY:")
                    print(f"   This bowl contains {len(detected)} detected ingredients")
                    print(f"   Match rate: {match_pct}%")
                    if match_pct > 70:
                        print(f"   🎉 EXCELLENT: High match rate for complex bowl!")
                    elif match_pct > 40:
                        print(f"   ✅ GOOD: Reasonable match rate for complex bowl")
                    else:
                        print(f"   ⚠️  NEEDS IMPROVEMENT: Low match rate")
                    
                    return {
                        'match_pct': match_pct,
                        'detected_count': len(detected),
                        'missing_count': len(missing),
                        'unexpected_count': len(unexpected)
                    }
                else:
                    print("❌ Failed to process image")
                    return None
                    
            except Exception as e:
                print(f"❌ Error processing image: {e}")
                return None
        else:
            print("❌ No uploaded images found in uploads/ directory")
            return None
    else:
        print("❌ Uploads directory not found")
        return None

if __name__ == "__main__":
    result = test_complex_bowl()
    if result:
        print(f"\n🎯 FINAL RESULT: {result['match_pct']}% match with {result['detected_count']} ingredients detected")

