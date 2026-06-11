from database import SessionLocal, FavoriteFood


def save_favorite(user_id, title, food_text):
    db = SessionLocal()

    item = FavoriteFood(
        user_id=user_id,
        title=title,
        food_text=food_text,
    )

    db.add(item)
    db.commit()
    db.close()


def get_favorites(user_id):
    db = SessionLocal()

    items = (
        db.query(FavoriteFood)
        .filter(FavoriteFood.user_id == user_id)
        .order_by(FavoriteFood.title.asc())
        .all()
    )

    db.close()

    return items


def get_favorite_by_id(favorite_id):
    db = SessionLocal()

    item = (
        db.query(FavoriteFood)
        .filter(FavoriteFood.id == favorite_id)
        .first()
    )

    db.close()

    return item
