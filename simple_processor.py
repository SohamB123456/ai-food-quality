#!/usr/bin/env python3
"""
Simple ChatGPT-4o Processor - Direct Image Analysis
No OCR, no OpenCV preprocessing - just pure AI vision
"""

import os
import json
import base64
from openai import OpenAI
from config import OPENAI_API_KEY

class SimpleChatGPTProcessor:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.ingredients = self.load_ingredients()
    
    def load_ingredients(self):
        """Load known ingredients from file"""
        ingredients = []
        try:
            with open('Ingredients.txt', 'r') as f:
                ingredients = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ Loaded {len(ingredients)} known ingredients")
        except FileNotFoundError:
            print("⚠️ Ingredients.txt not found, using empty list")
        return ingredients
    
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
            
            # Optimized prompt based on our testing
            prompt = """You are analyzing a poke bowl for ingredient accuracy. Common poke bowl ingredients include:

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
    "match_percentage": 85,
    "summary": "Brief summary of the analysis"
}"""
            
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
                print(f"Raw response: {content[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ ChatGPT API error: {e}")
            return None
    
    def process_image(self, image_path, output_dir):
        """Process a single image and return results"""
        print(f"🔄 Processing image: {os.path.basename(image_path)}")
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return None
        
        # Analyze with ChatGPT
        analysis = self.analyze_with_chatgpt(image_path)
        
        if not analysis:
            print("❌ ChatGPT analysis failed")
            return self.create_error_result("ChatGPT analysis failed")
        
        # Extract data from ChatGPT response
        receipt_ingredients = analysis.get('receipt_ingredients', [])
        bowl_ingredients = analysis.get('bowl_ingredients', [])
        missing_ingredients = analysis.get('missing_ingredients', [])
        extra_ingredients = analysis.get('extra_ingredients', [])
        match_percentage = analysis.get('match_percentage', 0)
        summary = analysis.get('summary', 'Analysis completed')
        
        # Combine all detected ingredients
        all_detected = list(set(receipt_ingredients + bowl_ingredients))
        
        # Create detected ingredients list with status
        detected_ingredients = []
        
        # Add receipt ingredients
        for ingredient in receipt_ingredients:
            detected_ingredients.append({
                'ingredient': ingredient,
                'source': 'receipt',
                'confidence': 90,
                'status': 'matched'
            })
        
        # Add bowl ingredients
        for ingredient in bowl_ingredients:
            detected_ingredients.append({
                'ingredient': ingredient,
                'source': 'bowl',
                'confidence': 85,
                'status': 'matched'
            })
        
        # Add missing ingredients
        for ingredient in missing_ingredients:
            detected_ingredients.append({
                'ingredient': ingredient,
                'source': 'receipt',
                'confidence': 80,
                'status': 'missing'
            })
        
        # Add extra ingredients
        for ingredient in extra_ingredients:
            detected_ingredients.append({
                'ingredient': ingredient,
                'source': 'bowl',
                'confidence': 75,
                'status': 'unexpected'
            })
        
        # Create result structure
        result = {
            'analysis': {
                'detected_ingredients': detected_ingredients,
                'missing_ingredients': missing_ingredients,
                'unexpected_ingredients': extra_ingredients,
                'match_percentage': match_percentage,
                'summary': summary
            },
            'receipt_text': f"Receipt ingredients: {', '.join(receipt_ingredients)}",
            'bowl_path': image_path,
            'receipt_path': image_path  # Same image contains both
        }
        
        print(f"✅ Processing complete - {match_percentage}% match")
        return result
    
    def create_error_result(self, error_message):
        """Create error result structure"""
        return {
            'analysis': {
                'detected_ingredients': [],
                'missing_ingredients': [],
                'unexpected_ingredients': [],
                'match_percentage': 0,
                'summary': f"Error: {error_message}"
            },
            'receipt_text': f"Error: {error_message}",
            'bowl_path': '',
            'receipt_path': ''
        }
    
    def batch_process(self, input_dir, output_dir):
        """Batch process multiple images"""
        print(f"🔄 Batch processing images from {input_dir}")
        
        if not os.path.exists(input_dir):
            print(f"❌ Input directory not found: {input_dir}")
            return []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"📸 Found {len(image_files)} images to process")
        
        for i, filename in enumerate(image_files, 1):
            print(f"\n🔄 Processing {i}/{len(image_files)}: {filename}")
            
            image_path = os.path.join(input_dir, filename)
            result = self.process_image(image_path, output_dir)
            
            if result:
                result['filename'] = filename
                results.append(result)
            else:
                print(f"❌ Failed to process {filename}")
        
        print(f"✅ Batch processing complete: {len(results)}/{len(image_files)} successful")
        return results

# Create global instance
simple_processor = SimpleChatGPTProcessor()
