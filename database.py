from datetime import date
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    meal_id = Column(String, index=True)
    food_name = Column(String)
    calories = Column(Float)
    protein = Column(Float)
    log_date = Column(Date, default=date.today, index=True)


class FoodCache(Base):
    __tablename__ = "food_cache"

    id = Column(Integer, primary_key=True)
    food_name = Column(String, unique=True, index=True)
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)


class UserGoal(Base):
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    calories_goal = Column(Float)
    protein_goal = Column(Float)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    language = Column(String, default="fa")


class TranslationCache(Base):
    __tablename__ = "translation_cache"

    id = Column(Integer, primary_key=True)
    source_text = Column(String, index=True)
    language = Column(String, index=True)
    translated_text = Column(String)


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    weight = Column(Float)
    log_date = Column(Date, default=date.today, index=True)

class ProductCache(Base):
    __tablename__ = "product_cache"

    barcode = Column(String, primary_key=True)

    name = Column(String)
    brand = Column(String)

    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(Integer, primary_key=True)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    last_log_date = Column(Date)


class FavoriteFood(Base):
    __tablename__ = "favorite_foods"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    food_text = Column(Text, nullable=False)


class UserFoodPreference(Base):
    __tablename__ = "user_food_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    original_food = Column(String, nullable=False)
    preferred_food = Column(String, nullable=False)
    preferred_unit = Column(String, nullable=False)
    usage_count = Column(Integer, default=1)


class CoachUsage(Base):
    __tablename__ = "coach_usage"

    user_id = Column(Integer, primary_key=True)
    last_used_at = Column(DateTime)


engine = create_engine("sqlite:///food.db")
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)
