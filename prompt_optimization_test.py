#!/usr/bin/env python3
"""
ChatGPT-4o Prompt Optimization Test
Tests different prompts to find the best one for ingredient detection
"""

import os
import sys
import json
import base64
from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY

class PromptOptimizer:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        
        # Define different prompt variations to test
        self.prompts = {
            "original": """Can you check the ingredients on the receipt and on the bowl and compare them to see if there is anything missing?

Please analyze this image and provide a JSON response with:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}

Focus on identifying all visible ingredients in both the receipt and the bowl, then compare them.""",

            "detailed_instructions": """You are a food quality assurance expert analyzing a poke bowl order. Your task is to:

1. Carefully examine the receipt to identify all listed ingredients
2. Carefully examine the bowl to identify all visible ingredients
3. Compare the two lists to find any discrepancies

Please provide a JSON response with:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}

Be very precise and only include ingredients you can clearly see or read. Pay attention to small details like sesame seeds, sauces, and garnishes.""",

            "step_by_step": """Analyze this poke bowl image step by step:

STEP 1: Read the receipt carefully and list all ingredients mentioned
STEP 2: Examine the bowl and identify all visible ingredients
STEP 3: Compare the two lists to find missing or extra ingredients

Provide your analysis as JSON:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}

Focus on accuracy over speed. Look for small ingredients like sesame seeds, sauces, and garnishes.""",

            "specific_ingredients": """You are analyzing a poke bowl for ingredient accuracy. Common poke bowl ingredients include:

Proteins: Ahi Tuna, Salmon, Spicy Tuna, Spicy Salmon, Shrimp, Chicken, Tofu, Lobster Surimi
Bases: White Rice, Brown Rice, Salad Mix
Vegetables: Cucumber, Edamame, Cabbage, Shredded Kale, Sliced Onions, Sweet Corn
Fruits: Mango, Pineapple, Mandarin Oranges
Seaweed: Hijiki Seaweed, Seaweed Salad, Shredded Nori
Garnishes: Cilantro, Green Onion, Serrano Peppers, Pickled Ginger
Sauces: Ponzu Fresh, Sweet Shoyu, Spicy Furikake, Sriracha Aioli
Toppings: Sesame Seeds, Masago, Wasabi, Soft Tofu, Surimi Salad
Crisps: Wonton Crisps, Garlic Crisps, Onion Crisps, Chili Crisp

Analyze the image and provide JSON:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}""",

            "quality_focus": """As a food quality control specialist, analyze this poke bowl order for accuracy:

1. Read the receipt thoroughly - note every ingredient listed
2. Examine the bowl systematically - check each section for ingredients
3. Pay special attention to:
   - Small toppings (sesame seeds, masago)
   - Sauces and dressings
   - Garnishes (cilantro, green onions)
   - Protein portions and types

Provide detailed JSON analysis:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}

Be thorough and accurate. It's better to miss something than to guess.""",

            "visual_analysis": """Perform a detailed visual analysis of this poke bowl image:

VISUAL INSPECTION CHECKLIST:
□ Read receipt text carefully
□ Identify base (rice/salad)
□ Count protein types and portions
□ Check for vegetables and fruits
□ Look for seaweed varieties
□ Spot small toppings (seeds, masago)
□ Identify sauces and dressings
□ Check for garnishes and herbs
□ Look for crispy toppings

Provide JSON analysis:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}

Take your time to be accurate.""",

            "concise_precise": """Analyze this poke bowl image. List ingredients from receipt and bowl separately, then compare.

JSON format only:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}

Be precise. Only include what you can clearly see or read."""
        }
    
    def encode_image(self, image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def test_prompt(self, image_path, prompt_name, prompt_text, expected_ingredients):
        """Test a specific prompt on an image"""
        print(f"\n🧪 Testing prompt: {prompt_name}")
        
        try:
            # Encode image
            image_b64 = self.encode_image(image_path)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a food quality assurance expert. Always respond with valid JSON."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                        ],
                    },
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                result = json.loads(content.strip())
                
                # Extract detected ingredients (combine receipt and bowl)
                receipt_ingredients = result.get('receipt_ingredients', [])
                bowl_ingredients = result.get('bowl_ingredients', [])
                detected_ingredients = list(set(receipt_ingredients + bowl_ingredients))
                
                # Calculate metrics
                metrics = self.calculate_metrics(expected_ingredients, detected_ingredients)
                
                print(f"✅ {prompt_name} - F1: {metrics['f1_score']:.1%}, Precision: {metrics['precision']:.1%}, Recall: {metrics['recall']:.1%}")
                
                return {
                    'prompt_name': prompt_name,
                    'success': True,
                    'receipt_ingredients': receipt_ingredients,
                    'bowl_ingredients': bowl_ingredients,
                    'detected_ingredients': detected_ingredients,
                    'missing_ingredients': result.get('missing_ingredients', []),
                    'extra_ingredients': result.get('extra_ingredients', []),
                    'model_match_percentage': result.get('match_percentage', 0),
                    'metrics': metrics
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ {prompt_name} - JSON parse error: {e}")
                return {
                    'prompt_name': prompt_name,
                    'success': False,
                    'error': f'JSON parse error: {e}',
                    'raw_response': content[:200]
                }
                
        except Exception as e:
            print(f"❌ {prompt_name} - API error: {e}")
            return {
                'prompt_name': prompt_name,
                'success': False,
                'error': f'API error: {e}'
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
    
    def test_all_prompts(self, image_path, expected_ingredients):
        """Test all prompts on a single image"""
        print(f"\n🚀 Testing all prompts on: {os.path.basename(image_path)}")
        print(f"📋 Expected: {len(expected_ingredients)} ingredients")
        
        results = {}
        
        for prompt_name, prompt_text in self.prompts.items():
            result = self.test_prompt(image_path, prompt_name, prompt_text, expected_ingredients)
            results[prompt_name] = result
        
        return results
    
    def generate_prompt_report(self, results, expected_ingredients):
        """Generate comprehensive prompt comparison report"""
        print(f"\n📊 PROMPT OPTIMIZATION REPORT")
        print("=" * 60)
        
        # Filter successful results
        successful_results = {k: v for k, v in results.items() if v.get('success', False)}
        failed_results = {k: v for k, v in results.items() if not v.get('success', False)}
        
        print(f"📈 Summary:")
        print(f"   Total prompts tested: {len(results)}")
        print(f"   Successful: {len(successful_results)}")
        print(f"   Failed: {len(failed_results)}")
        
        if failed_results:
            print(f"\n❌ Failed prompts:")
            for prompt_name, result in failed_results.items():
                print(f"   {prompt_name}: {result.get('error', 'Unknown error')}")
        
        if successful_results:
            # Sort by F1 score
            sorted_results = sorted(successful_results.items(), 
                                  key=lambda x: x[1]['metrics']['f1_score'], 
                                  reverse=True)
            
            print(f"\n🏆 PROMPT RANKING (by F1 Score):")
            print("-" * 60)
            
            for i, (prompt_name, result) in enumerate(sorted_results, 1):
                metrics = result['metrics']
                print(f"{i}. {prompt_name.upper()}:")
                print(f"   F1 Score: {metrics['f1_score']:.1%}")
                print(f"   Precision: {metrics['precision']:.1%}")
                print(f"   Recall: {metrics['recall']:.1%}")
                print(f"   True Positives: {len(metrics['true_positives'])}")
                print(f"   False Positives: {len(metrics['false_positives'])}")
                print(f"   False Negatives: {len(metrics['false_negatives'])}")
                print()
            
            # Show best prompt details
            best_prompt = sorted_results[0]
            print(f"🥇 BEST PROMPT: {best_prompt[0].upper()}")
            print("-" * 60)
            print(f"F1 Score: {best_prompt[1]['metrics']['f1_score']:.1%}")
            print(f"Precision: {best_prompt[1]['metrics']['precision']:.1%}")
            print(f"Recall: {best_prompt[1]['metrics']['recall']:.1%}")
            
            print(f"\n✅ True Positives: {best_prompt[1]['metrics']['true_positives']}")
            print(f"❌ False Positives: {best_prompt[1]['metrics']['false_positives']}")
            print(f"⚠️  False Negatives: {best_prompt[1]['metrics']['false_negatives']}")
            
            print(f"\n📋 Best Prompt Text:")
            print("-" * 60)
            print(self.prompts[best_prompt[0]])
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"prompt_optimization_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'results': results,
                'expected_ingredients': expected_ingredients,
                'best_prompt': sorted_results[0][0] if successful_results else None
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {report_file}")

def main():
    """Test all prompts on a specific image"""
    print("🤖 ChatGPT-4o Prompt Optimization Test")
    print("=" * 50)
    
    optimizer = PromptOptimizer()
    
    # Test on the challenging image we used before
    image_path = "Bowls/PHOTO-2025-07-21-11-44-48 2.jpg"
    expected_ingredients = [
        "Ahi Tuna",
        "Salmon", 
        "Cucumber",
        "Sliced Onions",
        "Cabbage",
        "Shredded Kale",
        "Mango",
        "Hijiki Seaweed",
        "Cilantro",
        "Serrano Peppers",
        "Surimi Salad",
        "Seaweed Salad",
        "Soft Tofu",
        "Wasabi",
        "Sesame Seeds",
        "Shredded Nori",
        "Garlic Crisps"
    ]
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Test all prompts
    results = optimizer.test_all_prompts(image_path, expected_ingredients)
    
    # Generate report
    optimizer.generate_prompt_report(results, expected_ingredients)

if __name__ == "__main__":
    main()
