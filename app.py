from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import json
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import pytesseract
from fuzzywuzzy import fuzz, process
import base64
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load ingredients list
def load_ingredients():
    try:
        with open('Ingredients.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

INGREDIENTS = load_ingredients()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Process the image
        try:
            results = process_image(filepath)
            results['filename'] = filename
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def process_image(image_path):
    """Process the uploaded image to detect bowl and receipt"""
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not load image")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Simple image splitting (assuming bowl on left, receipt on right)
    height, width = gray.shape
    mid_point = width // 2
    
    # Split image
    bowl_region = gray[:, :mid_point]
    receipt_region = gray[:, mid_point:]
    
    # Process receipt with OCR
    receipt_text = extract_text(receipt_region)
    
    # Process bowl with ingredient detection
    bowl_ingredients = detect_ingredients(bowl_region)
    
    # Match ingredients
    matched, missing, unexpected = match_ingredients(receipt_text, bowl_ingredients)
    
    return {
        'receipt_text': receipt_text,
        'detected_ingredients': bowl_ingredients,
        'matched_ingredients': matched,
        'missing_ingredients': missing,
        'unexpected_ingredients': unexpected,
        'match_percentage': calculate_match_percentage(matched, missing, unexpected)
    }

def extract_text(image):
    """Extract text from image using OCR"""
    try:
        # Preprocess image for better OCR
        # Apply thresholding
        _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract text
        text = pytesseract.image_to_string(thresh)
        return text.strip()
    except Exception as e:
        print(f"OCR error: {e}")
        return ""

def detect_ingredients(image):
    """Detect ingredients in bowl image"""
    # This is a simplified version - in practice, you'd use more sophisticated
    # computer vision techniques or ML models
    ingredients = []
    
    # Simple edge detection
    edges = cv2.Canny(image, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # For now, return some placeholder ingredients
    # In a real implementation, you'd analyze the image more thoroughly
    ingredients = ["White Rice", "Salmon", "Avocado", "Cucumber"]
    
    return ingredients

def match_ingredients(receipt_text, detected_ingredients):
    """Match detected ingredients with receipt text using fuzzy matching"""
    matched = []
    missing = []
    unexpected = []
    
    # Extract ingredients from receipt text
    receipt_ingredients = []
    for ingredient in INGREDIENTS:
        if ingredient.lower() in receipt_text.lower():
            receipt_ingredients.append(ingredient)
    
    # Match detected ingredients with receipt
    for detected in detected_ingredients:
        best_match = process.extractOne(detected, receipt_ingredients, scorer=fuzz.token_sort_ratio)
        if best_match and best_match[1] > 80:  # 80% similarity threshold
            matched.append(detected)
        else:
            unexpected.append(detected)
    
    # Find missing ingredients
    for receipt_ingredient in receipt_ingredients:
        if not any(process.extractOne(receipt_ingredient, matched, scorer=fuzz.token_sort_ratio)[1] > 80 for _ in [None]):
            missing.append(receipt_ingredient)
    
    return matched, missing, unexpected

def calculate_match_percentage(matched, missing, unexpected):
    """Calculate overall match percentage"""
    total_expected = len(matched) + len(missing)
    if total_expected == 0:
        return 0
    
    return round((len(matched) / total_expected) * 100, 2)

@app.route('/results/<filename>')
def results(filename):
    return render_template('results.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
