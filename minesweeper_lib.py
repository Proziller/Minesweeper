import tkinter as tk
from tkinter import messagebox
from random import sample
import os

class Minesweeper:
    def __init__(self, size=20, mines=100):
        self.size = size
        self.mines = mines
        self.gamemap = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.clicks = 0
        self.alive = True
        self.flags = set()
        self.revealed = set()
        self.labels = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.flags_leftLBL = None  # Flag count label (set in setup_gui)
        self.timer = 0  # Timer variable
        self.timer_running = False  # Flag to indicate if the timer is running
        self.started = False
        self.highscore = 10000000000

    def write_score(self):
        """Write the score (timer) to a text file when the game is won."""
        file_path = "minesweeper_scores.txt"
        
        # Write the current score (timer value) into the file
        with open(file_path, "a") as file:
            file.write(str(self.timer)+"\n")

    def read_scores(self):
        """Reads and prints the scores from the text file."""
        file_path = "minesweeper_scores.txt"
        
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                scores = file.readlines()
                for score in scores:
                    score_value = int(score.strip())  # Convert to int
                    if score_value < self.highscore:
                        self.highscore = score_value
        
        return self.highscore

    def gen_mines(self, safe_x, safe_y):
        """Generates mine positions avoiding the safe cell (first click) and its neighbors."""
        safe_zone = {(safe_x + dx, safe_y + dy)
                     for dx in (-1, 0, 1)
                     for dy in (-1, 0, 1)
                     if 0 <= safe_x + dx < self.size and 0 <= safe_y + dy < self.size}

        possible_positions = [
            (x, y) for y in range(self.size) for x in range(self.size)
            if (x, y) not in safe_zone
        ]
        mine_positions = sample(possible_positions, self.mines)

        for x, y in mine_positions:
            self.gamemap[y][x] = "M"

    def set_number(self, x, y):
        """Set number for a non-mine cell based on the count of adjacent mines."""
        if self.gamemap[y][x] == "M":
            return

        count = sum(
            self.gamemap[ny][nx] == "M"
            for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if 0 <= (nx := x + dx) < self.size and 0 <= (ny := y + dy) < self.size
        )
        self.gamemap[y][x] = count

    def generate_numbers(self):
        """Populate the board with numbers for non-mine cells."""
        for y in range(self.size):
            for x in range(self.size):
                self.set_number(x, y)

    def generate_map(self, safe_x, safe_y):
        """Generate the complete map with mines and numbers."""
        self.gamemap = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.flags.clear()
        self.revealed.clear()   
        self.alive = True
        self.clicks = 0

        self.gen_mines(safe_x, safe_y)
        self.generate_numbers()
        if self.gamemap[safe_y][safe_x] != 0:
            self.generate_map(safe_x, safe_y)

    def reveal_cell(self, x, y):
        """Recursively reveals cells. If the cell is empty, its neighbors are also revealed."""
        if (x, y) in self.revealed or (x, y) in self.flags:
            return
        self.revealed.add((x, y))
        label = self.labels[y][x]
        value = self.gamemap[y][x]

        color_map = {
            1: "#FA9770", 2: "#F56D61", 3: "#CB4942", 4: "#8C2927",
            5: "#721121", 6: "#721121", 7: "#721121", 8: "#721121"
        }

        if value == "M":
            label.config(text="💣", bg="red")
            self.alive = False
            self.game_over()
            return

        label.config(text=str(value) if value != 0 else "", bg=color_map.get(value, "#FFCF99"))

        if value == 0:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if (nx, ny) not in self.revealed:
                            self.reveal_cell(nx, ny)

    def left_click(self, x, y):
        """Handles left-click events."""
        if not self.alive:
            return
        if (x, y) in self.flags or (x, y) in self.revealed:
            return

        if self.clicks == 0:
            self.generate_map(x, y)
            self.started = True
            self.start_timer()  # Start the timer after the first click

        self.clicks += 1
        self.reveal_cell(x, y)

    def right_click(self, x, y):
        """Handles right-click events for flagging and updates flag counter."""
        if not self.alive or (x, y) in self.revealed:
            return

        label = self.labels[y][x]
        if (x, y) in self.flags:
            self.flags.remove((x, y))
            label.config(text="", bg="#8B3B47")
        else:
            if len(self.flags) < self.mines:  # Prevent more flags than mines
                self.flags.add((x, y))
                label.config(text="🏴", bg="#8B3B47")

        # Update the flags left label
        flags_left_text = f"Flags left: {self.mines - len(self.flags)}"
        self.flags_leftLBL.config(text=flags_left_text)

    def reset_game(self):
        """Resets the game board and updates the flag count display."""
        self.timer_running = False  # Stop the timer
        self.alive = True
        self.clicks = 0
        self.flags.clear()
        self.revealed.clear()
        self.gamemap = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.timer = 0  # Reset timer
        self.started = False

        # Reset all buttons
        for y in range(self.size):
            for x in range(self.size):
                btn = self.labels[y][x]
                if btn:
                    btn.config(text="", bg="#8B3B47")

        # Reset flags left label
        self.flags_leftLBL.config(text=f"Flags left: {self.mines}")

        # Reset the timer label
        self.timer_label.config(text="Time: 0")

    def setup_gui(self):
        """Initializes and runs the Tkinter GUI."""
        self.root = tk.Tk()
        self.root.title("Minesweeper")
        frame = tk.Frame(self.root)
        frame.pack()

        for y in range(self.size):
            for x in range(self.size):
                btn = tk.Label(frame, text="", width=4, height=2, relief="ridge", borderwidth=2, 
                            font=("Arial", 12), bg="#8B3B47", highlightbackground="#642B33", highlightthickness=0.5)
                btn.grid(row=y, column=x)
                btn.bind("<Button-1>", lambda e, x=x, y=y: self.left_click(x, y))
                btn.bind("<Button-3>", lambda e, x=x, y=y: self.right_click(x, y))
                btn.bind("<Enter>", lambda e, x=x, y=y: self.on_hover_enter(x, y))
                btn.bind("<Leave>", lambda e, x=x, y=y: self.on_hover_leave(x, y))
                self.labels[y][x] = btn

        # Add the flags left label
        self.flags_leftLBL = tk.Label(self.root, text=f"Flags left: {self.mines}", font=("Arial", 12), bg="#FA9770")
        self.flags_leftLBL.pack(pady=5)

        # Add the timer label
        self.timer_label = tk.Label(self.root, text="Time: 0", font=("Arial", 12), bg="#FA9770")
        self.timer_label.pack(pady=5)

        # Add a reset button with smaller size
        reset_button = tk.Button(self.root, text="Reset Game", font=("Arial", 10), bg="#FA9770", command=self.reset_game, width=10, height=1)
        reset_button.pack(pady=5)

        self.highscore_LBL = tk.Label(self.root, text="UwU", font=("Arial", 12), bg="#FA9770")
        self.highscore_LBL.pack(pady=5)
        
        self.root.configure(bg="#7F2735")  # Set background color of window


        self.root.mainloop()

    def on_hover_enter(self, x, y):
        """Handle the hover effect when the mouse enters a cell."""
        label = self.labels[y][x]
        if (x, y) not in self.revealed:  # Only apply hover effect if the cell is not revealed or flagged
            label.config(bg="#A05D67")  # Change color to something lighter

    def on_hover_leave(self, x, y):
        """Handle the hover effect when the mouse leaves a cell."""
        label = self.labels[y][x]
        if (x, y) not in self.revealed:  # Only reset if the cell is not revealed or flagged
            label.config(bg="#8B3B47")  # Reset to the original color

    def start_timer(self):
        self.update_highscore()
        self.timer = 0
        if self.timer_running == False:
            self.timer_running = True
            self.update_timer()

    def update_highscore(self):
        # Update the label with the current high score
        self.highscore_LBL.config(text=f"High Score: {self.highscore}")

    def update_timer(self):
        """Updates the timer label every second."""
        if self.size * self.size == self.mines + len(self.revealed):
            self.win_game()

        if self.started:
            self.timer += 1
            self.timer_label.config(text=f"Time: {self.timer}")
            self.root.after(1000, self.update_timer)  # Call this method again in 1 second

    def win_game(self):
        # Show a win message and write the score
        messagebox.showinfo("You are awesome", "You won")
        self.write_score()  # Write score when the game is won
        
        # Update highscore if the current score is lower
        if self.timer < self.highscore:
            self.highscore = self.timer
        
        # Update the highscore label
        self.update_highscore()
        
        self.reset_game()

    def game_over(self):
        """Show the game over screen when a mine is clicked."""
        self.started = False
        self.timer_running = False  # Stop the timer
        messagebox.showinfo("Game Over", "You clicked on a mine! Game Over!")
        self.reset_game()
