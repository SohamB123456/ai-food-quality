#!/usr/bin/env python3
"""
Batch Processing Module
Process multiple images in batch for bowl and receipt analysis
"""

import os
import json
import time
from datetime import datetime
import argparse
from pathlib import Path

# Import our processing modules
from auto_crop_detection import detect_bowl_receipt_split
from ocr_fuzzy_newimages import process_receipt_ocr
from clip_bowl_ingredient_check import analyze_bowl_ingredients

def process_single_image(image_path, output_dir, save_intermediates=True):
    """
    Process a single image through the complete pipeline
    
    Args:
        image_path (str): Path to the input image
        output_dir (str): Directory to save results
        save_intermediates (bool): Whether to save intermediate crops
    
    Returns:
        dict: Processing results
    """
    start_time = time.time()
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    print(f"\n🔄 Processing: {base_name}")
    print("=" * 50)
    
    results = {
        'filename': os.path.basename(image_path),
        'timestamp': datetime.now().isoformat(),
        'processing_time': 0,
        'success': False,
        'error': None,
        'bowl_analysis': None,
        'receipt_analysis': None,
        'match_results': None
    }
    
    try:
        # Step 1: Auto crop detection
        print("📸 Step 1: Auto crop detection...")
        bowl_crop, receipt_crop = detect_bowl_receipt_split(image_path, output_dir if save_intermediates else None)
        
        # Step 2: Receipt OCR processing
        print("📄 Step 2: Receipt OCR processing...")
        receipt_results = process_receipt_ocr(receipt_crop)
        results['receipt_analysis'] = receipt_results
        
        # Step 3: Bowl ingredient analysis
        print("🍣 Step 3: Bowl ingredient analysis...")
        bowl_results = analyze_bowl_ingredients(bowl_crop)
        results['bowl_analysis'] = bowl_results
        
        # Step 4: Match ingredients
        print("🔍 Step 4: Matching ingredients...")
        match_results = match_ingredients(receipt_results, bowl_results)
        results['match_results'] = match_results
        
        results['success'] = True
        print(f"✅ Processing completed successfully!")
        
    except Exception as e:
        results['error'] = str(e)
        print(f"❌ Error processing {base_name}: {e}")
    
    finally:
        results['processing_time'] = time.time() - start_time
        print(f"⏱️  Processing time: {results['processing_time']:.2f} seconds")
    
    return results

def match_ingredients(receipt_results, bowl_results):
    """
    Match ingredients between receipt and bowl analysis
    
    Args:
        receipt_results (dict): Receipt OCR results
        bowl_results (dict): Bowl analysis results
    
    Returns:
        dict: Matching results
    """
    from fuzzywuzzy import fuzz, process
    
    receipt_ingredients = receipt_results.get('ingredients', [])
    bowl_ingredients = bowl_results.get('detected_ingredients', [])
    
    matched = []
    missing = []
    unexpected = []
    
    # Match bowl ingredients with receipt
    for bowl_ingredient in bowl_ingredients:
        best_match = process.extractOne(bowl_ingredient, receipt_ingredients, scorer=fuzz.token_sort_ratio)
        if best_match and best_match[1] > 80:  # 80% similarity threshold
            matched.append({
                'bowl_ingredient': bowl_ingredient,
                'receipt_ingredient': best_match[0],
                'confidence': best_match[1]
            })
        else:
            unexpected.append(bowl_ingredient)
    
    # Find missing ingredients (on receipt but not in bowl)
    for receipt_ingredient in receipt_ingredients:
        if not any(m['receipt_ingredient'] == receipt_ingredient for m in matched):
            missing.append(receipt_ingredient)
    
    # Calculate match percentage
    total_expected = len(matched) + len(missing)
    match_percentage = (len(matched) / total_expected * 100) if total_expected > 0 else 0
    
    return {
        'matched_ingredients': matched,
        'missing_ingredients': missing,
        'unexpected_ingredients': unexpected,
        'match_percentage': round(match_percentage, 2),
        'total_expected': total_expected,
        'total_matched': len(matched)
    }

def batch_process_directory(input_dir, output_dir, save_intermediates=True):
    """
    Process all images in a directory
    
    Args:
        input_dir (str): Directory containing input images
        output_dir (str): Directory to save results
        save_intermediates (bool): Whether to save intermediate crops
    """
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    if not os.path.exists(input_dir):
        raise ValueError(f"Input directory does not exist: {input_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all image files
    image_files = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            image_files.append(os.path.join(input_dir, filename))
    
    if not image_files:
        print("❌ No image files found in input directory")
        return
    
    print(f"📁 Found {len(image_files)} images to process")
    print(f"📂 Input directory: {input_dir}")
    print(f"📂 Output directory: {output_dir}")
    
    # Process each image
    all_results = []
    successful_count = 0
    error_count = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n🔄 Processing image {i}/{len(image_files)}")
        
        try:
            results = process_single_image(image_path, output_dir, save_intermediates)
            all_results.append(results)
            
            if results['success']:
                successful_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            print(f"❌ Fatal error processing {image_path}: {e}")
            error_count += 1
    
    # Save batch results
    batch_results = {
        'batch_info': {
            'input_directory': input_dir,
            'output_directory': output_dir,
            'total_images': len(image_files),
            'successful': successful_count,
            'errors': error_count,
            'timestamp': datetime.now().isoformat()
        },
        'results': all_results
    }
    
    results_file = os.path.join(output_dir, f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_file, 'w') as f:
        json.dump(batch_results, f, indent=2)
    
    print(f"\n📊 Batch Processing Summary:")
    print(f"✅ Successful: {successful_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📄 Results saved to: {results_file}")

def main():
    parser = argparse.ArgumentParser(description='Batch process images for bowl and receipt analysis')
    parser.add_argument('input_dir', help='Directory containing input images')
    parser.add_argument('-o', '--output', default='batch_output', help='Output directory for results')
    parser.add_argument('--no-intermediates', action='store_true', help='Do not save intermediate crop images')
    
    args = parser.parse_args()
    
    save_intermediates = not args.no_intermediates
    
    try:
        batch_process_directory(args.input_dir, args.output, save_intermediates)
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")

if __name__ == "__main__":
    main()
