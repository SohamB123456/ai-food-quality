#!/usr/bin/env python3
"""
Simple test with manual CSV parsing to handle the inconsistent format
"""

import os
import sys
sys.path.append('.')

from processor import processor

def parse_labels_manually():
    """Manually parse the CSV to handle inconsistent formatting"""
    labels = {}
    
    with open('labels.csv', 'r') as f:
        lines = f.readlines()
    
    for line in lines[1:]:  # Skip header
        line = line.strip()
        if not line:
            continue
            
        # Find the first comma to separate filename from ingredients
        comma_pos = line.find(',')
        if comma_pos == -1:
            continue
            
        filename = line[:comma_pos].strip()
        ingredients_str = line[comma_pos+1:].strip()
        
        # Remove quotes if present
        if ingredients_str.startswith('"') and ingredients_str.endswith('"'):
            ingredients_str = ingredients_str[1:-1]
        
        # Split by comma and clean up
        ingredients = [ing.strip() for ing in ingredients_str.split(',')]
        labels[filename] = ingredients
    
    return labels

def test_single_image(image_path, expected_ingredients):
    """Test a single image against ground truth"""
    filename = os.path.basename(image_path)
    print(f"\n🧪 Testing: {filename}")
    print(f"📋 Expected: {len(expected_ingredients)} ingredients")
    for i, ing in enumerate(expected_ingredients, 1):
        print(f"  {i:2d}. {ing}")
    
    try:
        # Process the image
        result = processor.process_image(image_path, "test_simple_output")
        if not result:
            return None
        
        analysis = result.get('analysis', {})
        detected_ingredients = analysis.get('detected_ingredients', [])
        
        # Extract ingredient names from detected results
        detected_names = [ing.get('ingredient', '') for ing in detected_ingredients]
        
        # Calculate metrics
        expected_set = set(expected_ingredients)
        detected_set = set(detected_names)
        
        true_positives = expected_set.intersection(detected_set)
        false_positives = detected_set - expected_set
        false_negatives = expected_set - detected_set
        
        precision = len(true_positives) / len(detected_set) if detected_set else 0
        recall = len(true_positives) / len(expected_set) if expected_set else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n📊 Results:")
        print(f"  Expected: {len(expected_set)} ingredients")
        print(f"  Detected: {len(detected_set)} ingredients")
        print(f"  Precision: {precision:.1%}")
        print(f"  Recall: {recall:.1%}")
        print(f"  F1 Score: {f1_score:.1%}")
        
        print(f"\n✅ True Positives: {list(true_positives)}")
        print(f"❌ False Positives: {list(false_positives)}")
        print(f"⚠️  False Negatives: {list(false_negatives)}")
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': list(true_positives),
            'false_positives': list(false_positives),
            'false_negatives': list(false_negatives)
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🧪 Simple Labeled Testing")
    print("=" * 40)
    
    # Load labels
    labels = parse_labels_manually()
    print(f"📋 Loaded {len(labels)} labeled images")
    
    # Test a few images
    test_images = [
        'PHOTO-2025-07-21-11-44-42.jpg',
        'PHOTO-2025-07-21-11-44-42 3.jpg',
        'PHOTO-2025-07-21-11-44-41.jpg'
    ]
    
    results = []
    for filename in test_images:
        if filename in labels:
            expected = labels[filename]
            image_path = os.path.join('Bowls', filename)
            
            if os.path.exists(image_path):
                result = test_single_image(image_path, expected)
                if result:
                    results.append(result)
            else:
                print(f"⚠️ Image not found: {filename}")
        else:
            print(f"⚠️ No labels for: {filename}")
    
    # Summary
    if results:
        avg_precision = sum(r['precision'] for r in results) / len(results)
        avg_recall = sum(r['recall'] for r in results) / len(results)
        avg_f1 = sum(r['f1_score'] for r in results) / len(results)
        
        print(f"\n📊 SUMMARY:")
        print(f"  Average Precision: {avg_precision:.1%}")
        print(f"  Average Recall: {avg_recall:.1%}")
        print(f"  Average F1 Score: {avg_f1:.1%}")

if __name__ == "__main__":
    main()

