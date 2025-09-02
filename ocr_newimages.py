import cv2
import pytesseract
import os

folder_path = 'newImages'
results_folder = 'newImages_OCR_Results'
os.makedirs(results_folder, exist_ok=True)

def ocr_core(img):
    text = pytesseract.image_to_string(img)
    return text

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def remove_noise(image):
    return cv2.medianBlur(image, 5)

def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Batch OCR for newImages
for file in os.listdir(folder_path):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        file_path = os.path.join(folder_path, file)
        print(f"\nProcessing {file}...")
        
        # Read image
        img = cv2.imread(file_path)
        if img is None:
            print(f"Could not read {file}")
            continue
            
        # Apply preprocessing
        img_gray = get_grayscale(img)
        img_denoised = remove_noise(img_gray)
        img_thresholded = thresholding(img_denoised)
        
        # Perform OCR on both original and preprocessed images
        print("OCR Result (Original):")
        text_original = ocr_core(img)
        print(text_original)
        
        print("OCR Result (Preprocessed):")
        text_preprocessed = ocr_core(img_thresholded)
        print(text_preprocessed)
        
        # Save OCR results to txt files
        base_name = os.path.splitext(file)[0]
        
        # Save original OCR result
        txt_filename_original = base_name + '_original.txt'
        txt_path_original = os.path.join(results_folder, txt_filename_original)
        with open(txt_path_original, 'w') as f:
            f.write(text_original)
            
        # Save preprocessed OCR result
        txt_filename_preprocessed = base_name + '_preprocessed.txt'
        txt_path_preprocessed = os.path.join(results_folder, txt_filename_preprocessed)
        with open(txt_path_preprocessed, 'w') as f:
            f.write(text_preprocessed)
            
        print(f"Results saved to {results_folder}/")

print(f"\nAll OCR processing complete! Results saved in {results_folder}/") 