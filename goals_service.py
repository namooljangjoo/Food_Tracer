from database import UserGoal, SessionLocal


def save_goal(user_id, calories, protein):
    db = SessionLocal()

    goal = db.query(UserGoal).filter(
        UserGoal.user_id == user_id
    ).first()

    if goal:
        goal.calories_goal = calories
        goal.protein_goal = protein
    else:
        goal = UserGoal(
            user_id=user_id,
            calories_goal=calories,
            protein_goal=protein,
        )
        db.add(goal)

    db.commit()
    db.close()


def get_goal(user_id):
    db = SessionLocal()

    goal = db.query(UserGoal).filter(
        UserGoal.user_id == user_id
    ).first()

    db.close()
    return goal
