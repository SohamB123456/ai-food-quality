import cv2
import pytesseract
import os

folder_path = 'ProcessedVariants'
results_folder = 'MethodResults'
os.makedirs(results_folder, exist_ok=True)

def ocr_core(img) :
    text = pytesseract.image_to_string(img)
    return text

def get_grayscale( image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def remove_noise(image):
    return cv2. medianBlur(image, 5)

def thresholding( image):
    return cv2. threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Batch OCR for ProcessedVariants
for file in os.listdir(folder_path):
    if file.endswith('.jpg'):
        file_path = os.path.join(folder_path, file)
        print(f"\nProcessing {file}...")
        img = cv2.imread(file_path)
        text = ocr_core(img)
        print("OCR Result:")
        print(text)
        # Save OCR result to txt file
        txt_filename = os.path.splitext(file)[0] + '.txt'
        txt_path = os.path.join(results_folder, txt_filename)
        with open(txt_path, 'w') as f:
            f.write(text)

# Single image with preprocessing
img = cv2.imread('/Users/sohambhagnani/Desktop/Image Detection/Testing Images/Cropped.png')
img = get_grayscale(img)
img = thresholding(img)
img = remove_noise(img)
print ("New Method: OCR Result:")
new_method_text = ocr_core(img)
print(new_method_text)
# Save this result as well
with open(os.path.join(results_folder, 'Cropped_new_method.txt'), 'w') as f:
    f.write(new_method_text)
