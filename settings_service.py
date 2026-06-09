from database import UserSettings, SessionLocal


def save_language(user_id, language):
    db = SessionLocal()

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if settings:
        settings.language = language
    else:
        settings = UserSettings(user_id=user_id, language=language)
        db.add(settings)

    db.commit()
    db.close()


def get_language(user_id):
    db = SessionLocal()

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    db.close()

    if not settings:
        return None

    return settings.language
