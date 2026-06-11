import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_ai_coach_report(
    user_profile,
    weekly_data,
    recent_foods,
):
    prompt = f"""
You are an expert nutrition coach.

Analyze this user's nutrition.

User:

{user_profile}

Weekly Data:

{weekly_data}

Recent Foods:

{recent_foods}

Return a practical nutrition coaching report.

Requirements:
- Explain current progress
- Mention calories
- Mention protein
- Mention weight trend
- Mention strongest point
- Mention biggest problem
- Give 3 actionable recommendations
- Keep response under 250 words
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
