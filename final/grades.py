"""Solves grades problem for CS2435 final."""

print("Get a letter grade for the student based on the curve.")
grade = int(input("Please enter a grade between 0 and 100: "))

with open("grades.txt", encoding="utf-8") as file:
    grades = [int(line.rstrip()) for line in file]

class_average = sum(grades) / len(grades)
deviations = [(grade - class_average) ** 2 for grade in grades]
variance = sum(deviations) / len(deviations)
st_dev = variance**0.5
z_score = (grade - class_average) / st_dev
round_zsc = round(z_score)
letter_grades = {-1: "D", 0: "C", 1: "B"}
current_grade = letter_grades.get(round_zsc, "F" if round_zsc <= -2 else "A")

print(f"Class average: {class_average:.2f}")
print(f"Standard deviation: {st_dev:.2f}")
print(f"Z-score: {z_score:.2f}")
print(f"Current grade: {current_grade}")
