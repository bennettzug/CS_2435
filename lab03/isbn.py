from curses.ascii import isdigit

isbn = input('Enter an ISBN number: ')


def isValidIsbn(isbn):
    if len(isbn) != 10:
        return False

    firstNine = isbn[0:9]
    sum = 0
    iter = 10
    try:
        int(firstNine)
    except ValueError:
        return False

    for ch in firstNine:
        sum += int(ch) * iter
        iter -= 1
    lastDigit = 0
    if isbn[9] == 'X':
        lastDigit = 10
    elif isbn[9].isdigit():
        lastDigit = int(isbn[9])
    else:
        return False

    if (11 - (sum % 11)) % 11 == lastDigit:
        return True
    else:
        return False


if isValidIsbn(isbn):
    print("ISBN number accepted.")
else:
    print("Invalid ISBN number.")
