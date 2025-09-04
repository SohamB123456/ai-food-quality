import cv2
import os

# Paths
input_folder = 'newImages'  # Change this to your folder name
receipt_folder = 'Receipts'
bowl_folder = 'Bowls'

# Create output folders
os.makedirs(receipt_folder, exist_ok=True)
os.makedirs(bowl_folder, exist_ok=True)

def crop_image(image_path, output_receipt_path, output_bowl_path):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read {image_path}")
        return
    
    # Get image dimensions
    height, width = img.shape[:2]
    
    # Calculate crop boundaries
    # Left half (receipt) - from 0 to width/2
    # Right half (bowl) - from width/2 to width
    receipt_crop = img[:, :width//2]
    bowl_crop = img[:, width//2:]
    
    # Save the cropped images
    cv2.imwrite(output_receipt_path, receipt_crop)
    cv2.imwrite(output_bowl_path, bowl_crop)
    
    print(f"Processed {os.path.basename(image_path)}")
    print(f"  Receipt saved to: {output_receipt_path}")
    print(f"  Bowl saved to: {output_bowl_path}")

# Process all images in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        input_path = os.path.join(input_folder, filename)
        
        # Create output filenames
        base_name = os.path.splitext(filename)[0]
        receipt_filename = f"{base_name}_receipt.jpg"
        bowl_filename = f"{base_name}_bowl.jpg"
        
        receipt_path = os.path.join(receipt_folder, receipt_filename)
        bowl_path = os.path.join(bowl_folder, bowl_filename)
        
        # Crop the image
        crop_image(input_path, receipt_path, bowl_path)

print(f"\nCropping complete!")
print(f"Receipts saved to: {receipt_folder}/")
print(f"Bowls saved to: {bowl_folder}/") 