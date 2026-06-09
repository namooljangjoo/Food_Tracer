from database import FoodLog, SessionLocal

db = SessionLocal()

food = FoodLog(
    food_name="Chicken Breast",
    calories=250,
    protein=45
)

db.add(food)
db.commit()

print("Food saved successfully!")