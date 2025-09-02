import clip
import torch
from PIL import Image
import sys
import os

def check_bowl_ingredients(bowl_image_path, required_ingredients, similarity_threshold=0.25):
    """
    Check if a bowl image matches the required ingredients using CLIP
    
    Args:
        bowl_image_path: Path to the bowl image
        required_ingredients: List of required ingredients
        similarity_threshold: Minimum similarity score to consider a match
    
    Returns:
        tuple: (similarity_score, is_match, match_percentage)
    """
    
    # Load CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model, preprocess = clip.load("ViT-B/32", device=device)
    
    # Load and preprocess the image
    try:
        image = preprocess(Image.open(bowl_image_path)).unsqueeze(0).to(device)
    except Exception as e:
        print(f"Error loading image {bowl_image_path}: {e}")
        return None, False, 0
    
    # Prepare the text prompt
    ingredient_text = ", ".join(required_ingredients)
    text = clip.tokenize([ingredient_text]).to(device)
    
    # Encode image and text
    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)
    
    # Compute cosine similarity
    similarity = (image_features @ text_features.T).squeeze().item()
    
    # Determine if it's a match
    is_match = similarity >= similarity_threshold
    match_percentage = (similarity + 1) * 50  # Convert to percentage (CLIP scores range from -1 to 1)
    
    return similarity, is_match, match_percentage

def main():
    if len(sys.argv) < 3:
        print("Usage: python clip_bowl_ingredient_check.py <bowl_image_path> <ingredient1> <ingredient2> ...")
        print("Example: python clip_bowl_ingredient_check.py Bowls/bowl1.jpg 'white rice' 'salmon' 'cucumber'")
        sys.exit(1)
    
    bowl_image_path = sys.argv[1]
    required_ingredients = sys.argv[2:]
    
    print(f"Checking bowl: {bowl_image_path}")
    print(f"Required ingredients: {', '.join(required_ingredients)}")
    print("-" * 50)
    
    # Check if image exists
    if not os.path.exists(bowl_image_path):
        print(f"Error: Image file {bowl_image_path} not found!")
        sys.exit(1)
    
    # Perform the check
    similarity, is_match, match_percentage = check_bowl_ingredients(bowl_image_path, required_ingredients)
    
    if similarity is not None:
        print(f"CLIP Similarity Score: {similarity:.4f}")
        print(f"Match Percentage: {match_percentage:.1f}%")
        print(f"Match Result: {'✅ MATCH' if is_match else '❌ NO MATCH'}")
        
        # Provide interpretation
        if is_match:
            print(f"✅ The bowl appears to contain the required ingredients!")
        else:
            print(f"❌ The bowl may not contain all required ingredients.")
            print(f"   (Try lowering the threshold if this is a false negative)")
    else:
        print("❌ Failed to process the image")

if __name__ == "__main__":
    main() 