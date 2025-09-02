import cv2
import numpy as np
import os

# Input and output paths
input_path = '/Users/sohambhagnani/Desktop/Image Detection/Testing Images/Cropped.png'
output_dir = 'ProcessedVariants'
os.makedirs(output_dir, exist_ok=True)

# Load image
img = cv2.imread(input_path)

# 1. Original
cv2.imwrite(os.path.join(output_dir, 'original.jpg'), img)

# 2. Grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite(os.path.join(output_dir, 'gray.jpg'), gray)

# 3. Otsu Threshold
otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
cv2.imwrite(os.path.join(output_dir, 'otsu.jpg'), otsu)

# 4. Adaptive Mean Threshold
adapt_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 11)
cv2.imwrite(os.path.join(output_dir, 'adaptive_mean.jpg'), adapt_mean)

# 5. Adaptive Gaussian Threshold
adapt_gauss = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 11)
cv2.imwrite(os.path.join(output_dir, 'adaptive_gaussian.jpg'), adapt_gauss)

# 6. Median Blur
median = cv2.medianBlur(gray, 5)
cv2.imwrite(os.path.join(output_dir, 'median_blur.jpg'), median)

# 7. Bilateral Filter
bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
cv2.imwrite(os.path.join(output_dir, 'bilateral.jpg'), bilateral)

# 8. FastNlMeans Denoising
nlmeans = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
cv2.imwrite(os.path.join(output_dir, 'nlmeans.jpg'), nlmeans)

# 9. Morphological Opening
kernel = np.ones((2,2), np.uint8)
morph_open = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
cv2.imwrite(os.path.join(output_dir, 'morph_open.jpg'), morph_open)

# 10. Histogram Equalization
histeq = cv2.equalizeHist(gray)
cv2.imwrite(os.path.join(output_dir, 'histeq.jpg'), histeq)

# 11. Resize (2x)
resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
cv2.imwrite(os.path.join(output_dir, 'resized_2x.jpg'), resized)

# 12. Deskew (simple, based on largest contour)
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = 0
    if len(coords) > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return image

deskewed = deskew(gray)
cv2.imwrite(os.path.join(output_dir, 'deskewed.jpg'), deskewed)

print(f"Saved all variants to {output_dir}/") 