from database import SessionLocal, UserFoodPreference


AUTO_APPLY_THRESHOLD = 3


def remember_choice(
    user_id,
    original_food,
    preferred_food,
    preferred_unit,
):
    db = SessionLocal()

    item = (
        db.query(UserFoodPreference)
        .filter(
            UserFoodPreference.user_id == user_id,
            UserFoodPreference.original_food == original_food,
            UserFoodPreference.preferred_food == preferred_food,
        )
        .first()
    )

    if item:
        item.usage_count += 1
    else:
        item = UserFoodPreference(
            user_id=user_id,
            original_food=original_food,
            preferred_food=preferred_food,
            preferred_unit=preferred_unit,
            usage_count=1,
        )

        db.add(item)

    db.commit()
    db.close()


def get_preference(user_id, original_food):
    db = SessionLocal()

    item = (
        db.query(UserFoodPreference)
        .filter(
            UserFoodPreference.user_id == user_id,
            UserFoodPreference.original_food == original_food,
        )
        .order_by(UserFoodPreference.usage_count.desc())
        .first()
    )

    db.close()

    if not item:
        return None

    if item.usage_count < AUTO_APPLY_THRESHOLD:
        return None

    return {
        "food": item.preferred_food,
        "unit": item.preferred_unit,
        "count": item.usage_count,
    }
