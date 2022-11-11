import math
x = float(input("x = "))

exp = 1
total = 0
sign = 1
fact = 1
for i in range(10):
    if exp > 1:
        fact *= exp * (exp - 1)
    term = (x ** exp / fact)
    total += term * sign
    sign *= -1
    exp += 2

    print(f"iteration {i}: {total:.6f}")

print(f"Using Taylor series: sine({x:.6f}) = {total:.6f}")
print(f"Using math.sin: sine({x:.6f}) = {math.sin(x):.6f}")
