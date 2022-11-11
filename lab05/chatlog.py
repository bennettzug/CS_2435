'''user chat search

# format is 'username: message'

take a username and return all messages from a user into a new file'''


print('This program will find all messages from a given user in a chatlog')
username = input("Username: ")

f = open("chat.log", encoding='utf-8')

outputFile = f"{username}.txt"
w = open(outputFile, 'w', encoding='utf-8')


for line in f:
    if line.startswith(username) and line[len(username)] == ':':
        print(line.rstrip(line[-1]), file=w)


w.close()
f.close()
