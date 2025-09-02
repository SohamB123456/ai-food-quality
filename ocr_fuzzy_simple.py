import cv2
import pytesseract
import os
from rapidfuzz import fuzz, process

# Paths
folder_path = 'Receipts'
results_folder = 'newImages_OCR_Results'
ingredients_file = 'Ingredients.txt'
fuzzy_output_folder = 'newImages_FuzzyResults'
matched_ingredients_folder = 'MatchedIngredients'
os.makedirs(results_folder, exist_ok=True)
os.makedirs(fuzzy_output_folder, exist_ok=True)
os.makedirs(matched_ingredients_folder, exist_ok=True)

def ocr_core(img):
    text = pytesseract.image_to_string(img)
    return text

# Read ingredients
with open(ingredients_file, 'r') as f:
    ingredients = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(ingredients)} ingredients for matching")

# Simple OCR and fuzzy matching for newImages (original images only)
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
            
        # Perform OCR on original image only
        print("\nOCR Result:")
        text = ocr_core(img)
        print(text)
        
        # Save OCR result
        base_name = os.path.splitext(file)[0]
        txt_filename = base_name + '.txt'
        txt_path = os.path.join(results_folder, txt_filename)
        with open(txt_path, 'w') as f:
            f.write(text)
        
        # Fuzzy matching
        print(f"\nFuzzy Matching Results:")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        matches = []
        
        for line in lines:
            if len(line) > 2:  # Only process lines with meaningful content
                match, score, _ = process.extractOne(line, ingredients, scorer=fuzz.ratio)
                matches.append((line, match, score))
                print(f"'{line}' -> '{match}' (score: {score})")
        
        # Save fuzzy matching results
        fuzzy_filename = base_name + '_fuzzy.txt'
        fuzzy_path = os.path.join(fuzzy_output_folder, fuzzy_filename)
        with open(fuzzy_path, 'w') as f:
            f.write(f"Fuzzy matches for {txt_filename}:\n")
            f.write("="*50 + "\n")
            for orig, ing, score in matches:
                f.write(f"'{orig}' -> '{ing}' (score: {score})\n")
        
        # Save just the matched ingredients to separate folder
        matched_ingredients_filename = base_name + '_matched_ingredients.txt'
        matched_ingredients_path = os.path.join(matched_ingredients_folder, matched_ingredients_filename)
        with open(matched_ingredients_path, 'w') as f:
            for orig, ing, score in matches:
                f.write(f"{ing}\n")
            
        print(f"\nResults saved to {results_folder}/, {fuzzy_output_folder}/, and {matched_ingredients_folder}/")

print(f"\n{'='*50}")
print("All OCR and fuzzy matching processing complete!")
print(f"OCR results: {results_folder}/")
print(f"Fuzzy matching results: {fuzzy_output_folder}/")
print(f"Matched ingredients: {matched_ingredients_folder}/")
print(f"{'='*50}") 