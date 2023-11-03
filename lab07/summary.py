"""
Answers the summary question from lab07.
"""

with open("common.txt", encoding="utf-8") as f:
    common_words = set()
    for line in f:
        common_words.add(line.rstrip())

with open("article.txt", encoding="utf-8") as a:
    a_dict = {}
    for line in a:
        word = line.rstrip()
        if word not in common_words:
            if word in a_dict:
                a_dict[word] += 1
            else:
                a_dict[word] = 1

most_common_word = max(a_dict, key=a_dict.get)

print(f"The topic of this article is {most_common_word}")
