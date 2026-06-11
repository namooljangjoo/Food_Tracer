import os

from dotenv import load_dotenv
from openai import OpenAI

from goals_service import get_goal
from shopping_service import generate_shopping_list

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_weekly_meal_plan(user_id, language="fa"):
    goal = get_goal(user_id)

    if not goal:
        return None

    common_foods = generate_shopping_list(user_id)

    foods_text = "\n".join(
        [f"- {food_name} ({count} times)" for food_name, count in common_foods[:15]]
    )

    prompt = f"""
You are a nutrition coach.

Create a practical 7-day meal plan.

User goals:
Calories per day: {goal.calories_goal}
Protein per day: {goal.protein_goal}

Foods the user often eats:
{foods_text}

Rules:
- Keep it practical.
- Prefer foods the user already eats.
- Include breakfast, lunch, dinner, and one snack.
- Mention approximate calories and protein per day.
- Keep it concise.
- Language: {"Persian" if language == "fa" else "English"}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()
