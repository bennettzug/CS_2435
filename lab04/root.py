import math

a = float(input("A = "))

#start with guess of one
#stop when new answer isn't much different than last answer (within 1e-6 of it)


def f(x, A):
    return x**2 + A

def fprime(x):
    return 2 * x

def nrm(x, A):
    return f(x, A) / fprime(x)


x = 1
iteration = 0
prevx = 0

while abs(x - prevx) > 1E-10:
    print(f"iteration {iteration}: {x:.6f}")
    prevx = x
    x = nrm(x, a)
    
    iteration += 1

print(f"Using Newton-Raphson method: sqrt({a:.6f}) = {x:.6f}")
print(f"Using math.sqrt: sqrt({a:.6f}) = {math.sqrt(a):.6f}")

