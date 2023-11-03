import math

print("This program calculates the inverse tangent of a given value.")
iters = int(input("Number of iterations: "))
x = float(input("x = "))

# takes a hot minute
exp = 1
total = 0
sign = 1
for i in range(iters):
    term = x**exp / exp
    total += term * sign
    sign *= -1
    exp += 2

arctan = total
print(f"using Gregory's series, arctan({x:6f}) = {arctan:.6f}")
print(f"using the math library, arctan({x:.6f}) = {math.atan(x):.6f}")
