import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from database import SessionLocal, WeightLog


def create_weekly_chart(report, user_id):
    dates = list(report["daily"].keys())
    calories = [v["calories"] for v in report["daily"].values()]
    protein = [v["protein"] for v in report["daily"].values()]

    output_file = f"weekly_report_{user_id}.png"

    plt.figure(figsize=(9, 5))
    plt.plot(dates, calories, marker="o", label="Calories")
    plt.plot(dates, protein, marker="o", label="Protein")
    plt.title("Weekly Nutrition Report")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    return output_file


def create_weight_chart(weight_history, user_id):
    dates = [item["date"] for item in weight_history]
    weights = [item["weight"] for item in weight_history]

    output_file = f"weight_report_{user_id}.png"

    plt.figure(figsize=(9, 5))
    plt.plot(dates, weights, marker="o", label="Weight")
    plt.title("Weight Report")
    plt.xlabel("Date")
    plt.ylabel("Weight (kg)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    return output_file


def generate_weight_chart(user_id):
    db = SessionLocal()

    weights = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user_id)
        .order_by(WeightLog.log_date.asc())
        .all()
    )

    db.close()

    if len(weights) < 2:
        return None

    dates = [w.log_date.strftime("%d/%m") for w in weights]
    values = [w.weight for w in weights]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, values, marker="o")
    plt.title("Weight Progress")
    plt.ylabel("kg")
    plt.grid(True)

    chart_path = f"/tmp/weight_{user_id}.png"

    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path
