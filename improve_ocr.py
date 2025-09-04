#!/usr/bin/env python3
"""
OCR Improvement System for PokeWorks QA
Tests different OCR methods and preprocessing techniques
"""

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
# import matplotlib.pyplot as plt  # Not needed for this test

class OCRImprover:
    def __init__(self):
        self.methods = {
            'original': self.original_ocr,
            'denoised': self.denoised_ocr,
            'adaptive_thresh': self.adaptive_threshold_ocr,
            'morphology': self.morphology_ocr,
            'enhanced': self.enhanced_ocr,
            'multi_scale': self.multi_scale_ocr,
            'edge_based': self.edge_based_ocr,
            'color_separation': self.color_separation_ocr
        }
    
    def original_ocr(self, image):
        """Original OCR method"""
        return pytesseract.image_to_string(image, config='--psm 6')
    
    def denoised_ocr(self, image):
        """OCR with denoising"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply denoising
        denoised = cv2.medianBlur(gray, 5)
        denoised = cv2.bilateralFilter(denoised, 9, 75, 75)
        
        return pytesseract.image_to_string(denoised, config='--psm 6')
    
    def adaptive_threshold_ocr(self, image):
        """OCR with adaptive thresholding"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply adaptive threshold
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return pytesseract.image_to_string(adaptive_thresh, config='--psm 6')
    
    def morphology_ocr(self, image):
        """OCR with morphological operations"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply morphological operations
        kernel = np.ones((2,2), np.uint8)
        processed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        # Apply threshold
        _, thresh = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return pytesseract.image_to_string(thresh, config='--psm 6')
    
    def enhanced_ocr(self, image):
        """OCR with PIL enhancement"""
        # Convert to PIL Image
        if len(image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(2.0)
        
        # Convert back to OpenCV format
        enhanced_cv = cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(enhanced_cv, cv2.COLOR_BGR2GRAY)
        
        return pytesseract.image_to_string(gray, config='--psm 6')
    
    def multi_scale_ocr(self, image):
        """OCR with multiple scales"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        best_text = ""
        best_length = 0
        
        # Try different scales
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
        
        return best_text
    
    def edge_based_ocr(self, image):
        """OCR with edge detection preprocessing"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate edges to make text thicker
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Invert for OCR
        inverted = cv2.bitwise_not(dilated)
        
        return pytesseract.image_to_string(inverted, config='--psm 6')
    
    def color_separation_ocr(self, image):
        """OCR with color channel separation"""
        if len(image.shape) != 3:
            return ""
        
        best_text = ""
        best_length = 0
        
        # Try different color channels
        channels = ['B', 'G', 'R']
        for i, channel in enumerate(channels):
            # Extract single channel
            single_channel = image[:, :, i]
            
            # Apply preprocessing
            denoised = cv2.medianBlur(single_channel, 5)
            adaptive_thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Try OCR
            try:
                text = pytesseract.image_to_string(adaptive_thresh, config='--psm 6')
                if len(text.strip()) > best_length:
                    best_text = text
                    best_length = len(text.strip())
            except:
                continue
        
        return best_text
    
    def test_all_methods(self, image_path):
        """Test all OCR methods on an image"""
        print(f"🔍 Testing OCR methods on: {os.path.basename(image_path)}")
        print("=" * 60)
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Could not load image")
            return
        
        results = {}
        
        for method_name, method_func in self.methods.items():
            try:
                print(f"\n🧪 Testing {method_name}...")
                text = method_func(image)
                results[method_name] = text
                
                # Show sample of extracted text
                sample = text.strip()[:100] if text.strip() else "No text extracted"
                print(f"   Sample: {sample}...")
                print(f"   Length: {len(text.strip())} characters")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[method_name] = ""
        
        return results
    
    def analyze_results(self, results):
        """Analyze and compare OCR results"""
        print(f"\n📊 OCR Results Analysis")
        print("=" * 40)
        
        # Find the best method by text length
        best_method = max(results.items(), key=lambda x: len(x[1].strip()))
        print(f"🏆 Best method by length: {best_method[0]} ({len(best_method[1].strip())} chars)")
        
        # Show all results
        for method, text in results.items():
            length = len(text.strip())
            print(f"{method:15}: {length:3d} chars - {text.strip()[:50]}...")
        
        return best_method[0], best_method[1]

def main():
    """Main function to test OCR improvements"""
    print("🔧 OCR Improvement System")
    print("=" * 30)
    
    improver = OCRImprover()
    
    # Test on a few receipt images
    test_images = [
        'Bowls/PHOTO-2025-07-21-11-44-42.jpg',
        'Bowls/PHOTO-2025-07-21-11-44-42 3.jpg',
        'Bowls/PHOTO-2025-07-21-11-44-41.jpg'
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            # First, let's crop the receipt part
            print(f"\n📸 Processing: {os.path.basename(image_path)}")
            
            # Load and crop image (assuming receipt is on left side for now)
            image = cv2.imread(image_path)
            if image is None:
                continue
            
            height, width = image.shape[:2]
            receipt_region = image[:, :width//2]  # Left half
            
            # Save cropped receipt for testing
            cropped_path = f"temp_receipt_{os.path.basename(image_path)}"
            cv2.imwrite(cropped_path, receipt_region)
            
            # Test all OCR methods
            results = improver.test_all_methods(cropped_path)
            
            # Analyze results
            best_method, best_text = improver.analyze_results(results)
            
            # Clean up temp file
            os.remove(cropped_path)
            
            print(f"\n✅ Best OCR method for this image: {best_method}")
            print(f"📝 Best extracted text:")
            print(f"   {best_text.strip()}")
            
        else:
            print(f"⚠️ Image not found: {image_path}")

if __name__ == "__main__":
    main()
