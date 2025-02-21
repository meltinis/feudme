import tkinter as tk
from tkinter import messagebox
import os
import dictionary_builder   # Provides: build_dictionary_from_csv, load_dictionary, save_dictionary, find_possible_words
import letter_scoring       # Provides: calculate_word_value
import word_logic           # Provides anchor calculation and candidate generation functions

class GameUI:
    def __init__(self, master):
        self.master = master
        master.title("Crossword Board - Player's Tiles")
        
        # Load (or build) the dictionary from CSV/pickle.
        self.csv_file = "ordliste.csv"         # CSV file with words.
        self.pickle_file = "anagram_dict.pkl"   # Pickle file for the saved dictionary.
        if os.path.exists(self.pickle_file):
            self.anagram_dictionary = dictionary_builder.load_dictionary(self.pickle_file)
        else:
            self.anagram_dictionary = dictionary_builder.build_dictionary_from_csv(self.csv_file)
            dictionary_builder.save_dictionary(self.anagram_dictionary, self.pickle_file)
        
        # Dictionary for placed letters: coordinate -> letter.
        self.placed_letters = {}  # Updated when words are placed on the board.
        
        # Special cells for a 15x15 board (manually defined).
        # These cells are used for scoring but are ignored when calculating anchor availability.
        self.special_cells = {
            (7, 7): "START",  # Center start
            
            # Top-left quadrant
            (0, 0): "TL",  (0, 4): "TW",  (0, 7): "DL",
            (1, 1): "DL",  (1, 5): "TL",
            (2, 2): "DW",  (2, 6): "DL",
            (3, 3): "TL",  (3, 7): "DW",
            (4, 0): "TW",  (4, 4): "DW",  (4, 6): "DL",
            (5, 1): "TL",  (5, 5): "TL",
            (6, 2): "DL",  (6, 4): "DL",
            (7, 0): "DL",  (7, 3): "DW",
            
            # Top-right quadrant (mirrored using (14-x), y)
            (14, 0): "TL", (14, 4): "TW", (14, 7): "DL",
            (13, 1): "DL", (13, 5): "TL",
            (12, 2): "DW", (12, 6): "DL",
            (11, 3): "TL", (11, 7): "DW",
            (10, 0): "TW", (10, 4): "DL", (10, 6): "DL",
            (9, 1): "TL",  (9, 5): "TL",
            (8, 2): "DL",  (8, 4): "DL",
            (7, 14): "DL", (7, 11): "DW",
            
            # Bottom-left quadrant (mirrored using x, (14-y))
            (0, 14): "TL", (0, 10): "TW", (0, 7): "DL",
            (1, 13): "DL", (1, 9): "TL",
            (2, 12): "DW", (2, 8): "DL",
            (3, 11): "TL", (3, 7): "DW",
            (4, 10): "DL", (4, 14): "TW", (4, 8): "DL",
            (5, 9): "TL",  (5, 13): "TL",
            (6, 10): "DL", (6, 12): "DL",
            (7, 14): "DL", (7, 11): "DW",
            
            # Bottom-right quadrant (mirrored using (14-x), (14-y))
            (14, 14): "TL", (14, 10): "TW", (14, 7): "DL",
            (13, 13): "DL", (13, 9): "TL",
            (12, 12): "DW", (12, 8): "DL",
            (11, 11): "TL", (11, 7): "DW",
            (10, 10): "DL", (10, 14): "TW", (10, 8): "DL",
            (9, 9): "TL",   (9, 13): "TL",
            (8, 10): "DL",  (8, 12): "DL",
            (7, 14): "DL",  (7, 11): "DW",
        }
        
        # This dictionary will store candidate word information:
        # Mapping candidate word -> (anchor coordinate, scenario, available span).
        self.candidate_dict = {}
        
        # Main layout: two columns – left: board, rack, and input; right: possible words.
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="n")
        
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, padx=20, sticky="n")
        
        self.create_board(15, 15, parent=self.left_frame)
        self.create_player_rack(parent=self.left_frame)
        self.create_input_area(parent=self.left_frame)
        self.create_possible_words_area()
    
    # --- UI Creation Functions ---
    def create_board(self, rows, cols, parent):
        self.board_frame = tk.Frame(parent)
        self.board_frame.pack(pady=10)
        self.cells = {}
        for r in range(rows):
            for c in range(cols):
                if (r, c) in self.special_cells:
                    cell_type = self.special_cells[(r, c)]
                    if cell_type == "TW":
                        bg_color = "red"
                    elif cell_type == "DW":
                        bg_color = "orange"
                    elif cell_type == "DL":
                        bg_color = "green"
                    elif cell_type == "TL":
                        bg_color = "blue"
                    elif cell_type == "START":
                        bg_color = "purple"
                    else:
                        bg_color = "yellow"
                    text = cell_type
                else:
                    text = ""
                    bg_color = "white"
                label = tk.Label(self.board_frame, text=text, width=4, height=2,
                                 borderwidth=1, relief="solid", font=("Helvetica", 16), bg=bg_color)
                label.grid(row=r, column=c, padx=1, pady=1)
                self.cells[(r, c)] = label

    def create_player_rack(self, parent):
        self.rack_frame = tk.Frame(parent)
        self.rack_frame.pack(pady=10)
        self.update_rack("")

    def update_rack(self, letters):
        for widget in self.rack_frame.winfo_children():
            widget.destroy()
        for i, letter in enumerate(letters):
            label = tk.Label(self.rack_frame, text=letter, width=4, height=2,
                             borderwidth=1, relief="solid", font=("Helvetica", 16))
            label.grid(row=0, column=i, padx=2, pady=2)

    def create_input_area(self, parent):
        self.input_frame = tk.Frame(parent)
        self.input_frame.pack(pady=10)
        self.input_label = tk.Label(self.input_frame, text="Enter your tiles:", font=("Helvetica", 14))
        self.input_label.pack(side=tk.LEFT)
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(self.input_frame, textvariable=self.input_var, font=("Helvetica", 14))
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.update_button = tk.Button(self.input_frame, text="Update", command=self.update_all, font=("Helvetica", 14))
        self.update_button.pack(side=tk.LEFT, padx=5)
        self.availability_button = tk.Button(self.input_frame, text="Check Availability", command=self.check_availability_callback, font=("Helvetica", 12))
        self.availability_button.pack(side=tk.LEFT, padx=5)

    def create_possible_words_area(self):
        self.possible_words_frame = tk.Frame(self.right_frame)
        self.possible_words_frame.pack(pady=10)
        self.possible_words_label = tk.Label(self.possible_words_frame, text="Possible words:", font=("Helvetica", 14))
        self.possible_words_label.pack(anchor="w")
        self.words_listbox = tk.Listbox(self.possible_words_frame, font=("Helvetica", 12), width=30, height=20)
        self.words_listbox.pack()
        self.words_summary = tk.Label(self.possible_words_frame, text="", font=("Helvetica", 12))
        self.words_summary.pack(anchor="w", pady=5)
        self.place_word_button = tk.Button(self.possible_words_frame, text="Place selected word", command=self.place_word_button_callback, font=("Helvetica", 12))
        self.place_word_button.pack(pady=5)

    # --- Updating Possible Words ---
    def update_all(self):
        user_letters = self.input_var.get()
        self.update_rack(user_letters)
        if len(user_letters) < 2:
            self.words_listbox.delete(0, tk.END)
            self.words_summary.config(text="(Enter at least 2 letters)")
            return
        
        if not self.placed_letters:
            found_words = dictionary_builder.find_possible_words(user_letters, self.anagram_dictionary, min_length=2,"","")
            candidate_list = [(w, None, None, None) for w in found_words]
        else:
            candidate_list = word_logic.find_possible_words_with_board_scenarios(user_letters, self.placed_letters, self.anagram_dictionary, board_size=15)
        
        self.candidate_dict = {}
        for cand in candidate_list:
            w, anchor, scenario, avail = cand
            if w not in self.candidate_dict:
                self.candidate_dict[w] = (anchor, scenario, avail)
        scored_words = [(w, letter_scoring.calculate_word_value(w)) for w in self.candidate_dict.keys()]
        scored_words.sort(key=lambda x: x[1], reverse=True)
        total_count = len(scored_words)
        top_words = scored_words[:20]
        self.words_listbox.delete(0, tk.END)
        for w, score in top_words:
            if self.candidate_dict[w][0] is not None:
                anchor, scenario, avail = self.candidate_dict[w]
                self.words_listbox.insert(tk.END, f"{w} (Value: {score}) [Anchor: {anchor}, {scenario}]")
            else:
                self.words_listbox.insert(tk.END, f"{w} (Value: {score})")
        self.words_summary.config(text=f"Total: {total_count} words found")

    # --- Word Placement Functions ---
    def place_word_button_callback(self):
        selection = self.words_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a word from the list.")
            return
        index = selection[0]
        text = self.words_listbox.get(index)
        candidate_word = text.split()[0]
        info = self.candidate_dict.get(candidate_word, (None, None, None))
        anchor, scenario, avail = info
        if anchor is not None:
            r, c = anchor
            if scenario == "horiz_end":
                start_col = c - (len(candidate_word) - 1)
                start_row = r
                direction = "H"
            elif scenario == "horiz_start":
                start_col = c
                start_row = r
                direction = "H"
            elif scenario == "vert_end":
                start_row = r - (len(candidate_word) - 1)
                start_col = c
                direction = "V"
            elif scenario == "vert_start":
                start_row = r
                start_col = c
                direction = "V"
            else:
                start_row, start_col, direction = 0, 0, "H"
        else:
            start_row, start_col, direction = 0, 0, "H"
        self.open_place_word_dialog(candidate_word, start_row, start_col, direction, anchor, scenario)

    def open_place_word_dialog(self, word, start_row, start_col, direction, anchor, scenario):
        dialog = tk.Toplevel(self.master)
        dialog.title("Place Word")
        info_text = f"Place the word: {word}"
        if anchor is not None:
            info_text += f"\nAnchor: {anchor}, Scenario: {scenario}"
            info_text += f"\nAuto-start at: ({start_row}, {start_col}), Direction: {direction}"
        tk.Label(dialog, text=info_text, font=("Helvetica", 14)).pack(pady=5)
        
        frame_coord = tk.Frame(dialog)
        frame_coord.pack(pady=5)
        tk.Label(frame_coord, text="Row (0-14):", font=("Helvetica", 12)).grid(row=0, column=0)
        entry_row = tk.Entry(frame_coord, width=5, font=("Helvetica", 12))
        entry_row.grid(row=0, column=1, padx=5)
        entry_row.insert(0, str(start_row))
        tk.Label(frame_coord, text="Column (0-14):", font=("Helvetica", 12)).grid(row=0, column=2)
        entry_col = tk.Entry(frame_coord, width=5, font=("Helvetica", 12))
        entry_col.grid(row=0, column=3, padx=5)
        entry_col.insert(0, str(start_col))
        
        frame_dir = tk.Frame(dialog)
        frame_dir.pack(pady=5)
        tk.Label(frame_dir, text="Direction:", font=("Helvetica", 12)).pack(side=tk.LEFT)
        direction_var = tk.StringVar(value=direction)
        tk.Radiobutton(frame_dir, text="Horizontal", variable=direction_var, value="H", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_dir, text="Vertical", variable=direction_var, value="V", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        
        def preview_placement():
            try:
                row = int(entry_row.get())
                col = int(entry_col.get())
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers for row and column.")
                return
            d = direction_var.get()
            if d == "H" and col + len(word) > 15:
                messagebox.showerror("Error", "Word does not fit horizontally on the board.")
                return
            if d == "V" and row + len(word) > 15:
                messagebox.showerror("Error", "Word does not fit vertically on the board.")
                return
            self.preview_word_on_board(word, row, col, d)
        
        tk.Button(dialog, text="Preview", command=preview_placement, font=("Helvetica", 12)).pack(pady=5)
        
        def confirm_placement():
            try:
                row = int(entry_row.get())
                col = int(entry_col.get())
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers for row and column.")
                return
            d = direction_var.get()
            if d == "H" and col + len(word) > 15:
                messagebox.showerror("Error", "Word does not fit horizontally on the board.")
                return
            if d == "V" and row + len(word) > 15:
                messagebox.showerror("Error", "Word does not fit vertically on the board.")
                return
            self.place_word_on_board(word, row, col, d)
            dialog.destroy()
            current_letters = self.input_var.get()
            new_letters = self.remove_letters(current_letters, word)
            self.input_var.set(new_letters)
            self.update_rack(new_letters)
            self.update_all()
        
        tk.Button(dialog, text="Place", command=confirm_placement, font=("Helvetica", 12)).pack(pady=10)

    def preview_word_on_board(self, word, row, col, d):
        # Reset non-permanent cells.
        for coord, cell in self.cells.items():
            if coord not in self.placed_letters:
                if coord in self.special_cells:
                    cell_type = self.special_cells[coord]
                    if cell_type == "TW":
                        bg_color = "red"
                    elif cell_type == "DW":
                        bg_color = "orange"
                    elif cell_type == "DL":
                        bg_color = "green"
                    elif cell_type == "TL":
                        bg_color = "blue"
                    elif cell_type == "START":
                        bg_color = "purple"
                    else:
                        bg_color = "yellow"
                    cell.config(text=cell_type, fg="black", bg=bg_color)
                else:
                    cell.config(text="", fg="black", bg="white")
        # Show preview with red text.
        for i, letter in enumerate(word):
            if d == "H":
                r = row
                c = col + i
            else:
                r = row + i
                c = col
            if (r, c) in self.cells:
                self.cells[(r, c)].config(text=letter, fg="red")
            else:
                messagebox.showerror("Error", f"Cell ({r}, {c}) is off the board!")

    def place_word_on_board(self, word, row, col, d):
        for i, letter in enumerate(word):
            if d == "H":
                r = row
                c = col + i
            else:
                r = row + i
                c = col
            if (r, c) in self.cells:
                self.cells[(r, c)].config(text=letter, bg="lightgray", fg="black")
                self.placed_letters[(r, c)] = letter
            else:
                messagebox.showerror("Error", f"Cell ({r}, {c}) is off the board!")

    def remove_letters(self, original, word):
        original_list = list(original)
        for letter in word:
            for idx, orig_letter in enumerate(original_list):
                if orig_letter.lower() == letter.lower():
                    original_list.pop(idx)
                    break
        return "".join(original_list)

    def check_cell_availability(self):
        availability = {}
        board_size = 15
        for r in range(board_size):
            for c in range(board_size):
                coord = (r, c)
                if coord in self.placed_letters:
                    availability[coord] = {
                        "horiz_end": False,
                        "horiz_start": False,
                        "vert_end": False,
                        "vert_start": False
                    }
                else:
                    horiz_end = (c == 0) or ((r, c-1) not in self.placed_letters)
                    horiz_start = (c == board_size - 1) or ((r, c+1) not in self.placed_letters)
                    vert_end = (r == 0) or ((r-1, c) not in self.placed_letters)
                    vert_start = (r == board_size - 1) or ((r+1, c) not in self.placed_letters)
                    availability[coord] = {
                        "horiz_end": horiz_end,
                        "horiz_start": horiz_start,
                        "vert_end": vert_end,
                        "vert_start": vert_start
                    }
        return availability

    def check_availability_callback(self):
        avail = self.check_cell_availability()
        for coord, data in sorted(avail.items()):
            print(f"Cell {coord}: {data}")
        messagebox.showinfo("Availability", "Cell availability printed to console.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root)
    root.mainloop()
