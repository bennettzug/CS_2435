import random

rpsOptions = ("rock", "paper", "scissors")

compNum = random.randint(0, 2)
compChoice = rpsOptions[compNum]

humanChoice = input("Lets play a game of Rock, Paper and Scissors\nChoose one [type rock, paper or scissors]? ")
humanNum = rpsOptions.index(humanChoice)

choicesStr = f"Human chose {humanChoice}. Computer chose {compChoice}."

if compNum == humanNum:
    print(choicesStr + " Tie.")
elif compNum == humanNum + 1 or compNum == humanNum - 2:
    print(choicesStr + " Computer wins.")
elif compNum == humanNum + 2 or compNum == humanNum - 1:
    print(choicesStr + " Human wins.")
