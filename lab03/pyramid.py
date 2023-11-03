len = int(input("How many rows to print: "))

numspaces = len - 1

for i in range(len):
    stars = "*" * (2 * i + 1)
    print(
        " " * numspaces + stars
    )  # doesn't work with grader - it adds trailing whitespace, which is not accepted
    numspaces -= 1
