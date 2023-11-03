print("Let's Play Wordle!")
target = input("Target word: ")
f = open("guesses.txt", "r")
w = open("output.txt", "w")


def wstr(guess, word):
    wstr = ""

    for loc, ch in enumerate(guess):
        if ch not in word:
            wstr += "."
        elif ch == word[loc]:
            wstr += "!"
        else:
            wstr += "?"
    return wstr


print(target, file=w)
for line in f:
    print(f"{line.rstrip()} {wstr(line.rstrip(), target)}", file=w)

w.close()
f.close()
