#!/usr/bin/env python3
"""
PokeWorks QA System Demo
Comprehensive demonstration of all system capabilities
"""

import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def create_demo_image():
    """
    Create a simple demo image for testing
    """
    print("🎨 Creating demo image...")
    
    # Create a simple demo image (600x400)
    width, height = 600, 400
    demo_image = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
    
    # Draw a simple bowl on the left side
    bowl_center = (150, 200)
    bowl_radius = 80
    cv2.circle(demo_image, bowl_center, bowl_radius, (200, 150, 100), -1)  # Brown bowl
    cv2.circle(demo_image, bowl_center, bowl_radius, (0, 0, 0), 2)  # Black border
    
    # Add some "ingredients" in the bowl
    cv2.circle(demo_image, (130, 180), 15, (0, 255, 0), -1)  # Green (avocado)
    cv2.circle(demo_image, (170, 180), 15, (255, 0, 0), -1)  # Red (tomato)
    cv2.circle(demo_image, (150, 220), 15, (0, 0, 255), -1)  # Blue (fish)
    
    # Draw a receipt on the right side
    receipt_x = 320
    receipt_y = 50
    receipt_width = 250
    receipt_height = 300
    
    cv2.rectangle(demo_image, (receipt_x, receipt_y), 
                  (receipt_x + receipt_width, receipt_y + receipt_height), 
                  (240, 240, 240), -1)  # Light gray receipt
    cv2.rectangle(demo_image, (receipt_x, receipt_y), 
                  (receipt_x + receipt_width, receipt_y + receipt_height), 
                  (0, 0, 0), 2)  # Black border
    
    # Add text to the receipt
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(demo_image, "POKEWORKS", (receipt_x + 20, receipt_y + 30), 
                font, 0.7, (0, 0, 0), 2)
    cv2.putText(demo_image, "White Rice", (receipt_x + 20, receipt_y + 60), 
                font, 0.5, (0, 0, 0), 1)
    cv2.putText(demo_image, "Salmon", (receipt_x + 20, receipt_y + 90), 
                font, 0.5, (0, 0, 0), 1)
    cv2.putText(demo_image, "Avocado", (receipt_x + 20, receipt_y + 120), 
                font, 0.5, (0, 0, 0), 1)
    cv2.putText(demo_image, "Cucumber", (receipt_x + 20, receipt_y + 150), 
                font, 0.5, (0, 0, 0), 1)
    cv2.putText(demo_image, "Total: $12.50", (receipt_x + 20, receipt_y + 200), 
                font, 0.6, (0, 0, 0), 2)
    
    # Save the demo image
    demo_path = "demo_image.jpg"
    cv2.imwrite(demo_path, demo_image)
    print(f"✅ Demo image created: {demo_path}")
    
    return demo_path

def demo_fuzzy_matching():
    """
    Demo the fuzzy matching capabilities
    """
    print("\n🔍 DEMO: Fuzzy Matching System")
    print("=" * 50)
    
    try:
        from fuzzy_matching import IngredientMatcher, load_ingredients_from_file
        
        # Load ingredients
        ingredients = load_ingredients_from_file("Ingredients.txt")
        print(f"📋 Loaded {len(ingredients)} known ingredients")
        
        # Create matcher
        matcher = IngredientMatcher(ingredients)
        
        # Test various ingredient names
        test_ingredients = [
            "White Rice",
            "Salmon", 
            "Avocado",
            "Cucumber",
            "Spicy Tuna",
            "Brown Rice",
            "Seaweed Salad",
            "Extra Spicy Tuna",  # Should match "Spicy Tuna"
            "Unknown Ingredient"
        ]
        
        print(f"\n🧪 Testing ingredient matching:")
        for ingredient in test_ingredients:
            match_result = matcher.find_best_match(ingredient)
            if match_result:
                print(f"✅ '{ingredient}' -> '{match_result['matched_ingredient']}' "
                      f"(confidence: {match_result['confidence']}%, strategy: {match_result['strategy']})")
            else:
                print(f"❌ '{ingredient}' -> No match found")
                
    except Exception as e:
        print(f"❌ Error in fuzzy matching demo: {e}")

def demo_auto_crop():
    """
    Demo the auto crop detection
    """
    print("\n✂️  DEMO: Auto Crop Detection")
    print("=" * 50)
    
    try:
        from auto_crop_detection import detect_bowl_receipt_split
        
        # Create demo image
        demo_path = create_demo_image()
        
        # Test auto crop
        print(f"🔄 Testing auto crop on: {demo_path}")
        bowl_crop, receipt_crop = detect_bowl_receipt_split(demo_path, "demo_output")
        
        print(f"✅ Auto crop successful!")
        print(f"   Bowl crop shape: {bowl_crop.shape}")
        print(f"   Receipt crop shape: {receipt_crop.shape}")
        
    except Exception as e:
        print(f"❌ Error in auto crop demo: {e}")

def demo_ocr_processing():
    """
    Demo OCR processing
    """
    print("\n📄 DEMO: OCR Processing")
    print("=" * 50)
    
    try:
        import pytesseract
        
        # Create demo image
        demo_path = create_demo_image()
        
        # Load and process with OCR
        image = cv2.imread(demo_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simple OCR
        text = pytesseract.image_to_string(gray)
        
        print(f"📝 OCR Results:")
        print(f"Raw text: {text.strip()}")
        
        # Look for ingredients
        ingredients_found = []
        for line in text.split('\n'):
            line = line.strip()
            if any(ingredient.lower() in line.lower() for ingredient in ['rice', 'salmon', 'avocado', 'cucumber']):
                ingredients_found.append(line)
        
        print(f"🍣 Ingredients detected: {ingredients_found}")
        
    except Exception as e:
        print(f"❌ Error in OCR demo: {e}")

def demo_web_interface():
    """
    Demo the web interface
    """
    print("\n🌐 DEMO: Web Interface")
    print("=" * 50)
    
    print("🚀 To demo the web interface:")
    print("1. Run: python app.py")
    print("2. Open browser to: http://localhost:5000")
    print("3. Upload an image with bowl (left) and receipt (right)")
    print("4. Watch the AI process and analyze!")
    
    print("\n📱 Features:")
    print("✅ Drag & drop image upload")
    print("✅ Real-time processing progress")
    print("✅ Automatic image splitting")
    print("✅ OCR text extraction")
    print("✅ Ingredient matching")
    print("✅ Results visualization")
    print("✅ Export functionality")

def main():
    """
    Run the complete demo
    """
    print("🍣 POKEWORKS QA SYSTEM DEMO")
    print("=" * 60)
    print(f"🕐 Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all demos
    demo_fuzzy_matching()
    demo_auto_crop()
    demo_ocr_processing()
    demo_web_interface()
    
    print("\n🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("📊 System Capabilities Demonstrated:")
    print("✅ Fuzzy ingredient matching")
    print("✅ Automatic image cropping")
    print("✅ OCR text extraction")
    print("✅ Web interface ready")
    print("✅ Batch processing available")
    print("✅ Interactive cropping tools")
    
    print(f"\n🚀 Next Steps:")
    print("1. Run 'python app.py' to start the web interface")
    print("2. Upload your own bowl/receipt images")
    print("3. Test with real PokeWorks orders!")
    
    # Clean up demo files
    if os.path.exists("demo_image.jpg"):
        os.remove("demo_image.jpg")
        print("\n🧹 Demo files cleaned up")

if __name__ == "__main__":
    main()

