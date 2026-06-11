import base64
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_food_photo(image_path):
    image_base64 = image_to_base64(image_path)

    prompt = """
You are a nutrition estimation assistant.

Analyze the food in this image.

Estimate:
- food items
- grams for each item
- calories
- protein

Return ONLY valid JSON in this exact format:

{
  "items": [
    {
      "food": "food name",
      "grams": 100,
      "calories": 100,
      "protein": 10
    }
  ],
  "total_calories": 100,
  "total_protein": 10
}

Rules:
- Be conservative.
- If unsure, estimate reasonable portion sizes.
- Do not include markdown.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)
