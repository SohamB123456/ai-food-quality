#!/usr/bin/env python3
"""
ChatGPT Model Comparison Test
Tests multiple ChatGPT models to find the best performer for ingredient detection
"""

import os
import sys
import csv
import json
import base64
from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY

class ModelComparisonTester:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.labels = {}
        self.models_to_test = [
            "gpt-4o",
            "gpt-4o-mini"
        ]
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
    
    def analyze_with_model(self, image_path, model_name):
        """Analyze image with specified model"""
        print(f"🤖 Analyzing with {model_name}: {os.path.basename(image_path)}")
        
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
            
            # Prepare API parameters based on model
            api_params = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a food quality assurance expert. Always respond with valid JSON."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                        ],
                    },
                ],
            }
            
            # Add model-specific parameters
            if model_name == "gpt-5":
                api_params["max_completion_tokens"] = 1000
                # GPT-5 doesn't support temperature parameter
            else:
                api_params["max_tokens"] = 1000
                api_params["temperature"] = 0.1
            
            # Call OpenAI API
            response = self.client.chat.completions.create(**api_params)
            
            # Parse response
            content = response.choices[0].message.content.strip()
            print(f"✅ {model_name} analysis complete")
            
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
                print(f"⚠️ Failed to parse {model_name} JSON response: {e}")
                print(f"Raw response: {content[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ {model_name} API error: {e}")
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
    
    def test_single_image_with_all_models(self, image_path, expected_ingredients):
        """Test a single image with all models"""
        filename = os.path.basename(image_path)
        print(f"\n🧪 Testing: {filename}")
        print(f"📋 Expected: {len(expected_ingredients)} ingredients")
        for i, ing in enumerate(expected_ingredients, 1):
            print(f"  {i:2d}. {ing}")
        
        results = {}
        
        for model_name in self.models_to_test:
            print(f"\n--- Testing with {model_name} ---")
            
            # Analyze with model
            result = self.analyze_with_model(image_path, model_name)
            
            if not result:
                results[model_name] = {
                    'filename': filename,
                    'error': f'{model_name} analysis failed',
                    'expected': expected_ingredients,
                    'detected': [],
                    'match_percentage': 0
                }
                continue
            
            # Extract detected ingredients (combine receipt and bowl)
            receipt_ingredients = result.get('receipt_ingredients', [])
            bowl_ingredients = result.get('bowl_ingredients', [])
            detected_ingredients = list(set(receipt_ingredients + bowl_ingredients))
            
            # Calculate metrics
            metrics = self.calculate_metrics(expected_ingredients, detected_ingredients)
            
            print(f"\n📊 {model_name} Results:")
            print(f"  Receipt ingredients: {len(receipt_ingredients)}")
            print(f"  Bowl ingredients: {len(bowl_ingredients)}")
            print(f"  Total detected: {len(detected_ingredients)}")
            print(f"  Precision: {metrics['precision']:.1%}")
            print(f"  Recall: {metrics['recall']:.1%}")
            print(f"  F1 Score: {metrics['f1_score']:.1%}")
            
            results[model_name] = {
                'filename': filename,
                'expected': expected_ingredients,
                'detected': detected_ingredients,
                'receipt_ingredients': receipt_ingredients,
                'bowl_ingredients': bowl_ingredients,
                'missing_ingredients': result.get('missing_ingredients', []),
                'extra_ingredients': result.get('extra_ingredients', []),
                'model_match_percentage': result.get('match_percentage', 0),
                'metrics': metrics
            }
        
        return results
    
    def test_all_models(self, max_images=3):
        """Test all models on a subset of images"""
        print(f"\n🚀 Starting Model Comparison Test...")
        print(f"📊 Testing {len(self.models_to_test)} models: {', '.join(self.models_to_test)}")
        print(f"🔢 Testing on first {max_images} available images")
        
        all_results = {}
        tested_count = 0
        
        for filename, expected_ingredients in self.labels.items():
            if tested_count >= max_images:
                break
                
            # Check if image exists in Bowls folder
            image_path = os.path.join('Bowls', filename)
            if not os.path.exists(image_path):
                print(f"⚠️ Image not found: {filename}")
                continue
            
            # Test this image with all models
            image_results = self.test_single_image_with_all_models(image_path, expected_ingredients)
            all_results[filename] = image_results
            tested_count += 1
        
        print(f"\n✅ Completed testing {tested_count} images across all models")
        return all_results
    
    def generate_comparison_report(self, all_results):
        """Generate comprehensive comparison report"""
        if not all_results:
            print("❌ No test results available")
            return
        
        print(f"\n📊 MODEL COMPARISON REPORT")
        print("=" * 60)
        
        # Calculate average metrics for each model
        model_stats = {}
        
        for model_name in self.models_to_test:
            model_stats[model_name] = {
                'total_tests': 0,
                'successful_tests': 0,
                'precisions': [],
                'recalls': [],
                'f1_scores': [],
                'model_match_percentages': []
            }
        
        # Collect statistics
        for filename, image_results in all_results.items():
            for model_name, result in image_results.items():
                model_stats[model_name]['total_tests'] += 1
                
                if 'error' not in result:
                    model_stats[model_name]['successful_tests'] += 1
                    if 'metrics' in result:
                        model_stats[model_name]['precisions'].append(result['metrics']['precision'])
                        model_stats[model_name]['recalls'].append(result['metrics']['recall'])
                        model_stats[model_name]['f1_scores'].append(result['metrics']['f1_score'])
                    if 'model_match_percentage' in result:
                        model_stats[model_name]['model_match_percentages'].append(result['model_match_percentage'])
        
        # Display results for each model
        print(f"\n🏆 MODEL PERFORMANCE RANKING:")
        print("-" * 60)
        
        model_rankings = []
        
        for model_name in self.models_to_test:
            stats = model_stats[model_name]
            
            if stats['successful_tests'] > 0:
                avg_precision = sum(stats['precisions']) / len(stats['precisions'])
                avg_recall = sum(stats['recalls']) / len(stats['recalls'])
                avg_f1 = sum(stats['f1_scores']) / len(stats['f1_scores'])
                avg_model_match = sum(stats['model_match_percentages']) / len(stats['model_match_percentages']) if stats['model_match_percentages'] else 0
                
                model_rankings.append({
                    'model': model_name,
                    'f1_score': avg_f1,
                    'precision': avg_precision,
                    'recall': avg_recall,
                    'model_match': avg_model_match,
                    'success_rate': stats['successful_tests'] / stats['total_tests']
                })
                
                print(f"\n🤖 {model_name.upper()}:")
                print(f"   Success Rate: {stats['successful_tests']}/{stats['total_tests']} ({stats['successful_tests']/stats['total_tests']:.1%})")
                print(f"   Average Precision: {avg_precision:.1%}")
                print(f"   Average Recall: {avg_recall:.1%}")
                print(f"   Average F1 Score: {avg_f1:.1%}")
                print(f"   Average Model Match %: {avg_model_match:.1%}")
            else:
                print(f"\n❌ {model_name.upper()}: No successful tests")
        
        # Rank models by F1 score
        model_rankings.sort(key=lambda x: x['f1_score'], reverse=True)
        
        print(f"\n🥇 FINAL RANKING (by F1 Score):")
        print("-" * 60)
        for i, model_data in enumerate(model_rankings, 1):
            print(f"{i}. {model_data['model']}: F1={model_data['f1_score']:.1%}, Precision={model_data['precision']:.1%}, Recall={model_data['recall']:.1%}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"model_comparison_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'all_results': all_results,
                'model_stats': model_stats,
                'rankings': model_rankings
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {report_file}")

def main():
    """Main testing function"""
    print("🤖 ChatGPT Model Comparison Test")
    print("=" * 50)
    
    tester = ModelComparisonTester()
    
    if not tester.labels:
        print("❌ No labels loaded. Exiting.")
        return
    
    # Test models on just 2 images for quick comparison
    print("\n🔬 Testing models on first 2 images...")
    results = tester.test_all_models(max_images=2)
    
    # Generate comparison report
    tester.generate_comparison_report(results)

if __name__ == "__main__":
    main()
