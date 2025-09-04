#!/usr/bin/env python3
"""
Advanced PokeWorks QA Processor
Integrates GPT-4o Vision API, OCR, and image processing
"""

import os
import cv2
import numpy as np
import pytesseract
import base64
import json
import openai
from PIL import Image
from fuzzywuzzy import fuzz, process
from config import OPENAI_API_KEY, GPT_MODEL, GPT_MAX_TOKENS, GPT_TEMPERATURE
import uuid
from datetime import datetime

class PokeWorksProcessor:
    def __init__(self):
        """Initialize the processor with OpenAI API"""
        # Set OpenAI API key
        self.api_key = OPENAI_API_KEY
        openai.api_key = self.api_key
        
        # Load ingredients list
        self.ingredients = self.load_ingredients()
        
        print(f"✅ Processor initialized with {len(self.ingredients)} known ingredients")
    
    def load_ingredients(self):
        """Load ingredients from file"""
        try:
            with open('Ingredients.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []
    
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
    
    def extract_receipt_text(self, receipt_path):
        """Extract text from receipt using improved multi-scale OCR"""
        print(f"📄 Extracting text from receipt with improved OCR...")

        try:
            # Load image
            image = cv2.imread(receipt_path)
            if image is None:
                print("❌ Could not load receipt image")
                return ""

            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            best_text = ""
            best_length = 0

            # Multi-scale OCR approach (best performing method)
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

            text = best_text

            print(f"✅ Extracted {len(text)} characters with improved OCR")
            if text.strip():
                print(f"📝 Sample text: {text.strip()[:100]}...")
            else:
                print("⚠️ No text extracted from receipt")

            return text.strip()

        except Exception as e:
            print(f"❌ Improved OCR error: {e}")
            return ""
    
    def encode_image(self, image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def analyze_bowl_with_gpt4o(self, bowl_path, receipt_text):
        """Analyze bowl contents using GPT-4o Vision API"""
        print(f"🤖 Analyzing bowl with GPT-4o...")
        
        try:
            # Encode bowl image
            bowl_b64 = self.encode_image(bowl_path)
            
            # Create prompt
            prompt = f"""
            You are a food quality assurance expert analyzing a poke bowl. 
            
            The receipt shows these ingredients were ordered:
            {receipt_text}
            
            Please analyze the bowl image and:
            1. Identify all visible ingredients
            2. Match them against the receipt ingredients
            3. Note any missing or extra ingredients
            4. Provide confidence scores (0-100%) for each ingredient
            5. Calculate an overall match percentage
            
            Return your analysis in this JSON format:
            {{
                "detected_ingredients": [
                    {{
                        "ingredient": "Salmon",
                        "confidence": 95.5,
                        "from_receipt": true,
                        "status": "matched"
                    }},
                    {{
                        "ingredient": "Extra Spice",
                        "confidence": 75.0,
                        "from_receipt": false,
                        "status": "unexpected"
                    }}
                ],
                "summary": "Bowl contains fresh salmon, avocado, and rice as ordered, plus some extra spice.",
                "match_percentage": 92.5,
                "missing_ingredients": ["Cucumber"],
                "unexpected_ingredients": ["Extra Spice"]
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
            content = response['choices'][0]['message']['content']
            
            # Try to extract JSON from response
            try:
                # Find JSON in response
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                result = json.loads(json_str)
                
                print(f"✅ GPT-4o analysis complete: {result.get('match_percentage', 0)}% match")
                return result
                
            except json.JSONDecodeError:
                print("⚠️ Could not parse JSON from GPT-4o response")
                return self.create_fallback_result(content)
                
        except Exception as e:
            print(f"❌ GPT-4o API error: {e}")
            return self.create_fallback_result(f"API Error: {e}")
    
    def create_fallback_result(self, content):
        """Create fallback result when API fails - use local analysis"""
        print("🔄 Using local analysis fallback...")
        
        # Try to analyze using local methods
        try:
            # This will be populated by the calling function
            return {
                "detected_ingredients": [],
                "summary": "Local analysis in progress...",
                "match_percentage": 0,
                "missing_ingredients": [],
                "unexpected_ingredients": []
            }
        except Exception as e:
            return {
                "detected_ingredients": [
                    {
                        "ingredient": "Analysis Failed",
                        "confidence": 0,
                        "from_receipt": False,
                        "status": "error"
                    }
                ],
                "summary": f"Could not analyze bowl: {content[:100]}...",
                "match_percentage": 0,
                "missing_ingredients": [],
                "unexpected_ingredients": ["Analysis Failed"]
            }
    
    def analyze_bowl_locally(self, bowl_path, receipt_text):
        """Analyze bowl using local computer vision and fuzzy matching"""
        print("🔍 Analyzing bowl with local computer vision...")
        
        try:
            # Load bowl image
            bowl_image = cv2.imread(bowl_path)
            if bowl_image is None:
                return self.create_fallback_result("Could not load bowl image")
            
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(bowl_image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(bowl_image, cv2.COLOR_BGR2LAB)
            
            # Detect different colored regions (ingredients)
            detected_ingredients = []
            
            # Color-based ingredient detection
            color_ranges = {
                       "Salmon": ([0, 50, 50], [20, 255, 255]),  # Orange-red
                       "Tuna": ([0, 50, 50], [20, 255, 255]),    # Red
                       "Avocado": ([35, 50, 50], [85, 255, 255]), # Green
                       "Cucumber": ([35, 50, 50], [85, 255, 255]), # Green
                       "Seaweed": ([35, 50, 50], [85, 255, 255]), # Green
                       "Cilantro": ([35, 50, 50], [85, 255, 255]), # Green
                       "Green Onion": ([35, 50, 50], [85, 255, 255]), # Green
                       "Sweet Corn": ([15, 100, 100], [35, 255, 255]), # Yellow
                       "Rice": ([0, 0, 200], [180, 30, 255]),     # White
                       "Sesame": ([0, 0, 200], [180, 30, 255]),   # White/Black
                       "Garlic Crisps": ([0, 0, 150], [30, 50, 255]), # Light brown
                       "Onion Crisps": ([0, 0, 150], [30, 50, 255]), # Light brown
                       "Masago": ([15, 100, 100], [35, 255, 255]), # Orange
                       "Surimi Salad": ([0, 0, 200], [180, 30, 255]), # White/Pink
                       "Wasabi": ([35, 50, 50], [85, 255, 255]), # Green
                       "Shredded Nori": ([0, 0, 0], [180, 255, 50]), # Dark/Black
                   }
            
            for ingredient, (lower, upper) in color_ranges.items():
                # Create mask for this color range
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                
                # Count pixels in this color range
                pixel_count = cv2.countNonZero(mask)
                total_pixels = bowl_image.shape[0] * bowl_image.shape[1]
                percentage = (pixel_count / total_pixels) * 100
                
                # If significant amount of this color is present
                if percentage > 2:  # At least 2% of image
                    confidence = min(percentage * 10, 95)  # Scale to confidence
                    detected_ingredients.append({
                        "ingredient": ingredient,
                        "confidence": round(confidence, 1),
                        "from_receipt": False,
                        "status": "detected"
                    })
            
            # Extract ingredients from receipt text (improved parsing)
            receipt_ingredients = []
            
            # Clean up the receipt text
            cleaned_text = receipt_text.lower()
            
            # Common ingredient variations in receipts (including OCR error patterns)
            ingredient_variations = {
                       "white rice": ["rice", "white", "wr", "ri", "re", "ris"],
                       "brown rice": ["brown", "br"],
                       "ahi tuna": ["ahi", "tuna", "fish", "ahi", "tun"],
                       "salmon": ["salmon", "fish", "sal", "salm", "spicy salmon"],
                       "spicy salmon": ["spicy", "salmon", "spicy salmon"],
                       "avocado": ["avocado", "avo", "avoc"],
                       "cucumber": ["cucumber", "cuke", "cuc"],
                       "cabbage": ["cabbage", "cab", "cabb"],
                       "edamame": ["edamame", "beans", "edam", "edamame"],
                       "mango": ["mango", "fruit", "mang"],
                       "sweet corn": ["corn", "sweet", "sweet corn"],
                       "cilantro": ["cilantro", "coriander", "cil"],
                       "green onion": ["green onion", "scallion", "spring onion", "green", "onion"],
                       "garlic crisps": ["garlic", "crisps", "garlic crisps", "fried garlic"],
                       "onion crisps": ["onion", "crisps", "onion crisps", "fried onion"],
                       "seaweed salad": ["seaweed", "salad", "wakame", "sea", "weed", "hijiki seaweed"],
                       "hijiki seaweed": ["hijiki", "seaweed", "hijiki seaweed"],
                       "surimi salad": ["surimi", "salad", "crab", "surimi salad"],
                       "masago": ["masago", "fish roe", "roe", "masago"],
                       "wasabi": ["wasabi", "wasabi"],
                       "shredded nori": ["nori", "shredded", "shredded nori", "seaweed"],
                       "spicy furikake": ["furikake", "spicy", "spicy furikake"],
                       "extra chili crisp": ["chili", "crisp", "extra", "extra chili crisp"],
                       "sesame seeds": ["sesame", "seeds", "ses", "seem"],
                       "pokeworks classic": ["classic", "sauce", "pokeworks", "poke", "pokeworks classic"],
                       "shoyu sauce": ["shoyu", "soy", "sauce", "shoyu sauce"],
                       "medium flavor": ["medium", "flavor", "med"],
                       "heavy flavor": ["heavy", "flavor", "heavy flavor"]
                   }
            
            # OCR error patterns - common misreadings
            ocr_patterns = {
                "salmon": ["salm", "sal", "salmn", "salmon"],
                "tuna": ["tun", "tun", "tuna", "tun"],
                "rice": ["ri", "ris", "rice", "re", "ris"],
                "avocado": ["avoc", "avo", "avocado"],
                "cucumber": ["cuc", "cuke", "cucumber"],
                "cabbage": ["cab", "cabb", "cabbage"],
                "edamame": ["edam", "edamame", "beans"],
                "mango": ["mang", "mango", "fruit"],
                "seaweed": ["sea", "weed", "seaweed"],
                "sesame": ["ses", "seem", "sesame"]
            }
            
            # Look for ingredients in the receipt text
            for ingredient in self.ingredients:
                ingredient_lower = ingredient.lower()
                found = False
                
                # Direct match
                if ingredient_lower in cleaned_text:
                    receipt_ingredients.append(ingredient)
                    found = True
                # Check variations
                elif ingredient_lower in ingredient_variations:
                    for variation in ingredient_variations[ingredient_lower]:
                        if variation in cleaned_text:
                            receipt_ingredients.append(ingredient)
                            found = True
                            break
                
                # Check OCR error patterns
                if not found and ingredient_lower in ocr_patterns:
                    for pattern in ocr_patterns[ingredient_lower]:
                        if pattern in cleaned_text:
                            receipt_ingredients.append(ingredient)
                            found = True
                            break
                
                # Fuzzy match for OCR errors (more aggressive)
                if not found:
                    words = cleaned_text.split()
                    for word in words:
                        if len(word) > 2:  # Check words longer than 2 characters
                            score = fuzz.ratio(ingredient_lower, word)
                            if score > 70:  # Lower threshold for OCR errors
                                receipt_ingredients.append(ingredient)
                                found = True
                                break
                
                # Also check partial matches in the text
                if not found:
                    for word in cleaned_text.split():
                        if len(word) > 3 and ingredient_lower[:4] in word:
                            receipt_ingredients.append(ingredient)
                            found = True
                            break
            
            print(f"📋 Found {len(receipt_ingredients)} ingredients in receipt: {receipt_ingredients}")
            
            # Match detected ingredients with receipt
            matched = []
            missing = []
            unexpected = []
            
            # Remove duplicates from receipt ingredients
            receipt_ingredients = list(set(receipt_ingredients))
            
            for detected in detected_ingredients:
                # Find best match in receipt ingredients
                best_match = None
                best_score = 0
                
                for receipt_ingredient in receipt_ingredients:
                    # Check for direct matches first
                    if detected["ingredient"].lower() in receipt_ingredient.lower() or receipt_ingredient.lower() in detected["ingredient"].lower():
                        best_match = receipt_ingredient
                        best_score = 100
                        break
                    # Then check fuzzy matches
                    score = fuzz.token_sort_ratio(detected["ingredient"].lower(), receipt_ingredient.lower())
                    if score > best_score and score > 60:  # Lower threshold for better matching
                        best_score = score
                        best_match = receipt_ingredient
                
                if best_match:
                    detected["from_receipt"] = True
                    detected["status"] = "matched"
                    detected["ingredient"] = best_match  # Use receipt name
                    matched.append(detected)
                    # Remove from receipt ingredients to avoid double matching
                    if best_match in receipt_ingredients:
                        receipt_ingredients.remove(best_match)
                else:
                    detected["status"] = "unexpected"
                    unexpected.append(detected)
            
            # Remaining receipt ingredients are missing
            missing = receipt_ingredients
            
            # Calculate match percentage
            total_expected = len(matched) + len(missing)
            match_percentage = (len(matched) / total_expected * 100) if total_expected > 0 else 0
            
            # Create summary
            summary_parts = []
            if matched:
                summary_parts.append(f"Found {len(matched)} matching ingredients")
            if missing:
                summary_parts.append(f"{len(missing)} ingredients missing")
            if unexpected:
                summary_parts.append(f"{len(unexpected)} unexpected ingredients")
            
            summary = "Local analysis: " + ", ".join(summary_parts) if summary_parts else "No clear ingredients detected"
            
            return {
                "detected_ingredients": detected_ingredients,
                "summary": summary,
                "match_percentage": round(match_percentage, 1),
                "missing_ingredients": missing,
                "unexpected_ingredients": [ing["ingredient"] for ing in unexpected]
            }
            
        except Exception as e:
            print(f"❌ Local analysis error: {e}")
            return self.create_fallback_result(f"Local analysis failed: {e}")
    
    def process_image(self, image_path, output_dir="output"):
        """Complete processing pipeline"""
        print(f"\n🚀 Starting complete processing pipeline...")
        print(f"📁 Input: {os.path.basename(image_path)}")
        
        # Step 1: Crop image
        receipt_path, bowl_path = self.crop_image(image_path, output_dir)
        if not receipt_path or not bowl_path:
            return None
        
        # Step 2: Extract receipt text
        receipt_text = self.extract_receipt_text(receipt_path)
        
        # Step 3: Analyze bowl with GPT-4o (fallback to local analysis)
        analysis = self.analyze_bowl_with_gpt4o(bowl_path, receipt_text)
        
        # If API failed, use local analysis
        if (analysis.get('match_percentage') == 0 and 
            (not analysis.get('detected_ingredients') or 
             any("Analysis Failed" in str(ing) for ing in analysis.get('detected_ingredients', [])))):
            print("🔄 API failed, switching to local computer vision analysis...")
            analysis = self.analyze_bowl_locally(bowl_path, receipt_text)
        
        # Step 4: Prepare results
        results = {
            "receipt_text": receipt_text,
            "bowl_path": bowl_path,
            "receipt_path": receipt_path,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "filename": os.path.basename(image_path)
        }
        
        print(f"✅ Processing complete!")
        return results
    
    def batch_process(self, input_dir, output_dir="batch_output"):
        """Process multiple images in batch"""
        print(f"📦 Starting batch processing...")
        print(f"📁 Input directory: {input_dir}")
        print(f"📁 Output directory: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        
        for file in os.listdir(input_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(input_dir, file))
        
        print(f"📊 Found {len(image_files)} images to process")
        
        results = []
        for i, image_path in enumerate(image_files, 1):
            print(f"\n🔄 Processing {i}/{len(image_files)}: {os.path.basename(image_path)}")
            
            try:
                result = self.process_image(image_path, output_dir)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"❌ Error processing {image_path}: {e}")
        
        # Save batch results
        results_file = os.path.join(output_dir, "batch_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Batch processing complete!")
        print(f"📊 Processed {len(results)}/{len(image_files)} images successfully")
        print(f"💾 Results saved to: {results_file}")
        
        return results

# Create global processor instance
processor = PokeWorksProcessor()
