#!/usr/bin/env python3
"""
Comprehensive testing system using labels.csv and Bowls folder
Tests the system against ground truth data to measure accuracy
"""

import os
import sys
import csv
import json
from datetime import datetime
sys.path.append('.')

from processor import processor
from fuzzywuzzy import fuzz

class LabeledTester:
    def __init__(self):
        self.processor = processor
        self.labels = {}
        self.results = []
        self.load_labels()
    
    def load_labels(self):
        """Load ground truth labels from CSV"""
        print("📋 Loading ground truth labels...")
        try:
            with open('labels.csv', 'r', newline='') as f:
                # Use csv.reader with proper handling of multiline quoted fields
                reader = csv.reader(f)
                header = next(reader)  # Skip header
                
                for row in reader:
                    if len(row) < 2:
                        continue
                    filename = row[0]
                    ingredients_str = row[1]
                    
                    # Parse ingredients string into list
                    ingredients = [ing.strip() for ing in ingredients_str.split(',')]
                    
                    # Handle duplicate filenames by combining ingredients
                    if filename in self.labels:
                        print(f"⚠️ Duplicate filename found: {filename}")
                        # Combine ingredients from both entries
                        existing = set(self.labels[filename])
                        new = set(ingredients)
                        combined = list(existing.union(new))
                        self.labels[filename] = combined
                        print(f"   Combined: {len(combined)} total ingredients")
                    else:
                        self.labels[filename] = ingredients
            print(f"✅ Loaded {len(self.labels)} labeled images")
        except FileNotFoundError:
            print("❌ labels.csv not found")
            return
    
    def test_single_image(self, image_path, expected_ingredients):
        """Test a single image against ground truth"""
        filename = os.path.basename(image_path)
        print(f"\n🧪 Testing: {filename}")
        print(f"📋 Expected: {len(expected_ingredients)} ingredients")
        
        try:
            # Process the image
            result = self.processor.process_image(image_path, "test_labeled_output")
            if not result:
                return {
                    'filename': filename,
                    'error': 'Processing failed',
                    'expected': expected_ingredients,
                    'detected': [],
                    'match_percentage': 0
                }
            
            analysis = result.get('analysis', {})
            detected_ingredients = analysis.get('detected_ingredients', [])
            
            # Extract ingredient names from detected results
            detected_names = [ing.get('ingredient', '') for ing in detected_ingredients]
            
            # Calculate accuracy metrics
            metrics = self.calculate_metrics(expected_ingredients, detected_names)
            
            result_data = {
                'filename': filename,
                'expected': expected_ingredients,
                'detected': detected_names,
                'match_percentage': analysis.get('match_percentage', 0),
                'metrics': metrics,
                'analysis': analysis
            }
            
            print(f"✅ Results: {metrics['precision']:.1%} precision, {metrics['recall']:.1%} recall")
            return result_data
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'filename': filename,
                'error': str(e),
                'expected': expected_ingredients,
                'detected': [],
                'match_percentage': 0
            }
    
    def calculate_metrics(self, expected, detected):
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
    
    def test_all_images(self, max_images=None):
        """Test all labeled images"""
        print(f"\n🚀 Starting comprehensive testing...")
        print(f"📊 Testing against {len(self.labels)} labeled images")
        
        if max_images:
            print(f"🔢 Limiting to first {max_images} images")
        
        tested_count = 0
        for filename, expected_ingredients in self.labels.items():
            if max_images and tested_count >= max_images:
                break
                
            # Check if image exists in Bowls folder
            image_path = os.path.join('Bowls', filename)
            if not os.path.exists(image_path):
                print(f"⚠️ Image not found: {filename}")
                continue
            
            result = self.test_single_image(image_path, expected_ingredients)
            self.results.append(result)
            tested_count += 1
        
        print(f"\n✅ Completed testing {tested_count} images")
        return self.results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        if not self.results:
            print("❌ No test results available")
            return
        
        print(f"\n📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Overall statistics
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if 'error' not in r])
        
        print(f"📈 Overall Statistics:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_tests - successful_tests}")
        print(f"   Success Rate: {successful_tests/total_tests:.1%}")
        
        if successful_tests > 0:
            # Calculate average metrics
            precisions = [r['metrics']['precision'] for r in self.results if 'metrics' in r]
            recalls = [r['metrics']['recall'] for r in self.results if 'metrics' in r]
            f1_scores = [r['metrics']['f1_score'] for r in self.results if 'metrics' in r]
            
            avg_precision = sum(precisions) / len(precisions)
            avg_recall = sum(recalls) / len(recalls)
            avg_f1 = sum(f1_scores) / len(f1_scores)
            
            print(f"\n🎯 Average Performance:")
            print(f"   Precision: {avg_precision:.1%}")
            print(f"   Recall: {avg_recall:.1%}")
            print(f"   F1 Score: {avg_f1:.1%}")
            
            # Best and worst performers
            best_result = max(self.results, key=lambda x: x['metrics']['f1_score'] if 'metrics' in x else 0)
            worst_result = min(self.results, key=lambda x: x['metrics']['f1_score'] if 'metrics' in x else 0)
            
            print(f"\n🏆 Best Performance:")
            print(f"   File: {best_result['filename']}")
            print(f"   F1 Score: {best_result['metrics']['f1_score']:.1%}")
            print(f"   Expected: {len(best_result['expected'])} ingredients")
            print(f"   Detected: {len(best_result['detected'])} ingredients")
            
            print(f"\n⚠️ Worst Performance:")
            print(f"   File: {worst_result['filename']}")
            print(f"   F1 Score: {worst_result['metrics']['f1_score']:.1%}")
            print(f"   Expected: {len(worst_result['expected'])} ingredients")
            print(f"   Detected: {len(worst_result['detected'])} ingredients")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {report_file}")
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'avg_precision': avg_precision if successful_tests > 0 else 0,
            'avg_recall': avg_recall if successful_tests > 0 else 0,
            'avg_f1': avg_f1 if successful_tests > 0 else 0
        }

def main():
    """Main testing function"""
    print("🧪 PokeWorks QA System - Labeled Testing")
    print("=" * 50)
    
    tester = LabeledTester()
    
    if not tester.labels:
        print("❌ No labels loaded. Exiting.")
        return
    
    # Test a few images first
    print("\n🔬 Testing first 5 images...")
    results = tester.test_all_images(max_images=5)
    
    # Generate report
    report = tester.generate_report()
    
    # Ask if user wants to test more
    print(f"\n❓ Test more images? (y/n)")
    # For automated testing, we'll test a few more
    print("🔬 Testing 10 more images...")
    results = tester.test_all_images(max_images=15)
    report = tester.generate_report()

if __name__ == "__main__":
    main()
