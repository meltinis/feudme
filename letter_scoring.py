LETTER_DATA = {
    'A': {'count': 7, 'point': 1},
    'B': {'count': 3, 'point': 3},
    'C': {'count': 2, 'point': 8},
    'D': {'count': 4, 'point': 2},
    'E': {'count': 11, 'point': 1},
    'F': {'count': 2, 'point': 3},
    'G': {'count': 3, 'point': 3},
    'H': {'count': 2, 'point': 4},
    'I': {'count': 6, 'point': 2},
    'J': {'count': 2, 'point': 4},
    'K': {'count': 4, 'point': 3},
    'L': {'count': 5, 'point': 2},
    'M': {'count': 3, 'point': 3},
    'N': {'count': 6, 'point': 1},
    'O': {'count': 5, 'point': 2},
    'P': {'count': 2, 'point': 3},
    'R': {'count': 6, 'point': 1},
    'S': {'count': 6, 'point': 1},
    'T': {'count': 5, 'point': 1},
    'U': {'count': 3, 'point': 3},
    'V': {'count': 2, 'point': 3},
    'X': {'count': 1, 'point': 8},
    'Y': {'count': 2, 'point': 4},
    'Z': {'count': 1, 'point': 8},
    'Æ': {'count': 2, 'point': 4},
    'Ø': {'count': 2, 'point': 4},
    'Å': {'count': 2, 'point': 4}
}

def calculate_word_value(word):
    total = 0
    for letter in word.upper():
        if letter in LETTER_DATA:
            total += LETTER_DATA[letter]['point']
        else:
            print(f"Warning: letter {letter} not defined.")
    return total
