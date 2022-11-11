import math
initialAmount = int(input("Enter the initial amount of Carbon-14 in the sample (in grams): "))
currentAmount = int(input("Enter the current amount of Carbon-14 in the sample (in grams): "))
k = 3.9e-12
t = (math.log(currentAmount / initialAmount)) / (k * -1)
tInYears = t / 3153600
print(f"The age of the sample is {tInYears:.2f} years")
