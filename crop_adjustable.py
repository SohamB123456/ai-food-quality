#!/usr/bin/env python3
"""
Adjustable Crop Module
Interactive cropping tool for fine-tuning bowl and receipt regions
"""

import cv2
import numpy as np
import os
import argparse
from typing import Tuple, Optional

class AdjustableCropper:
    """
    Interactive cropping tool with adjustable parameters
    """
    
    def __init__(self, image_path: str):
        """
        Initialize the cropper with an image
        
        Args:
            image_path: Path to the input image
        """
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        self.height, self.width = self.image.shape[:2]
        self.split_x = self.width // 2  # Default split at middle
        self.bowl_crop = None
        self.receipt_crop = None
        
        print(f"📏 Image loaded: {self.width}x{self.height}")
        print(f"📍 Initial split at x={self.split_x}")
    
    def set_split_position(self, x: int) -> None:
        """
        Set the split position for cropping
        
        Args:
            x: X coordinate for the split (0 to width)
        """
        self.split_x = max(0, min(x, self.width))
        print(f"📍 Split position set to x={self.split_x}")
    
    def crop_regions(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Crop the image into bowl and receipt regions
        
        Returns:
            Tuple of (bowl_crop, receipt_crop)
        """
        self.bowl_crop = self.image[:, :self.split_x]
        self.receipt_crop = self.image[:, self.split_x:]
        
        print(f"✂️  Cropped regions:")
        print(f"   Bowl: {self.bowl_crop.shape[1]}x{self.bowl_crop.shape[0]}")
        print(f"   Receipt: {self.receipt_crop.shape[1]}x{self.receipt_crop.shape[0]}")
        
        return self.bowl_crop, self.receipt_crop
    
    def preview_crop(self) -> np.ndarray:
        """
        Create a preview image showing the crop regions
        
        Returns:
            Preview image with crop lines
        """
        preview = self.image.copy()
        
        # Draw vertical line at split position
        cv2.line(preview, (self.split_x, 0), (self.split_x, self.height), (0, 255, 0), 2)
        
        # Add labels
        cv2.putText(preview, "BOWL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(preview, "RECEIPT", (self.split_x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add split position info
        cv2.putText(preview, f"Split: x={self.split_x}", (10, self.height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return preview
    
    def save_crops(self, output_dir: str, prefix: str = "") -> Tuple[str, str]:
        """
        Save the cropped regions to files
        
        Args:
            output_dir: Directory to save the crops
            prefix: Prefix for the output filenames
            
        Returns:
            Tuple of (bowl_path, receipt_path)
        """
        if self.bowl_crop is None or self.receipt_crop is None:
            self.crop_regions()
        
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        bowl_path = os.path.join(output_dir, f"{prefix}{base_name}_bowl.jpg")
        receipt_path = os.path.join(output_dir, f"{prefix}{base_name}_receipt.jpg")
        
        cv2.imwrite(bowl_path, self.bowl_crop)
        cv2.imwrite(receipt_path, self.receipt_crop)
        
        print(f"💾 Saved crops:")
        print(f"   Bowl: {bowl_path}")
        print(f"   Receipt: {receipt_path}")
        
        return bowl_path, receipt_path
    
    def interactive_adjust(self) -> None:
        """
        Interactive adjustment of crop position using mouse
        """
        print("🖱️  Interactive crop adjustment")
        print("   - Click to set split position")
        print("   - Press 's' to save crops")
        print("   - Press 'q' to quit")
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.set_split_position(x)
                preview = self.preview_crop()
                cv2.imshow('Adjustable Crop', preview)
        
        preview = self.preview_crop()
        cv2.namedWindow('Adjustable Crop', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Adjustable Crop', mouse_callback)
        cv2.imshow('Adjustable Crop', preview)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                output_dir = "adjusted_crops"
                self.save_crops(output_dir)
                print("✅ Crops saved!")
        
        cv2.destroyAllWindows()

def auto_detect_optimal_split(image_path: str) -> int:
    """
    Automatically detect the optimal split position
    
    Args:
        image_path: Path to the input image
        
    Returns:
        Optimal x coordinate for splitting
    """
    image = cv2.imread(image_path)
    if image is None:
        return cv2.imread(image_path).shape[1] // 2
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    # Method 1: Edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
    vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, vertical_kernel)
    
    # Find contours
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Look for vertical line near the middle
    mid_point = width // 2
    best_split = mid_point
    min_distance = float('inf')
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < 20 and h > height * 0.3 and abs(x - mid_point) < width * 0.2:
            distance = abs(x - mid_point)
            if distance < min_distance:
                min_distance = distance
                best_split = x
    
    return best_split

def batch_adjust_crops(input_dir: str, output_dir: str, auto_detect: bool = True):
    """
    Batch process images with adjustable cropping
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save cropped images
        auto_detect: Whether to auto-detect optimal split positions
    """
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    if not os.path.exists(input_dir):
        raise ValueError(f"Input directory does not exist: {input_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    image_files = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            image_files.append(os.path.join(input_dir, filename))
    
    if not image_files:
        print("❌ No image files found in input directory")
        return
    
    print(f"📁 Processing {len(image_files)} images...")
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n🔄 Processing {i}/{len(image_files)}: {os.path.basename(image_path)}")
        
        try:
            cropper = AdjustableCropper(image_path)
            
            if auto_detect:
                optimal_split = auto_detect_optimal_split(image_path)
                cropper.set_split_position(optimal_split)
                print(f"🤖 Auto-detected split at x={optimal_split}")
            
            cropper.save_crops(output_dir)
            
        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Adjustable crop tool for bowl and receipt images')
    parser.add_argument('input', help='Input image path or directory')
    parser.add_argument('-o', '--output', default='cropped_output', help='Output directory')
    parser.add_argument('--interactive', action='store_true', help='Interactive crop adjustment')
    parser.add_argument('--batch', action='store_true', help='Batch process directory')
    parser.add_argument('--auto-detect', action='store_true', help='Auto-detect optimal split position')
    parser.add_argument('--split-x', type=int, help='Manual split position (x coordinate)')
    
    args = parser.parse_args()
    
    if args.batch:
        batch_adjust_crops(args.input, args.output, args.auto_detect)
    else:
        try:
            cropper = AdjustableCropper(args.input)
            
            if args.split_x is not None:
                cropper.set_split_position(args.split_x)
            elif args.auto_detect:
                optimal_split = auto_detect_optimal_split(args.input)
                cropper.set_split_position(optimal_split)
            
            if args.interactive:
                cropper.interactive_adjust()
            else:
                cropper.save_crops(args.output)
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
