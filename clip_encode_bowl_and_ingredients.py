import clip
import torch
from PIL import Image
import sys

# Usage: python clip_encode_bowl_and_ingredients.py <bowl_image_path> "ingredient1, ingredient2, ..."

if len(sys.argv) != 3:
    print("Usage: python clip_encode_bowl_and_ingredients.py <bowl_image_path> 'ingredient1, ingredient2, ...'")
    sys.exit(1)

bowl_image_path = sys.argv[1]
ingredient_list = sys.argv[2]

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load and preprocess the image
image = preprocess(Image.open(bowl_image_path)).unsqueeze(0).to(device)

# Prepare the text prompt
text = clip.tokenize([ingredient_list]).to(device)

# Encode image and text
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)

# Compute cosine similarity
similarity = (image_features @ text_features.T).squeeze().item()

print(f"Similarity score between bowl image and ingredient list: {similarity:.4f}") 