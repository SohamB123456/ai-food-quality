import openai
import base64
import os

# Set your OpenAI API key here or via the OPENAI_API_KEY environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def check_bowl_receipt_match(image_path):
    image_b64 = encode_image(image_path)

    prompt = (
        "You are a helpful assistant. "
        "This image contains both a food bowl and a receipt. "
        "Determine if the ingredients in the bowl match the items listed on the receipt. "
        "Be specific about any matches or mismatches."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "This image contains both the bowl and the receipt."},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                ],
            },
        ],
        max_tokens=500,
    )

    print(response['choices'][0]['message']['content'])

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python bowl_receipt_match_gpt4o.py <image_path>")
        exit(1)
    image_path = sys.argv[1]
    check_bowl_receipt_match(image_path)