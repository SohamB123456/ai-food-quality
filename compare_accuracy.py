#!/usr/bin/env python3
"""
Compare GPT-4o vs Local Analysis accuracy using labels.csv
"""

import os
import sys
sys.path.append('.')

from processor import processor
import csv

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

def calculate_metrics(expected, detected):
    """Calculate precision, recall, and F1 score"""
    expected_set = set(expected)
    detected_set = set(detected)
    
    # True positives: ingredients correctly detected
    true_positives = expected_set.intersection(detected_set)
    
    # False positives: ingredients detected but not expected
    false_positives = detected_set - expected_set
    
    # False negatives: ingredients expected but not detected
    false_negatives = expected_set - detected_set
    
    # Calculate metrics
    precision = len(true_positives) / len(detected_set) if detected_set else 0
    recall = len(true_positives) / len(expected_set) if expected_set else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'true_positives': list(true_positives),
        'false_positives': list(false_positives),
        'false_negatives': list(false_negatives),
        'expected_count': len(expected_set),
        'detected_count': len(detected_set)
    }

def test_with_gpt4o(image_path, expected_ingredients):
    """Test with GPT-4o enabled"""
    print(f"\n🤖 Testing with GPT-4o: {os.path.basename(image_path)}")
    
    try:
        result = processor.process_image(image_path, "test_gpt4o_comparison")
        if not result:
            return None
        
        analysis = result.get('analysis', {})
        detected_ingredients = analysis.get('detected_ingredients', [])
        
        # Extract ingredient names from detected results
        detected_names = [ing.get('ingredient', '') for ing in detected_ingredients]
        
        metrics = calculate_metrics(expected_ingredients, detected_names)
        
        print(f"  📊 GPT-4o Results:")
        print(f"    Precision: {metrics['precision']:.1%}")
        print(f"    Recall: {metrics['recall']:.1%}")
        print(f"    F1 Score: {metrics['f1_score']:.1%}")
        print(f"    Expected: {metrics['expected_count']}, Detected: {metrics['detected_count']}")
        
        return metrics
        
    except Exception as e:
        print(f"  ❌ GPT-4o Error: {e}")
        return None

def test_with_local_only(image_path, expected_ingredients):
    """Test with local analysis only (disable GPT-4o)"""
    print(f"\n🔧 Testing with Local Analysis: {os.path.basename(image_path)}")
    
    # Temporarily disable GPT-4o by setting a dummy API key
    original_key = processor.api_key
    processor.api_key = "dummy_key_to_force_local_fallback"
    
    try:
        result = processor.process_image(image_path, "test_local_comparison")
        if not result:
            return None
        
        analysis = result.get('analysis', {})
        detected_ingredients = analysis.get('detected_ingredients', [])
        
        # Extract ingredient names from detected results
        detected_names = [ing.get('ingredient', '') for ing in detected_ingredients]
        
        metrics = calculate_metrics(expected_ingredients, detected_names)
        
        print(f"  📊 Local Results:")
        print(f"    Precision: {metrics['precision']:.1%}")
        print(f"    Recall: {metrics['recall']:.1%}")
        print(f"    F1 Score: {metrics['f1_score']:.1%}")
        print(f"    Expected: {metrics['expected_count']}, Detected: {metrics['detected_count']}")
        
        return metrics
        
    except Exception as e:
        print(f"  ❌ Local Error: {e}")
        return None
    finally:
        # Restore original API key
        processor.api_key = original_key

def main():
    print("🔬 GPT-4o vs Local Analysis Accuracy Comparison")
    print("=" * 55)
    
    # Load labels
    labels = parse_labels_manually()
    print(f"📋 Loaded {len(labels)} labeled images")
    
    # Test images that exist in Bowls folder
    test_images = [
        'PHOTO-2025-07-21-11-44-42.jpg',
        'PHOTO-2025-07-21-11-44-42 3.jpg',
        'PHOTO-2025-07-21-11-44-41.jpg',
        'PHOTO-2025-07-21-11-44-41 5.jpg',
        'PHOTO-2025-07-21-11-44-40.jpg'
    ]
    
    gpt4o_results = []
    local_results = []
    
    for filename in test_images:
        if filename in labels:
            expected = labels[filename]
            image_path = os.path.join('Bowls', filename)
            
            if os.path.exists(image_path):
                print(f"\n{'='*60}")
                print(f"🧪 Testing: {filename}")
                print(f"📋 Expected: {len(expected)} ingredients")
                for i, ing in enumerate(expected, 1):
                    print(f"  {i:2d}. {ing}")
                
                # Test with GPT-4o
                gpt4o_metrics = test_with_gpt4o(image_path, expected)
                if gpt4o_metrics:
                    gpt4o_results.append(gpt4o_metrics)
                
                # Test with local analysis
                local_metrics = test_with_local_only(image_path, expected)
                if local_metrics:
                    local_results.append(local_metrics)
                
                # Compare results
                if gpt4o_metrics and local_metrics:
                    print(f"\n  🆚 Comparison:")
                    print(f"    F1 Score: GPT-4o {gpt4o_metrics['f1_score']:.1%} vs Local {local_metrics['f1_score']:.1%}")
                    improvement = gpt4o_metrics['f1_score'] - local_metrics['f1_score']
                    print(f"    Improvement: {improvement:+.1%}")
            else:
                print(f"⚠️ Image not found: {filename}")
        else:
            print(f"⚠️ No labels for: {filename}")
    
    # Summary
    if gpt4o_results and local_results:
        print(f"\n{'='*60}")
        print(f"📊 FINAL COMPARISON SUMMARY")
        print(f"{'='*60}")
        
        # Calculate averages
        gpt4o_avg_precision = sum(r['precision'] for r in gpt4o_results) / len(gpt4o_results)
        gpt4o_avg_recall = sum(r['recall'] for r in gpt4o_results) / len(gpt4o_results)
        gpt4o_avg_f1 = sum(r['f1_score'] for r in gpt4o_results) / len(gpt4o_results)
        
        local_avg_precision = sum(r['precision'] for r in local_results) / len(local_results)
        local_avg_recall = sum(r['recall'] for r in local_results) / len(local_results)
        local_avg_f1 = sum(r['f1_score'] for r in local_results) / len(local_results)
        
        print(f"🤖 GPT-4o Average Performance:")
        print(f"   Precision: {gpt4o_avg_precision:.1%}")
        print(f"   Recall: {gpt4o_avg_recall:.1%}")
        print(f"   F1 Score: {gpt4o_avg_f1:.1%}")
        
        print(f"\n🔧 Local Analysis Average Performance:")
        print(f"   Precision: {local_avg_precision:.1%}")
        print(f"   Recall: {local_avg_recall:.1%}")
        print(f"   F1 Score: {local_avg_f1:.1%}")
        
        print(f"\n🎯 Improvement with GPT-4o:")
        print(f"   Precision: {gpt4o_avg_precision - local_avg_precision:+.1%}")
        print(f"   Recall: {gpt4o_avg_recall - local_avg_recall:+.1%}")
        print(f"   F1 Score: {gpt4o_avg_f1 - local_avg_f1:+.1%}")
        
        # Overall improvement
        overall_improvement = gpt4o_avg_f1 - local_avg_f1
        if overall_improvement > 0:
            print(f"\n🏆 GPT-4o is {overall_improvement:.1%} better overall!")
        else:
            print(f"\n⚠️ Local analysis performed better by {abs(overall_improvement):.1%}")

if __name__ == "__main__":
    main()

