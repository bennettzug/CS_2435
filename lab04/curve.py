print("Computing the area under the curve x^2 + x + 1")
left = 100  # int(input("Enter the left end point a: x = "))
right = 200  # int(input("Enter the right end point b: x = "))


def f(x):
    return x**2 + x + 1


dx = 0.1
for i in range(6):
    total = 0
    x = left
    while x < right:
        total += f(x) * dx
        x += dx
    print(
        f"Area under the curve between {left} and {right} using dx = {dx:.0E} is {total:.6f}"
    )
    dx /= 10
