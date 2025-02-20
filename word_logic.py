# word_logic.py
from dictionary_builder import find_possible_words



def find_spot_left(placed_letters, r, c, board_size=15):
    
    pattern = ""
    count = 0
    col = c - 1
    
    #counting the number of empty slots - cannot exeed the number of user letter (7)
    while count < = 7:
        #build the pattern
        if (r,col) in placed_letters:
            pattern = (r,col) + pattern
        else:
            pattern = ".?" + pattern
        
        count += 1
        col -= 1
    
    return pattern



class Spot:
    def __init__(self, scenario, letter, prepattern, postpattern):
        self.scenario = scenario
        self.prepattern = prepattern
        self.postpattern = postpattern
        self.fullpattern = prepattern + letter + postpattern

def get_anchor_data(placed_letters, board_size=15):
    """
    For each placed letter, determines its anchor properties.
    - Horizontal END anchor: if there is no letter immediately to its left,
      available span = 1 + count_empty_left.
    - Vertical END anchor: if there is no letter immediately above,
      available span = 1 + count_empty_above.
    - Horizontal START anchor: if there is no letter immediately to its right,
      available span = 1 + count_empty_right.
    - Vertical START anchor: if there is no letter immediately below,
      available span = 1 + count_empty_below.
    Returns a dictionary mapping each placed letter coordinate to a dictionary of available spans.
    """
    anchor_data = {}
    for (r, c) in placed_letters:
        spots = []
    
        #Start with the horizontal spots
        pre_empty_len, prefix = find_spot_left(placed_letters, r, c)
        post_empty_len, postfix = find_spot_right(placed_letters, r, c)
        
        spot("horizontal", prefix, postfix, pre_empty_len, post_empty_len)

        spots.append(spot)
        
        #vertical spots
        pre_empty_len, prefix = find_spot_top(placed_letters, r, c)
        post_empty_len, postfix = find_spot_bottom(placed_letters, r, c)
        
        spot("vertical", prefix, postfix, pre_empty_len, post_empty_len)
        
        spots.append(spot)
        

    return spots

def find_possible_words_with_board_scenarios(user_letters, placed_letters, anagram_dictionary, board_size=15):
    """
    Uses anchor data to generate candidate words.
    For each anchor:
      - For "horiz_end" or "vert_end": candidate = user_letters + board letter.
      - For "horiz_start" or "vert_start": candidate = board letter + user_letters.
    Only candidates whose length does not exceed the available span are considered.
    Returns a list of tuples: (candidate_word, anchor_coordinate, scenario, available_span).
    """
    candidates = []
    anchors = get_anchor_data(placed_letters, board_size)
    
    for spot in anchors.items():
        
    
    for (r, c), scenarios in anchors.items():
        for scenario, avail in scenarios.items():
            if scenario in ["horiz_end", "vert_end"]:
                candidate = user_letters + placed_letters[(r, c)]
            else:  # "horiz_start" or "vert_start"
                candidate = placed_letters[(r, c)] + user_letters
            if len(candidate) <= avail:
                words = find_possible_words(candidate, anagram_dictionary, min_length=2)
                for w in words:
                    if len(w) <= avail:
                        candidates.append((w, (r, c), scenario, avail))
    return candidates
