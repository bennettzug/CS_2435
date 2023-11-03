item = input("What inventory item are we looking for? ")
f = open("inventory.txt", "r")

inventory = []
for line in f:
    inventory.append(line.strip())

f.close()

# check how many
num = inventory.count(item)

print(f"The number of times {item} appears is {num}")
