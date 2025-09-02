from openai import OpenAI
import base64
import os
import sys

# Set your OpenAI API key here or via the OPENAI_API_KEY environment variable
openai_api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Your published prompt ID (replace with your actual prompt ID if different)
PROMPT_ID = "pmp_6886654a37e8819496650dd064467ddc02cd4803"
PROMPT_VERSION = "1"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def check_bowl_receipt_match(image_path):
    image_b64 = encode_image(image_path)

    # This input structure assumes your prompt expects a user message and an image
    response = client.responses.create(
        prompt={
            "id": PROMPT_ID,
            "version": PROMPT_VERSION
        },
        input={
            "user_message": "This image contains both the bowl and the receipt. Do they match?",
            "image": f"data:image/jpeg;base64,{image_b64}"
        }
    )
    print(response)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bowl_receipt_match_custom_prompt.py <image_path>")
        exit(1)
    image_path = sys.argv[1]
    check_bowl_receipt_match(image_path) 