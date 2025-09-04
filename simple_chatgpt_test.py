#!/usr/bin/env python3
"""
Simple ChatGPT-4o Test - Direct Image Analysis
No OCR, no OpenCV preprocessing - just pure AI vision
"""

import os
import sys
import csv
import json
import base64
from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY

class SimpleChatGPTTester:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.labels = {}
        self.load_labels()
    
    def load_labels(self):
        """Load ground truth labels from CSV"""
        print("📋 Loading ground truth labels...")
        try:
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
                self.labels[filename] = ingredients
            
            print(f"✅ Loaded {len(self.labels)} labeled images")
        except FileNotFoundError:
            print("❌ labels.csv not found")
            return
    
    def encode_image(self, image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_with_chatgpt(self, image_path):
        """Analyze image directly with ChatGPT-4o"""
        print(f"🤖 Analyzing with ChatGPT-4o: {os.path.basename(image_path)}")
        
        try:
            # Encode image
            image_b64 = self.encode_image(image_path)
            
            # Simple, direct prompt
            prompt = """Can you check the ingredients on the receipt and on the bowl and compare them to see if there is anything missing?

Please analyze this image and provide a JSON response with:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}

Focus on identifying all visible ingredients in both the receipt and the bowl, then compare them."""
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a food quality assurance expert. Always respond with valid JSON."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                        ],
                    },
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            print(f"✅ ChatGPT analysis complete")
            
            # Try to parse JSON
            try:
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                result = json.loads(content.strip())
                return result
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse ChatGPT JSON response: {e}")
                print(f"Raw response: {content}")
                return None
                
        except Exception as e:
            print(f"❌ ChatGPT API error: {e}")
            return None
    
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
    
    def test_single_image(self, image_path, expected_ingredients):
        """Test a single image against ground truth"""
        filename = os.path.basename(image_path)
        print(f"\n🧪 Testing: {filename}")
        print(f"📋 Expected: {len(expected_ingredients)} ingredients")
        for i, ing in enumerate(expected_ingredients, 1):
            print(f"  {i:2d}. {ing}")
        
        # Analyze with ChatGPT
        result = self.analyze_with_chatgpt(image_path)
        
        if not result:
            return {
                'filename': filename,
                'error': 'ChatGPT analysis failed',
                'expected': expected_ingredients,
                'detected': [],
                'match_percentage': 0
            }
        
        # Extract detected ingredients (combine receipt and bowl)
        receipt_ingredients = result.get('receipt_ingredients', [])
        bowl_ingredients = result.get('bowl_ingredients', [])
        detected_ingredients = list(set(receipt_ingredients + bowl_ingredients))
        
        # Calculate metrics
        metrics = self.calculate_metrics(expected_ingredients, detected_ingredients)
        
        print(f"\n📊 ChatGPT Results:")
        print(f"  Receipt ingredients: {len(receipt_ingredients)}")
        print(f"  Bowl ingredients: {len(bowl_ingredients)}")
        print(f"  Total detected: {len(detected_ingredients)}")
        print(f"  Precision: {metrics['precision']:.1%}")
        print(f"  Recall: {metrics['recall']:.1%}")
        print(f"  F1 Score: {metrics['f1_score']:.1%}")
        
        print(f"\n✅ True Positives: {metrics['true_positives']}")
        print(f"❌ False Positives: {metrics['false_positives']}")
        print(f"⚠️  False Negatives: {metrics['false_negatives']}")
        
        return {
            'filename': filename,
            'expected': expected_ingredients,
            'detected': detected_ingredients,
            'receipt_ingredients': receipt_ingredients,
            'bowl_ingredients': bowl_ingredients,
            'missing_ingredients': result.get('missing_ingredients', []),
            'extra_ingredients': result.get('extra_ingredients', []),
            'chatgpt_match_percentage': result.get('match_percentage', 0),
            'metrics': metrics
        }
    
    def test_all_images(self, max_images=None):
        """Test all labeled images"""
        print(f"\n🚀 Starting ChatGPT-4o Testing...")
        print(f"📊 Testing against {len(self.labels)} labeled images")
        
        if max_images:
            print(f"🔢 Limiting to first {max_images} images")
        
        results = []
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
            results.append(result)
            tested_count += 1
        
        print(f"\n✅ Completed testing {tested_count} images")
        return results
    
    def generate_report(self, results):
        """Generate comprehensive test report"""
        if not results:
            print("❌ No test results available")
            return
        
        print(f"\n📊 CHATGPT-4O TEST REPORT")
        print("=" * 50)
        
        # Overall statistics
        total_tests = len(results)
        successful_tests = len([r for r in results if 'error' not in r])
        
        print(f"📈 Overall Statistics:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_tests - successful_tests}")
        print(f"   Success Rate: {successful_tests/total_tests:.1%}")
        
        if successful_tests > 0:
            # Calculate average metrics
            precisions = [r['metrics']['precision'] for r in results if 'metrics' in r]
            recalls = [r['metrics']['recall'] for r in results if 'metrics' in r]
            f1_scores = [r['metrics']['f1_score'] for r in results if 'metrics' in r]
            chatgpt_matches = [r.get('chatgpt_match_percentage', 0) for r in results if 'chatgpt_match_percentage' in r]
            
            avg_precision = sum(precisions) / len(precisions)
            avg_recall = sum(recalls) / len(recalls)
            avg_f1 = sum(f1_scores) / len(f1_scores)
            avg_chatgpt_match = sum(chatgpt_matches) / len(chatgpt_matches)
            
            print(f"\n🎯 Average Performance:")
            print(f"   Precision: {avg_precision:.1%}")
            print(f"   Recall: {avg_recall:.1%}")
            print(f"   F1 Score: {avg_f1:.1%}")
            print(f"   ChatGPT Match %: {avg_chatgpt_match:.1%}")
            
            # Best and worst performers
            best_result = max(results, key=lambda x: x['metrics']['f1_score'] if 'metrics' in x else 0)
            worst_result = min(results, key=lambda x: x['metrics']['f1_score'] if 'metrics' in x else 0)
            
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
        report_file = f"chatgpt_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {report_file}")

def main():
    """Main testing function"""
    print("🤖 ChatGPT-4o Direct Image Analysis Test")
    print("=" * 50)
    
    tester = SimpleChatGPTTester()
    
    if not tester.labels:
        print("❌ No labels loaded. Exiting.")
        return
    
    # Test a few images first
    print("\n🔬 Testing first 3 images...")
    results = tester.test_all_images(max_images=3)
    
    # Generate report
    tester.generate_report(results)

if __name__ == "__main__":
    main()
