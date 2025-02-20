import csv
import pickle
from collections import defaultdict, Counter

def build_dictionary_from_csv(csv_filename):
    """
    Reads words from a CSV file, removes duplicates,
    and builds a dictionary mapping the sorted letters to a list of words.
    """
    unique_words = set()
    with open(csv_filename, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for word in row:
                clean_word = word.strip().lower()
                if clean_word:
                    unique_words.add(clean_word)
    anagram_dict = defaultdict(list)
    for word in unique_words:
        key = ''.join(sorted(word))
        anagram_dict[key].append(word)
    return dict(anagram_dict)

def load_dictionary(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_dictionary(dictionary, filename):
    with open(filename, 'wb') as f:
        pickle.dump(dictionary, f)

def find_possible_words(letters, anagram_dict, min_length=2, prefix="", postfix=""):
    """
    SKAL OPDATERES SÅLEDES AT:
    
    
    
    
    
    
    
    
    Given a set of letters, returns all words from the anagram_dict that can be formed
    from those letters (considering multiplicity). Two additional parameters, prefix and postfix,
    allow you to constrain the result to words that start with the given prefix and/or end with the given postfix.
    If prefix or postfix is empty, no constraint is applied for that position.
    """
    candidate_counter = Counter(letters.lower())
    results = set()
    for key, word_list in anagram_dict.items():
        if len(key) < min_length:
            continue
        key_counter = Counter(key)
        if all(candidate_counter[letter] >= count for letter, count in key_counter.items()):
            for word in word_list:
                # Apply the prefix and postfix constraints if provided.
                if prefix and not word.startswith(prefix.lower()):
                    continue
                if postfix and not word.endswith(postfix.lower()):
                    continue
                results.add(word)
    return results
