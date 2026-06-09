from meal_calculator import calculate_and_save_meal
from daily_summary import get_today_summary
from formatter import format_meal_response

meal_result = calculate_and_save_meal(
    "دو عدد تخم مرغ و 150 گرم سینه مرغ و یک بشقاب برنج"
)

today_summary = get_today_summary()

message = format_meal_response(meal_result, today_summary)

print(message)