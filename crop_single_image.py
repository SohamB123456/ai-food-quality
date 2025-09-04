import cv2
import os

# Specific image path
image_path = '/Users/sohambhagnani/Desktop/Image Detection/PHOTO-2025-07-21-11-44-48.jpg'

# Output folders
receipt_folder = 'Receipts'
bowl_folder = 'Bowls'

# Create output folders
os.makedirs(receipt_folder, exist_ok=True)
os.makedirs(bowl_folder, exist_ok=True)

def crop_single_image(image_path):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read {image_path}")
        return
    
    # Get image dimensions
    height, width = img.shape[:2]
    print(f"Image dimensions: {width} x {height}")
    
    # Calculate crop boundaries
    # Left half (receipt) - from 0 to width/2
    # Right half (bowl) - from width/2 to width
    receipt_crop = img[:, :width//2]
    bowl_crop = img[:, width//2:]
    
    # Create output filenames
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    receipt_filename = f"{base_name}_receipt.jpg"
    bowl_filename = f"{base_name}_bowl.jpg"
    
    receipt_path = os.path.join(receipt_folder, receipt_filename)
    bowl_path = os.path.join(bowl_folder, bowl_filename)
    
    # Save the cropped images
    cv2.imwrite(receipt_path, receipt_crop)
    cv2.imwrite(bowl_path, bowl_crop)
    
    print(f"Processed: {os.path.basename(image_path)}")
    print(f"  Receipt saved to: {receipt_path}")
    print(f"  Bowl saved to: {bowl_path}")
    print(f"  Receipt crop size: {receipt_crop.shape[1]} x {receipt_crop.shape[0]}")
    print(f"  Bowl crop size: {bowl_crop.shape[1]} x {bowl_crop.shape[0]}")

# Crop the specific image
crop_single_image(image_path)

print(f"\nCropping complete!")
print(f"Receipts saved to: {receipt_folder}/")
print(f"Bowls saved to: {bowl_folder}/") 