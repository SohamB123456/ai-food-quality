import os
import shutil

# Paths
ocr_results_folder = 'newImages_OCR_Results'
clean_results_folder = 'newImages_CleanOCR'

# Clear and recreate the clean folder
if os.path.exists(clean_results_folder):
    shutil.rmtree(clean_results_folder)
os.makedirs(clean_results_folder, exist_ok=True)

# Copy OCR results to clean folder with new names
for filename in os.listdir(ocr_results_folder):
    if filename.endswith('.txt'):
        # Source file
        source_path = os.path.join(ocr_results_folder, filename)
        
        # Create clean filename (remove any suffixes and just keep the base name)
        base_name = filename.replace('.txt', '')
        clean_filename = f"{base_name}_clean.txt"
        clean_path = os.path.join(clean_results_folder, clean_filename)
        
        # Copy the file
        shutil.copy2(source_path, clean_path)
        print(f"Copied: {filename} -> {clean_filename}")

print(f"\nClean OCR results saved to: {clean_results_folder}/")
print("These files contain only the OCR text without any extra formatting.") 