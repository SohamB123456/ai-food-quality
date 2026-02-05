#!/usr/bin/env python3
"""
Auto Crop Detection Module
Automatically detects and crops bowl and receipt regions from combined images
"""

import cv2
import numpy as np
from PIL import Image
import os
import argparse

def detect_bowl_receipt_split(image_path, output_dir=None):

    print(f"Processing image: {os.path.basename(image_path)}")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    height, width = image.shape[:2]
    print(f"Image dimensions: {width}x{height}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Vertical split (middle)
    mid_point = width // 2
    bowl_region = image[:, :mid_point]
    receipt_region = image[:, mid_point:]
    
    # Edge detection 
    edges = cv2.Canny(gray, 50, 150)
    
    # Find vertical lines that might indicate a split
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
    vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, vertical_kernel)
    
    # Find contours of vertical lines
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Look for a vertical line near the middle
    best_split = mid_point
    min_distance = float('inf')
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Check if this is a vertical line in the middle region
        if w < 20 and h > height * 0.3 and abs(x - mid_point) < width * 0.2:
            distance = abs(x - mid_point)
            if distance < min_distance:
                min_distance = distance
                best_split = x
    
    print(f"Detected split at x={best_split} (original middle: {mid_point})")
    
    # Crop using the detected split
    bowl_crop = image[:, :best_split]
    receipt_crop = image[:, best_split:]
    
    # Save crops if output directory specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        bowl_path = os.path.join(output_dir, f"{base_name}_bowl.jpg")
        receipt_path = os.path.join(output_dir, f"{base_name}_receipt.jpg")
        
        cv2.imwrite(bowl_path, bowl_crop)
        cv2.imwrite(receipt_path, receipt_crop)
    
    return bowl_crop, receipt_crop

def batch_process_images(input_dir, output_dir):
   
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    if not os.path.exists(input_dir):
        raise ValueError(f"Input directory does not exist: {input_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    processed_count = 0
    error_count = 0
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)
            
            try:
                detect_bowl_receipt_split(input_path, output_dir)
                processed_count += 1
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
                error_count += 1
    
    print(f"\nProcessing complete!")
    print(f"Processed: {processed_count} images")
    print(f"Errors: {error_count} images")

def main():
    parser = argparse.ArgumentParser(description='Auto crop bowl and receipt from combined images')
    parser.add_argument('input', help='Input image path or directory')
    parser.add_argument('-o', '--output', help='Output directory for cropped images')
    parser.add_argument('--batch', action='store_true', help='Process all images in input directory')
    
    args = parser.parse_args()
    
    if args.batch:
        batch_process_images(args.input, args.output or 'cropped_output')
    else:
        detect_bowl_receipt_split(args.input, args.output)

if __name__ == "__main__":
    main()
