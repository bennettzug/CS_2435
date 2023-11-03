"""Prints the total post-interest amount paid, after taking a couple values
 as input"""

P = int(input("Enter the principal amount: "))
r = int(input("Enter the rate of interest: ")) * 0.01
n = int(input("Enter the number of times interest is compounded in a year: "))
t = int(input("Enter the total number of years borrowed: "))
total_amount_paid = P * (1 + (r / n)) ** (n * t)
print(f"The total amount paid is {total_amount_paid:.2f}")
