#!/usr/bin/env python3
"""
Simple Web Interface for Poke Bowl Receipt Analyzer
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
sys.path.append('.')

from app import processor

app = Flask(__name__)

@app.route('/')
def index():
    """Simple upload page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🍜 Poke Bowl Analyzer</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 20px; background-color: #f8f9fa; }
            .upload-area { border: 2px dashed #dee2e6; border-radius: 10px; padding: 40px; text-align: center; }
            .upload-area:hover { border-color: #007bff; }
            .result-box { background: white; border-radius: 10px; padding: 20px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mb-4">🍜 Poke Bowl Receipt Analyzer</h1>
            
            <div class="upload-area" id="uploadArea">
                <h4>📷 Upload Your Image</h4>
                <p class="text-muted">Drag and drop or click to select an image</p>
                <input type="file" id="imageInput" accept="image/*" style="display: none;">
                <button class="btn btn-primary" onclick="document.getElementById('imageInput').click()">
                    Choose Image
                </button>
            </div>
            
            <div id="loading" style="display: none;" class="text-center mt-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Analyzing your image...</p>
            </div>
            
            <div id="results" style="display: none;" class="result-box">
                <h4>📊 Analysis Results</h4>
                <div id="ingredientsList"></div>
                <div id="bowlAnalysis"></div>
            </div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const imageInput = document.getElementById('imageInput');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = '#007bff';
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.borderColor = '#dee2e6';
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = '#dee2e6';
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFile(files[0]);
                }
            });
            
            imageInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });
            
            function handleFile(file) {
                if (!file.type.startsWith('image/')) {
                    alert('Please select an image file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('image', file);
                
                loading.style.display = 'block';
                results.style.display = 'none';
                
                fetch('/analyze', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    results.style.display = 'block';
                    
                    // Display ingredients
                    const ingredientsList = document.getElementById('ingredientsList');
                    if (data.ingredients && data.ingredients.length > 0) {
                        ingredientsList.innerHTML = `
                            <h5>✅ Found ${data.ingredients.length} ingredients:</h5>
                            <ul class="list-group list-group-flush">
                                ${data.ingredients.map(ing => `<li class="list-group-item">${ing}</li>`).join('')}
                            </ul>
                        `;
                    } else {
                        ingredientsList.innerHTML = '<p class="text-warning">❌ No ingredients found</p>';
                    }
                    
                    // Display bowl analysis
                    const bowlAnalysis = document.getElementById('bowlAnalysis');
                    if (data.bowl_analysis && data.bowl_analysis.match_percentage) {
                        bowlAnalysis.innerHTML = `
                            <h5 class="mt-3">🍽️ Bowl Analysis:</h5>
                            <p><strong>Match Percentage:</strong> ${data.bowl_analysis.match_percentage.toFixed(1)}%</p>
                        `;
                    } else {
                        bowlAnalysis.innerHTML = '<p class="text-muted mt-3">⚠️ Bowl analysis not available</p>';
                    }
                })
                .catch(error => {
                    loading.style.display = 'none';
                    alert('Error analyzing image: ' + error.message);
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, file.filename)
        file.save(filepath)
        
        # Process the image
        receipt_path, bowl_path = processor.crop_image(filepath, upload_dir)
        
        if not receipt_path or not bowl_path:
            return jsonify({'error': 'Failed to crop image'}), 400
        
        # Extract text and ingredients
        receipt_text = processor.extract_text_from_receipt(receipt_path)
        ingredients = processor.extract_ingredients_from_receipt(receipt_text)
        
        # Try bowl analysis
        bowl_analysis = None
        try:
            bowl_analysis = processor.detect_ingredients_in_bowl(bowl_path, ingredients)
        except Exception as e:
            print(f"Bowl analysis failed: {e}")
        
        return jsonify({
            'ingredients': ingredients,
            'bowl_analysis': bowl_analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Starting Simple Web Interface...")
    print("📱 Open your browser to: http://localhost:5001")
    print("💡 Upload an image to test the analyzer!")
    app.run(host='0.0.0.0', port=5001, debug=True) 