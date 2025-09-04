#!/usr/bin/env python3
"""
Test the improved prompt on multiple images
"""

import os
import sys
import json
import base64
from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY

def test_improved_prompt():
    """Test the improved prompt on different images"""
    
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # The best prompt from our optimization test, with improvements
    improved_prompt = """You are analyzing a poke bowl for ingredient accuracy. Common poke bowl ingredients include:

Proteins: Ahi Tuna, Salmon, Spicy Tuna, Spicy Salmon, Shrimp, Chicken, Tofu, Lobster Surimi
Bases: White Rice, Brown Rice, Salad Mix
Vegetables: Cucumber, Edamame, Cabbage, Shredded Kale, Sliced Onions, Sweet Corn
Fruits: Mango, Pineapple, Mandarin Oranges
Seaweed: Hijiki Seaweed, Seaweed Salad, Shredded Nori
Garnishes: Cilantro, Green Onion, Serrano Peppers, Pickled Ginger
Sauces: Ponzu Fresh, Sweet Shoyu, Spicy Furikake, Sriracha Aioli
Toppings: Sesame Seeds, Masago, Wasabi, Soft Tofu, Surimi Salad
Crisps: Wonton Crisps, Garlic Crisps, Onion Crisps, Chili Crisp

IMPORTANT: Only include ingredients you can clearly see or read. Be conservative - it's better to miss something than to guess.

Analyze the image and provide JSON:
{
    "receipt_ingredients": ["ingredient1", "ingredient2", ...],
    "bowl_ingredients": ["ingredient1", "ingredient2", ...],
    "missing_ingredients": ["ingredient1", "ingredient2", ...],
    "extra_ingredients": ["ingredient1", "ingredient2", ...],
    "match_percentage": 85
}"""
    
    # Test images with their expected ingredients
    test_cases = [
        {
            "image": "Bowls/PHOTO-2025-07-21-11-44-42.jpg",
            "expected": [
                "White Rice",
                "Salad Mix",
                "Spicy Salmon",
                "Sliced Onions",
                "Sweet Corn",
                "Mango",
                "Surimi Salad",
                "Seaweed Salad",
                "Green Onion",
                "Garlic Crisps"
            ]
        },
        {
            "image": "Bowls/PHOTO-2025-07-21-11-44-42 6.jpg",
            "expected": [
                "Brown Rice",
                "Salad Mix",
                "Lobster Surimi",
                "Cucumber",
                "Sliced Onions",
                "Edamame",
                "Avocado",
                "Surimi Salad",
                "Seaweed Salad",
                "Pickled Ginger",
                "Green Onion",
                "Soft Tofu",
                "Chili Crisp",
                "Garlic Crisps"
            ]
        },
        {
            "image": "Bowls/PHOTO-2025-07-21-11-44-48 2.jpg",
            "expected": [
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
        }
    ]
    
    def encode_image(image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def calculate_metrics(expected, detected):
        """Calculate precision, recall, and F1 score"""
        expected_set = set(expected)
        detected_set = set(detected)
        
        true_positives = expected_set.intersection(detected_set)
        false_positives = detected_set - expected_set
        false_negatives = expected_set - detected_set
        
        precision = len(true_positives) / len(detected_set) if detected_set else 0
        recall = len(true_positives) / len(expected_set) if expected_set else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': list(true_positives),
            'false_positives': list(false_positives),
            'false_negatives': list(false_negatives)
        }
    
    def test_image(image_path, expected_ingredients):
        """Test a single image with the improved prompt"""
        print(f"\n🧪 Testing: {os.path.basename(image_path)}")
        print(f"📋 Expected: {len(expected_ingredients)} ingredients")
        
        try:
            # Encode image
            image_b64 = encode_image(image_path)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a food quality assurance expert. Always respond with valid JSON."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": improved_prompt},
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
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                result = json.loads(content.strip())
                
                # Extract detected ingredients
                receipt_ingredients = result.get('receipt_ingredients', [])
                bowl_ingredients = result.get('bowl_ingredients', [])
                detected_ingredients = list(set(receipt_ingredients + bowl_ingredients))
                
                # Calculate metrics
                metrics = calculate_metrics(expected_ingredients, detected_ingredients)
                
                print(f"📊 Results:")
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
                    'filename': os.path.basename(image_path),
                    'expected_count': len(expected_ingredients),
                    'detected_count': len(detected_ingredients),
                    'metrics': metrics,
                    'receipt_ingredients': receipt_ingredients,
                    'bowl_ingredients': bowl_ingredients
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print(f"Raw response: {content[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ API error: {e}")
            return None
    
    # Test all images
    print("🤖 Testing Improved Prompt on Multiple Images")
    print("=" * 60)
    
    results = []
    for test_case in test_cases:
        if os.path.exists(test_case["image"]):
            result = test_image(test_case["image"], test_case["expected"])
            if result:
                results.append(result)
        else:
            print(f"⚠️ Image not found: {test_case['image']}")
    
    # Generate summary
    if results:
        print(f"\n📊 OVERALL PERFORMANCE SUMMARY")
        print("=" * 60)
        
        avg_precision = sum(r['metrics']['precision'] for r in results) / len(results)
        avg_recall = sum(r['metrics']['recall'] for r in results) / len(results)
        avg_f1 = sum(r['metrics']['f1_score'] for r in results) / len(results)
        
        print(f"Average Precision: {avg_precision:.1%}")
        print(f"Average Recall: {avg_recall:.1%}")
        print(f"Average F1 Score: {avg_f1:.1%}")
        
        # Find best and worst performers
        best = max(results, key=lambda x: x['metrics']['f1_score'])
        worst = min(results, key=lambda x: x['metrics']['f1_score'])
        
        print(f"\n🏆 Best Performance: {best['filename']} (F1: {best['metrics']['f1_score']:.1%})")
        print(f"⚠️  Worst Performance: {worst['filename']} (F1: {worst['metrics']['f1_score']:.1%})")

if __name__ == "__main__":
    test_improved_prompt()
