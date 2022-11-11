print("This program will count the number of syllables in a phrase")
phrase = input("Enter a phrase: ").lower()

def sylCounter(word):
    vowels = ('a', 'i', 'e', 'o', 'u', 'y')
    syl = 0
    loc = 0
    if len(word) <= 2:
        return 1 # if word has 2 or fewer characters, it must have 1 syllable
    for ch in word:
        if ch in vowels and word[loc + 1] not in vowels:
            syl += 1 # add one to counter for each letter that follows the pattern Vs (V being current ch)
        if loc != len(word) - 2:
            loc += 1 # keep iterating if loc would not exceed checkable range
    if word[-1] in vowels and word[-2] not in vowels:
        syl += 1 # add one to counter if the last two characters are sv
    if word[-1] == 'e' and word[-2] not in vowels:
        syl -= 1 # subtract one from counter if last two characters are se
        
    if word[-1] in vowels and word[-2] in vowels:
        syl += 1 # add one to counter if last two characters are vv
        
    return syl


words = phrase.split(" ")
sylcount = 0
for word in words:
    sylcount += sylCounter(word)

print(f"The number of syllables is {sylcount}")
