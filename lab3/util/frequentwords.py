import os

words = []

file = open(os.path.join(os.path.dirname(__file__), 'resources/frequent_words.txt'))
for line in file:
    words.append(line.strip().lower())
file.close()


def is_frequent_word(word):
    word = word.lower()
    l, r = 0, len(words) - 1
    while l <= r:
        m = (l + r) // 2
        if word == words[m]:
            return True
        if word < words[m]:
            r = m - 1
            m = (l + r) // 2
        else:
            l = m + 1
            m = (l + r) // 2
    return False
