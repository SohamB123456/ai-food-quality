#!/usr/bin/env python3
"""
Test a specific image with GPT-4o
"""

import os
import sys
import json
import base64
from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY

def test_specific_image(image_path, expected_ingredients):
    """Test a specific image with GPT-4o"""
    
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    print(f"🧪 Testing: {os.path.basename(image_path)}")
    print(f"📋 Expected: {len(expected_ingredients)} ingredients")
    for i, ing in enumerate(expected_ingredients, 1):
        print(f"  {i:2d}. {ing}")
    
    def encode_image(image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_with_chatgpt(image_path):
        """Analyze image directly with ChatGPT-4o"""
        print(f"\n🤖 Analyzing with ChatGPT-4o: {os.path.basename(image_path)}")
        
        try:
            # Encode image
            image_b64 = encode_image(image_path)
            
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
            response = client.chat.completions.create(
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
    
    # Analyze with ChatGPT
    result = analyze_with_chatgpt(image_path)
    
    if not result:
        print("❌ Analysis failed")
        return
    
    # Extract detected ingredients (combine receipt and bowl)
    receipt_ingredients = result.get('receipt_ingredients', [])
    bowl_ingredients = result.get('bowl_ingredients', [])
    detected_ingredients = list(set(receipt_ingredients + bowl_ingredients))
    
    # Calculate metrics
    metrics = calculate_metrics(expected_ingredients, detected_ingredients)
    
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
    
    print(f"\n📋 Detailed Analysis:")
    print(f"  Receipt ingredients found: {receipt_ingredients}")
    print(f"  Bowl ingredients found: {bowl_ingredients}")
    print(f"  Missing ingredients: {result.get('missing_ingredients', [])}")
    print(f"  Extra ingredients: {result.get('extra_ingredients', [])}")
    print(f"  Model match percentage: {result.get('match_percentage', 0)}%")

def main():
    """Test the specific image"""
    print("🤖 Testing Specific Image with GPT-4o")
    print("=" * 50)
    
    # The image that's available (closest to your description)
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
    
    # Test the image
    test_specific_image(image_path, expected_ingredients)

if __name__ == "__main__":
    main()