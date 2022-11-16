
import random
import math
# its roughtly n/ln(n)
def is_prime(n):
    '''primality checker'''
    if n < 2:
        return False
    if n == 2:
        return True
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True

#probability that a random number is prime is 1 / ln(n) for a given range

# should take ln(n) trials to encounter a prime


def experiment(n):
    count = 1
    while True:
        count += 1
        x = random.randint(1, n)
        if is_prime(x):
            return count


print(f'{"size":^10}{"avg":^10}{"exp":^10}')

for i in range(5):
    n = 10**(i+3)
    trials = 100_000
    count = 0
    for i in range(trials):
        count += experiment(n)
    real = count/trials
    exp = math.log(n)
    print(f'{n:^10,}{real:^10.2f}{exp:^10.2f}')