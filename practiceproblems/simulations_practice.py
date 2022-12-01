'''
example problems from CS2345 on 11/7/2022
'''
import random
from typing import Callable


# simulation of flipping a coin
def coin_flip() -> bool:
    '''Returns the result of flipping a coin, either 'H' or 'T'.'''
    return random.choice(['H', 'T'])


# simulation of rolling a die
def roll(sides: int) -> int:
    '''Returns the result of rolling one die.'''
    return random.randint(1, sides)


# simulation of rolling two dice
def two_rolls(sides: int) -> int:
    '''Returns the result of rolling two dice.'''
    return roll(sides) + roll(sides)


def six_rolls() -> bool:
    for _ in range(4):
        if roll(6) == 6:
            return True
    return False


def twenty_four_rolls() -> bool:
    for _ in range(24):
        if two_rolls(6) == 12:
            return True
    return False


DECK = [(suit, rank+1) for suit in ['S', 'C', 'H', 'D'] for rank in range(13)]


def hand_generator() -> list:
    '''returns a hand of 5 cards from a deck.'''
    return random.sample(DECK, 5)


def flush_checker() -> bool:
    '''Returns a bool value as to whether a hand is a flush.'''
    hand = hand_generator()
    isuit, *_ = hand[0]
    for suit, *_ in hand:
        if suit != isuit:
            return False
    return True


def full_house_checker() -> bool:
    '''Returns a bool value as to whether or not a hand is a full house.'''
    hand = hand_generator()
    count = {}
    for *_, rank in hand:
        if rank in count:
            count[rank] += 1
        else:
            count[rank] = 1
    return set(count.values()) == {2, 3}


def pi_tester() -> bool:
    '''Determines whether or not a random value is inside of a circle inscribed
    in a square of side length 2. Should average to 1/4 * pi.'''
    x = random.random() * 2
    y = random.random() * 2
    d = (x-1)*(x-1) + (y-1)*(y-1)
    return d <= 1


def geometric_repeater(trials: int, function: Callable, success=True) -> float:
    '''Runs a geometric distribition a certain number of times, and then
     returns the average numnber of trials.'''
    count = 0
    avg = 0
    for _ in range(trials):
        while True:
            count += 1
            if function() in success:
                avg += count
                break
    return avg / trials


def bool_repeater(trials: int, function: Callable[float, float], success=True) -> float:
    '''Repeats a boolean test a certain number of times, then returns the
     success rate.'''
    count = 0
    for _ in range(trials):
        if function() == success:
            count += 1
    return count / trials


def pi_calculator(trials: int) -> None:
    '''Repeats pi_tester a certain number of times, then prints
     an approximation of pi.'''
    num = bool_repeater(trials, pi_tester)
    print(f"pi is roughly {4 * num}")


def prob_calculator(trials: int, function: Callable, success=True):
    '''Prints a string describing the probability that some function will be
     equal to a success value.'''

    prob = bool_repeater(trials, function, success)
    print(f'probability of {function.__name__} being {success} ' +
          f'is {prob * 100}%')


def main() -> None:
    '''does that dudes experiment w/ 10 million trials'''
    print(bool_repeater(1_000_000, twenty_four_rolls))


if __name__ == "__main__":
    main()
