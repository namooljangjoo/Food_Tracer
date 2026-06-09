from goals_service import save_goal, get_goal

save_goal(2500, 180)

goal = get_goal()

print(goal.calories_goal)
print(goal.protein_goal)