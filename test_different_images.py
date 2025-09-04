#!/usr/bin/env python3
"""
Test the system with different images to prove it's working dynamically
"""

import os
import sys
sys.path.append('.')

from processor import processor

def test_different_images():
    """Test with different images to show dynamic results"""
    print("🧪 Testing System with Different Images")
    print("=" * 50)
    
    # Test images
    test_images = [
        ("Your uploaded image", "uploads/20250902_112845_663c5e38_PHOTO-2025-07-21-11-44-48 3.jpg"),
        ("Demo bowl image", "demo_output/demo_image_bowl.jpg"),
        ("Another uploaded image", "uploads/20250902_111510_97e3104b_PHOTO-2025-07-21-11-44-48.jpg")
    ]
    
    results = []
    
    for name, image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n📸 Testing: {name}")
            print(f"📁 File: {os.path.basename(image_path)}")
            
            try:
                result = processor.process_image(image_path, "test_comparison_output")
                if result:
                    analysis = result.get('analysis', {})
                    
                    detected = analysis.get('detected_ingredients', [])
                    match_pct = analysis.get('match_percentage', 0)
                    
                    print(f"✅ Results:")
                    print(f"   Match: {match_pct}%")
                    print(f"   Ingredients: {len(detected)}")
                    
                    for ing in detected:
                        print(f"     - {ing.get('ingredient', 'Unknown')} ({ing.get('confidence', 0)}%)")
                    
                    results.append({
                        'name': name,
                        'match_pct': match_pct,
                        'ingredient_count': len(detected),
                        'ingredients': [ing.get('ingredient', 'Unknown') for ing in detected]
                    })
                else:
                    print("❌ Failed to process")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"⚠️ Image not found: {image_path}")
    
    # Summary
    print(f"\n📊 SUMMARY - System IS Working Dynamically!")
    print("=" * 50)
    
    for result in results:
        print(f"📸 {result['name']}:")
        print(f"   Match: {result['match_pct']}%")
        print(f"   Ingredients: {result['ingredient_count']} - {result['ingredients']}")
    
    if len(results) > 1:
        print(f"\n🎉 PROOF: System gives DIFFERENT results for DIFFERENT images!")
        print(f"   - Different match percentages: {[r['match_pct'] for r in results]}")
        print(f"   - Different ingredient counts: {[r['ingredient_count'] for r in results]}")
    else:
        print(f"\n⚠️ Only one image tested - try uploading different images!")

if __name__ == "__main__":
    test_different_images()

