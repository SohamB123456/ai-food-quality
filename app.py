from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import json
from datetime import datetime
import sys

# Add current directory to path
sys.path.append('.')

# Import our advanced processor
from simple_processor import simple_processor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Demo navigation page showing all available interfaces"""
    return render_template('demo.html')

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
        
        # Process the image using simple ChatGPT processor
        try:
            results = simple_processor.process_image(filepath, app.config['UPLOAD_FOLDER'])
            if results:
                results['filename'] = filename
                return jsonify(results)
            else:
                return jsonify({'error': 'Failed to process image'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Old processing functions removed - now using advanced processor

@app.route('/splash')
def splash():
    """Splash screen for mobile app demo"""
    return render_template('splash.html')

@app.route('/split-preview')
def split_preview():
    """Split preview screen for mobile app demo"""
    return render_template('split-preview.html')

@app.route('/detail-overlay')
def detail_overlay():
    """Detail overlay screen for mobile app demo"""
    return render_template('detail-overlay.html')

@app.route('/batch-process')
def batch_process_page():
    """Batch processing page"""
    return render_template('batch_process.html')

@app.route('/api/batch-process', methods=['POST'])
def batch_process_api():
    """API endpoint for batch processing"""
    try:
        input_dir = request.json.get('input_dir', 'newImages')
        output_dir = request.json.get('output_dir', 'batch_output')
        
        results = simple_processor.batch_process(input_dir, output_dir)
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/mobile-results/<filename>')
def mobile_results(filename):
    """Enhanced mobile results screen"""
    # Process the uploaded image to get results
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Process the image using simple ChatGPT processor
        results_data = simple_processor.process_image(filepath, app.config['UPLOAD_FOLDER'])
        
        if not results_data:
            raise Exception("Failed to process image")
        
        # Extract analysis data
        analysis = results_data.get('analysis', {})
        detected_ingredients = analysis.get('detected_ingredients', [])
        
        # Separate ingredients by status
        matched = [ing for ing in detected_ingredients if ing.get('status') == 'matched']
        missing = analysis.get('missing_ingredients', [])
        unexpected = analysis.get('unexpected_ingredients', [])
        
        return render_template('results.html', 
                             filename=filename,
                             match_percentage=analysis.get('match_percentage', 0),
                             matched_ingredients=matched,
                             missing_ingredients=missing,
                             unexpected_ingredients=unexpected,
                             receipt_text=results_data.get('receipt_text', ''),
                             detected_ingredients=detected_ingredients,
                             summary=analysis.get('summary', ''),
                             bowl_path=results_data.get('bowl_path', ''),
                             receipt_path=results_data.get('receipt_path', ''))
    except Exception as e:
        return render_template('results.html', 
                             filename=filename,
                             match_percentage=0,
                             matched_ingredients=[],
                             missing_ingredients=[],
                             unexpected_ingredients=[],
                             receipt_text="Error processing image",
                             detected_ingredients=[],
                             summary=f"Error: {str(e)}",
                             bowl_path="",
                             receipt_path="",
                             error=str(e))

@app.route('/results/<filename>')
def results(filename):
    # Process the uploaded image to get results
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Process the image using simple ChatGPT processor
        results_data = simple_processor.process_image(filepath, app.config['UPLOAD_FOLDER'])
        
        if not results_data:
            raise Exception("Failed to process image")
        
        # Extract analysis data
        analysis = results_data.get('analysis', {})
        detected_ingredients = analysis.get('detected_ingredients', [])
        
        # Separate ingredients by status
        matched = [ing for ing in detected_ingredients if ing.get('status') == 'matched']
        missing = analysis.get('missing_ingredients', [])
        unexpected = analysis.get('unexpected_ingredients', [])
        
        return render_template('results.html', 
                             filename=filename,
                             match_percentage=analysis.get('match_percentage', 0),
                             matched_ingredients=matched,
                             missing_ingredients=missing,
                             unexpected_ingredients=unexpected,
                             receipt_text=results_data.get('receipt_text', ''),
                             detected_ingredients=detected_ingredients,
                             summary=analysis.get('summary', ''),
                             bowl_path=results_data.get('bowl_path', ''),
                             receipt_path=results_data.get('receipt_path', ''))
    except Exception as e:
        return render_template('results.html', 
                             filename=filename,
                             match_percentage=0,
                             matched_ingredients=[],
                             missing_ingredients=[],
                             unexpected_ingredients=[],
                             receipt_text="Error processing image",
                             detected_ingredients=[],
                             summary=f"Error: {str(e)}",
                             bowl_path="",
                             receipt_path="",
                             error=str(e))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
