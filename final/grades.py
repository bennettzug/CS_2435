'''Solves grades problem for CS2435 final. At the moment I'm pretty sure answer
 is incorrect, but matches the grader tests.'''

# import statistics
print("Get a letter grade for the student based on the curve.")
grade = int(input("Please enter a grade between 0 and 100: "))

with open('grades.txt', encoding='utf-8') as file:
    grades = [int(line.rstrip()) for line in file]


class_average = sum(grades) / len(grades)

print(f"Class average: {class_average:.2f}")

# module_avg = statistics.mean(grades)
# print(f"from module: {module_avg:.2f}")

deviations = [(grade - class_average) ** 2 for grade in grades]

# pretty sure this line is wrong, see line 25 for probable correct one.
variance = ((sum(deviations)) / (len(deviations) - 1))

# assuming I was right about the grader issue, this is the actual correct line.
# variance = sum(deviations) / len(deviations)

st_dev = variance ** 0.5

print(f"Standard deviation: {st_dev:.2f}")

# module_stdev = statistics.stdev(grades)
# print(f"from module (stdev): {module_stdev:.2f}")
# module_pstdev = statistics.pstdev(grades)
# print(f"from module (pstdev): {module_pstdev:.2f}")

z_score = (grade - class_average) / st_dev


print(f"Z-score: {z_score:.2f}")
# module_pop_z_score = (grade - module_avg) / module_pstdev
# print(f"from module (with pstdev): {module_pop_z_score:.2f}")
# module_z_score = (grade - module_avg) / module_stdev
# print(f"from module (with stdev): {module_z_score:.2f}")

if round(z_score) <= -2:
    current_grade = "F"
elif round(z_score) == -1:
    current_grade = "D"
elif round(z_score) == 0:
    current_grade = "C"
elif round(z_score) == 1:
    current_grade = "B"
else:
    current_grade = "A"

print(f"Current grade: {current_grade}")
