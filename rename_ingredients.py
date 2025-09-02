import os
import re
import shutil

# Read ingredients from Ingredients.txt
with open('Ingredients.txt', 'r') as f:
    ingredients = [line.strip() for line in f if line.strip()]

# Path to ingredients folder
ingredients_folder = 'Ingredients'

# Get all image files in the ingredients folder
image_files = [f for f in os.listdir(ingredients_folder) 
               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

print("Ingredients from Ingredients.txt:")
for ing in ingredients:
    print(f"  - {ing}")

print(f"\nFound {len(image_files)} images in {ingredients_folder}/")
print("Image files:")
for img in image_files:
    print(f"  - {img}")

# Create a mapping of ingredient names to their images
ingredient_to_images = {}

for ingredient in ingredients:
    matching_images = []
    
    # Look for images that contain the ingredient name (case insensitive)
    for image_file in image_files:
        # Remove file extension and convert to lowercase for comparison
        image_name = os.path.splitext(image_file)[0].lower()
        ingredient_lower = ingredient.lower()
        
        # Check if ingredient name appears in image filename
        if ingredient_lower in image_name or image_name in ingredient_lower:
            matching_images.append(image_file)
    
    if matching_images:
        ingredient_to_images[ingredient] = matching_images

# Create output folder for renamed images
output_folder = 'RenamedIngredients'
os.makedirs(output_folder, exist_ok=True)

# Copy images to the new folder (keeping original names)
copied_count = 0
for ingredient, images in ingredient_to_images.items():
    for image_file in images:
        # Copy the file with original name
        old_path = os.path.join(ingredients_folder, image_file)
        new_path = os.path.join(output_folder, image_file)
        
        print(f"Copying: {image_file}")
        shutil.copy2(old_path, new_path)
        copied_count += 1

print(f"\nCopied {copied_count} images to {output_folder}/")

# Create a summary file
with open('ingredient_images_summary.txt', 'w') as f:
    f.write("Ingredient Images Summary\n")
    f.write("=" * 30 + "\n\n")
    
    for ingredient in ingredients:
        if ingredient in ingredient_to_images:
            f.write(f"{ingredient}:\n")
            for image_file in ingredient_to_images[ingredient]:
                f.write(f"  - {image_file}\n")
            f.write("\n")
        else:
            f.write(f"{ingredient}: No matching images found\n\n")

print("Created ingredient_images_summary.txt with the mapping.") 