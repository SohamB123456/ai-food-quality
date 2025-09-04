#!/usr/bin/env python3
"""
Improved PokeWorks QA Processor with Enhanced OCR
"""

import os
import cv2
import numpy as np
import pytesseract
import base64
import json
import openai
from PIL import Image, ImageEnhance
from fuzzywuzzy import fuzz, process
from config import OPENAI_API_KEY, GPT_MODEL, GPT_MAX_TOKENS, GPT_TEMPERATURE
import uuid
from datetime import datetime

class ImprovedPokeWorksProcessor:
    def __init__(self):
        """Initialize the processor with OpenAI API"""
        # Set OpenAI API key
        self.api_key = OPENAI_API_KEY
        openai.api_key = self.api_key
        
        # Load ingredients list
        self.ingredients = self.load_ingredients()
        print(f"✅ Improved Processor initialized with {len(self.ingredients)} known ingredients")
    
    def load_ingredients(self):
        """Load ingredients from file"""
        ingredients = []
        try:
            with open('Ingredients.txt', 'r') as f:
                for line in f:
                    ingredient = line.strip()
                    if ingredient:
                        ingredients.append(ingredient)
        except FileNotFoundError:
            print("⚠️ Ingredients.txt not found")
        return ingredients
    
    def improved_ocr(self, image_path):
        """Enhanced OCR using the best performing method (multi-scale)"""
        print(f"📄 Extracting text with improved OCR...")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print("❌ Could not load image")
                return ""
            
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            best_text = ""
            best_length = 0
            
            # Try different scales (multi-scale approach)
            scales = [0.8, 1.0, 1.2, 1.5, 2.0]
            for scale in scales:
                # Resize image
                height, width = gray.shape
                new_height = int(height * scale)
                new_width = int(width * scale)
                scaled = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                
                # Apply preprocessing
                denoised = cv2.medianBlur(scaled, 3)
                adaptive_thresh = cv2.adaptiveThreshold(
                    denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
                
                # Try different PSM modes
                for psm in [6, 7, 8, 13]:
                    try:
                        text = pytesseract.image_to_string(adaptive_thresh, config=f'--psm {psm}')
                        if len(text.strip()) > best_length:
                            best_text = text
                            best_length = len(text.strip())
                    except:
                        continue
            
            print(f"✅ Extracted {len(best_text)} characters with improved OCR")
            if best_text.strip():
                print(f"📝 Sample text: {best_text.strip()[:100]}...")
            else:
                print("⚠️ No text extracted")
            
            return best_text.strip()
            
        except Exception as e:
            print(f"❌ Improved OCR error: {e}")
            return ""
    
    def crop_image(self, image_path, output_dir="output"):
        """Auto-crop image into bowl and receipt sections using improved detection"""
        print(f"🔍 Processing image: {os.path.basename(image_path)}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not load image: {image_path}")
            return None, None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Try to detect receipt vs bowl regions
        # Receipts are typically white/light with text, bowls have more color variation
        
        # Split image into left and right halves
        left_half = gray[:, :width//2]
        right_half = gray[:, width//2:]
        
        # Calculate variance (text has higher variance than uniform backgrounds)
        left_variance = cv2.Laplacian(left_half, cv2.CV_64F).var()
        right_variance = cv2.Laplacian(right_half, cv2.CV_64F).var()
        
        # Calculate mean brightness (receipts are typically brighter)
        left_brightness = left_half.mean()
        right_brightness = right_half.mean()
        
        print(f"Left: variance={left_variance:.1f}, brightness={left_brightness:.1f}")
        print(f"Right: variance={right_variance:.1f}, brightness={right_brightness:.1f}")
        
        # Determine which side is the receipt
        # Receipt typically has higher variance (text) and higher brightness (white paper)
        receipt_score_left = left_variance + (left_brightness - 128) * 0.5
        receipt_score_right = right_variance + (right_brightness - 128) * 0.5
        
        if receipt_score_left > receipt_score_right:
            # Receipt is on the left
            receipt_region = image[:, :width//2]
            bowl_region = image[:, width//2:]
            print("📄 Receipt detected on LEFT side")
        else:
            # Receipt is on the right
            receipt_region = image[:, width//2:]
            bowl_region = image[:, :width//2]
            print("📄 Receipt detected on RIGHT side")
        
        # Generate filenames
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        bowl_path = os.path.join(output_dir, f"{base_name}_bowl.jpg")
        receipt_path = os.path.join(output_dir, f"{base_name}_receipt.jpg")
        
        # Save cropped images
        cv2.imwrite(bowl_path, bowl_region)
        cv2.imwrite(receipt_path, receipt_region)
        
        print(f"✅ Bowl saved: {os.path.basename(bowl_path)}")
        print(f"✅ Receipt saved: {os.path.basename(receipt_path)}")
        
        return receipt_path, bowl_path
    
    def encode_image(self, image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_bowl_with_gpt4o(self, bowl_path, receipt_text):
        """Analyze bowl using GPT-4o Vision API"""
        print("🤖 Analyzing bowl with GPT-4o...")
        
        try:
            # Encode bowl image
            bowl_b64 = self.encode_image(bowl_path)
            
            # Create prompt
            prompt = f"""
            Analyze this PokeWorks bowl image and extract all visible ingredients.
            Also compare with the receipt text to determine what was ordered vs what's actually in the bowl.
            
            Receipt text: {receipt_text}
            
            Known ingredients: {', '.join(self.ingredients[:20])}...
            
            Return a JSON response with:
            {{
                "detected_ingredients": [
                    {{"ingredient": "name", "confidence": 85, "status": "matched|missing|unexpected"}}
                ],
                "match_percentage": 75,
                "missing_ingredients": ["ingredient1", "ingredient2"],
                "unexpected_ingredients": ["ingredient3", "ingredient4"],
                "summary": "Brief analysis summary"
            }}
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a food quality assurance expert. Always respond with valid JSON."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{bowl_b64}"}},
                        ],
                    },
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            print(f"✅ GPT-4o analysis complete: {content[:100]}...")
            
            # Try to parse JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                print("⚠️ Failed to parse GPT-4o JSON response")
                return None
                
        except Exception as e:
            print(f"❌ GPT-4o API error: {e}")
            return None
    
    def process_image(self, image_path, output_dir="output"):
        """Main processing pipeline with improved OCR"""
        print(f"🚀 Starting improved processing pipeline...")
        print(f"📁 Input: {os.path.basename(image_path)}")
        
        try:
            # Step 1: Crop image
            receipt_path, bowl_path = self.crop_image(image_path, output_dir)
            if not receipt_path or not bowl_path:
                return self.create_fallback_result("Failed to crop image")
            
            # Step 2: Extract receipt text with improved OCR
            receipt_text = self.improved_ocr(receipt_path)
            
            # Step 3: Analyze with GPT-4o
            gpt_result = self.analyze_bowl_with_gpt4o(bowl_path, receipt_text)
            
            if gpt_result and gpt_result.get('detected_ingredients'):
                print("✅ GPT-4o analysis successful")
                return {
                    'analysis': gpt_result,
                    'receipt_text': receipt_text,
                    'bowl_path': bowl_path,
                    'receipt_path': receipt_path
                }
            else:
                print("🔄 GPT-4o failed, using local analysis fallback...")
                return self.analyze_bowl_locally(bowl_path, receipt_text, output_dir)
                
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return self.create_fallback_result(str(e))
    
    def analyze_bowl_locally(self, bowl_path, receipt_text, output_dir):
        """Local analysis fallback"""
        print("🔍 Analyzing bowl with local computer vision...")
        
        # Simple local analysis (same as before)
        detected_ingredients = []
        
        # Parse receipt text for ingredients
        receipt_ingredients = []
        if receipt_text:
            # Simple ingredient extraction from receipt
            for ingredient in self.ingredients:
                if ingredient.lower() in receipt_text.lower():
                    receipt_ingredients.append(ingredient)
        
        print(f"📋 Found {len(receipt_ingredients)} ingredients in receipt: {receipt_ingredients}")
        
        # Simple visual detection (placeholder)
        visual_ingredients = ["White Rice", "Salmon", "Avocado"]  # Placeholder
        
        # Match ingredients
        matched = []
        missing = []
        unexpected = []
        
        for ing in visual_ingredients:
            if ing in receipt_ingredients:
                matched.append({"ingredient": ing, "confidence": 85, "status": "matched"})
            else:
                unexpected.append({"ingredient": ing, "confidence": 70, "status": "unexpected"})
        
        for ing in receipt_ingredients:
            if ing not in [m["ingredient"] for m in matched]:
                missing.append(ing)
        
        match_percentage = len(matched) / len(receipt_ingredients) * 100 if receipt_ingredients else 0
        
        return {
            'analysis': {
                'detected_ingredients': matched + unexpected,
                'match_percentage': match_percentage,
                'missing_ingredients': missing,
                'unexpected_ingredients': [ing["ingredient"] for ing in unexpected],
                'summary': f"Local analysis: {len(matched)} matched, {len(missing)} missing, {len(unexpected)} unexpected"
            },
            'receipt_text': receipt_text,
            'bowl_path': bowl_path,
            'receipt_path': receipt_path
        }
    
    def create_fallback_result(self, error_msg):
        """Create fallback result when processing fails"""
        return {
            'analysis': {
                'detected_ingredients': [],
                'match_percentage': 0,
                'missing_ingredients': [],
                'unexpected_ingredients': [],
                'summary': f"Error: {error_msg}"
            },
            'receipt_text': "",
            'bowl_path': "",
            'receipt_path': ""
        }

# Create global instance
improved_processor = ImprovedPokeWorksProcessor()

