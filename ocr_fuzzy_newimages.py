import cv2
import pytesseract
import os
from rapidfuzz import fuzz, process

# Paths
folder_path = 'newImages'
results_folder = 'newImages_OCR_Results'
ingredients_file = 'Ingredients.txt'
fuzzy_output_folder = 'newImages_FuzzyResults'
os.makedirs(results_folder, exist_ok=True)
os.makedirs(fuzzy_output_folder, exist_ok=True)

def ocr_core(img):
    text = pytesseract.image_to_string(img)
    return text

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def remove_noise(image):
    return cv2.medianBlur(image, 5)

def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Read ingredients
with open(ingredients_file, 'r') as f:
    ingredients = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(ingredients)} ingredients for matching")

# Batch OCR and fuzzy matching for newImages
for file in os.listdir(folder_path):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        file_path = os.path.join(folder_path, file)
        print(f"\n{'='*50}")
        print(f"Processing {file}...")
        print(f"{'='*50}")
        
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
        print("\nOCR Result (Original):")
        text_original = ocr_core(img)
        print(text_original)
        
        print("\nOCR Result (Preprocessed):")
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
        
        # Fuzzy matching for original OCR
        print(f"\nFuzzy Matching Results for {txt_filename_original}:")
        lines_original = [line.strip() for line in text_original.split('\n') if line.strip()]
        matches_original = []
        
        for line in lines_original:
            if len(line) > 2:  # Only process lines with meaningful content
                match, score, _ = process.extractOne(line, ingredients, scorer=fuzz.ratio)
                matches_original.append((line, match, score))
                print(f"'{line}' -> '{match}' (score: {score})")
        
        # Fuzzy matching for preprocessed OCR
        print(f"\nFuzzy Matching Results for {txt_filename_preprocessed}:")
        lines_preprocessed = [line.strip() for line in text_preprocessed.split('\n') if line.strip()]
        matches_preprocessed = []
        
        for line in lines_preprocessed:
            if len(line) > 2:  # Only process lines with meaningful content
                match, score, _ = process.extractOne(line, ingredients, scorer=fuzz.ratio)
                matches_preprocessed.append((line, match, score))
                print(f"'{line}' -> '{match}' (score: {score})")
        
        # Save fuzzy matching results
        fuzzy_filename_original = base_name + '_original_fuzzy.txt'
        fuzzy_path_original = os.path.join(fuzzy_output_folder, fuzzy_filename_original)
        with open(fuzzy_path_original, 'w') as f:
            f.write(f"Fuzzy matches for {txt_filename_original}:\n")
            f.write("="*50 + "\n")
            for orig, ing, score in matches_original:
                f.write(f"'{orig}' -> '{ing}' (score: {score})\n")
        
        fuzzy_filename_preprocessed = base_name + '_preprocessed_fuzzy.txt'
        fuzzy_path_preprocessed = os.path.join(fuzzy_output_folder, fuzzy_filename_preprocessed)
        with open(fuzzy_path_preprocessed, 'w') as f:
            f.write(f"Fuzzy matches for {txt_filename_preprocessed}:\n")
            f.write("="*50 + "\n")
            for orig, ing, score in matches_preprocessed:
                f.write(f"'{orig}' -> '{ing}' (score: {score})\n")
            
        print(f"\nResults saved to {results_folder}/ and {fuzzy_output_folder}/")

print(f"\n{'='*50}")
print("All OCR and fuzzy matching processing complete!")
print(f"OCR results: {results_folder}/")
print(f"Fuzzy matching results: {fuzzy_output_folder}/")
print(f"{'='*50}") 