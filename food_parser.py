import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_json(content):
    content = content.strip()
    content = re.sub(r"^```json", "", content)
    content = re.sub(r"^```", "", content)
    content = re.sub(r"```$", "", content)
    return content.strip()


def parse_food(text):
    prompt = f"""
Analyze this food text. It can be Persian or English.

Return ONLY raw JSON. No markdown. No explanation.

Translate every food name to simple English.

Use this exact format:
[
  {{
    "food": "egg",
    "quantity": 2,
    "unit": "piece"
  }}
]

Rules:
- If the user says grams, use unit: "gram"
- If the user says one glass, use unit: "glass"
- If the user says one plate, use unit: "plate"
- If the user says spoon of jam/honey, decide tablespoon or teaspoon based on context.
- If uncertain about a household unit, make a reasonable estimate.

Text:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content
    clean_content = extract_json(content)
    return json.loads(clean_content)
