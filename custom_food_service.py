import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from database import FoodCache, SessionLocal

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def estimate_custom_food(food_name, ingredients_text):
    prompt = f"""
You are a nutrition estimator.

Estimate nutrition per 100 grams for this custom food.
Return food_name as a simple English lowercase name, even if the input is Persian.

Food name:
{food_name}

Ingredients:
{ingredients_text}

Return ONLY valid JSON:
{{
  "food_name": "...",
  "calories_per_100g": 0,
  "protein_per_100g": 0
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    data = json.loads(content)

    return {
        "food_name": data["food_name"],
        "calories_per_100g": float(data["calories_per_100g"]),
        "protein_per_100g": float(data["protein_per_100g"]),
    }


def save_custom_food(food_name, calories_per_100g, protein_per_100g):
    db = SessionLocal()

    existing = db.query(FoodCache).filter(
        FoodCache.food_name == food_name.lower().strip()
    ).first()

    if existing:
        existing.calories_per_100g = calories_per_100g
        existing.protein_per_100g = protein_per_100g
    else:
        item = FoodCache(
            food_name=food_name.lower().strip(),
            calories_per_100g=calories_per_100g,
            protein_per_100g=protein_per_100g,
        )
        db.add(item)

    db.commit()
    db.close()
