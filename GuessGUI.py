
import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import json
import os

SAVE_FILE = "profiles.json"

class GuessingGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")

        self.profiles = {}
        self.current_profile = None
        self.secret_number = None
        self.attempts = 0

        self.build_gui()
        self.root.bind("<Return>", lambda event: self.check_guess())
        self.load_profiles()

        if self.profiles:
            first_profile = list(self.profiles.keys())[0]
            self.profile_var.set(first_profile)
            self.switch_profile(first_profile)
        else:
            self.label.config(text="Create a profile to start!")

    def build_gui(self):
        profile_frame = tk.Frame(self.root)
        profile_frame.pack(pady=5)

        tk.Label(profile_frame, text="Profile:").pack(side=tk.LEFT)
        self.profile_var = tk.StringVar()
        self.profile_menu = tk.OptionMenu(profile_frame, self.profile_var, ())
        self.profile_menu.pack(side=tk.LEFT)

        self.profile_var.trace('w', self.on_profile_change)

        self.add_profile_btn = tk.Button(profile_frame, text="Add Profile", command=self.add_profile)
        self.add_profile_btn.pack(side=tk.LEFT, padx=5)

        difficulty_frame = tk.Frame(self.root)
        difficulty_frame.pack(pady=5)
        tk.Label(difficulty_frame, text="Difficulty:").pack(side=tk.LEFT, padx=(0, 5))

        self.difficulty = tk.StringVar(value="Easy")
        self.difficulty_menu = tk.OptionMenu(difficulty_frame, self.difficulty, "Easy", "Medium", "Hard")
        self.difficulty_menu.pack(side=tk.LEFT)
        self.difficulty.trace('w', self.update_difficulty_description)
        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=5)

        self.label = tk.Label(self.root, text="Select difficulty and start the game!")
        self.label.pack(pady=5)

        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.entry.config(state=tk.DISABLED)

        self.guess_button = tk.Button(self.root, text="Guess", command=self.check_guess, state=tk.DISABLED)
        self.guess_button.pack(pady=5)

        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack(pady=5)

        self.guess_counter_label = tk.Label(self.root, text="Guesses this game: 0")
        self.guess_counter_label.pack(pady=2)

        self.stats_label = tk.Label(self.root, text="Best Score: N/A")
        self.stats_label.pack(pady=10)

        self.scoreboard_label = tk.Label(self.root, text="📜 Game History")
        self.scoreboard_label.pack()

        self.scoreboard = tk.Text(self.root, height=15, width=60, state=tk.DISABLED)
        self.scoreboard.pack(pady=5)

        self.clear_button = tk.Button(self.root, text="Reset Scoreboard", command=self.clear_scoreboard)
        self.clear_button.pack(pady=5)

        # Confetti canvas (starts hidden)
        self.confetti_canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.confetti_canvas.place_forget()

        self.update_difficulty_description()

    def update_difficulty_description(self, *args):
        level = self.difficulty.get()
        if level == "Easy":
            text = "Easy: Guess a number between 1 and 10"
        elif level == "Medium":
            text = "Medium: Guess a number between 1 and 50"
        elif level == "Hard":
            text = "Hard: Guess a number between 1 and 100"
        else:
            text = ""
        self.label.config(text=text)

    def add_profile(self):
        name = simpledialog.askstring("New Profile", "Enter profile name:")
        if name:
            if name in self.profiles:
                messagebox.showerror("Error", "Profile already exists.")
                return
            self.profiles[name] = {
                "best_score": None,
                "games_played": 0,
                "game_history": []
            }
            self.save_profiles()
            self.update_profile_menu()
            self.profile_var.set(name)
            self.switch_profile(name)

    def update_profile_menu(self):
        menu = self.profile_menu["menu"]
        menu.delete(0, "end")
        for profile in self.profiles.keys():
            menu.add_command(label=profile, command=lambda p=profile: self.profile_var.set(p))

    def on_profile_change(self, *args):
        selected = self.profile_var.get()
        if selected != self.current_profile:
            self.switch_profile(selected)

    def switch_profile(self, profile_name):
        if profile_name not in self.profiles:
            return
        self.current_profile = profile_name
        profile_data = self.profiles[profile_name]

        best = profile_data["best_score"]
        best_text = f"Best Score: {best}" if best is not None else "Best Score: N/A"
        self.stats_label.config(text=best_text)

        self.update_difficulty_description()
        self.entry.config(state=tk.DISABLED)
        self.guess_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.difficulty_menu.config(state="normal")

        self.update_scoreboard()
        self.result_label.config(text="")
        self.attempts = 0
        self.secret_number = None

    def load_profiles(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                try:
                    self.profiles = json.load(f)
                except json.JSONDecodeError:
                    self.profiles = {}
            self.update_profile_menu()
        else:
            self.profiles = {}

    def save_profiles(self):
        with open(SAVE_FILE, "w") as f:
            json.dump(self.profiles, f, indent=2)

    def start_game(self):
        self.set_secret_number()
        self.label.config(text=self.get_range_text())

        self.guess_button.config(state=tk.NORMAL)
        self.guess_counter_label.config(text="Guesses this game: 0")
        self.entry.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.entry.config(bg="white")  # ✅ Reset background color

        self.start_button.config(state=tk.DISABLED)
        self.difficulty_menu.config(state="disabled")
        self.result_label.config(text="Game started! Make your guess.")

        self.root.bind("<Return>", lambda event: self.check_guess())  # Re-enable Enter

    def set_secret_number(self):
        level = self.difficulty.get()
        if level == "Easy":
            self.secret_number = random.randint(1, 10)
        elif level == "Medium":
            self.secret_number = random.randint(1, 50)
        elif level == "Hard":
            self.secret_number = random.randint(1, 100)

    def get_range_text(self):
        level = self.difficulty.get()
        if level == "Easy":
            return "Guess a number between 1 and 10:"
        elif level == "Medium":
            return "Guess a number between 1 and 50:"
        elif level == "Hard":
            return "Guess a number between 1 and 100:"
        return "Guess a number:"

    def flash_entry(self, color, stay=False):
        if stay:
            self.entry.config(bg=color)
        else:
            original_color = self.entry.cget("bg")
            self.entry.config(bg=color)
            self.root.after(150, lambda: self.entry.config(bg=original_color))

    def check_guess(self):
        try:
            guess = int(self.entry.get())
            level = self.difficulty.get()
            min_val, max_val = 1, 10  # Default range

            if level == "Medium":
                max_val = 50
            elif level == "Hard":
                max_val = 100

            if not (min_val <= guess <= max_val):
                self.result_label.config(text=f"Please enter a number between {min_val} and {max_val}.")
                self.flash_entry("red")
                self.entry.delete(0, tk.END)
                return

            self.attempts += 1
            self.guess_counter_label.config(text=f"Guesses this game: {self.attempts}")
            profile = self.profiles[self.current_profile]

            if guess == self.secret_number:
                result = f"🎉 Correct! You guessed it in {self.attempts} attempts."
                self.show_confetti()

                if profile["best_score"] is None or self.attempts < profile["best_score"]:
                    profile["best_score"] = self.attempts
                    result += "\n🏆 New best score!"

                profile["games_played"] += 1
                profile["game_history"].append({
                    "Game": profile["games_played"],
                    "Guesses": self.attempts,
                    "Number": self.secret_number,
                    "Difficulty": level
                })

                self.result_label.config(text=result)
                self.stats_label.config(text=f"Best Score: {profile['best_score']}")
                
                self.guess_button.config(state=tk.DISABLED)
                self.entry.config(state=tk.DISABLED)
                self.start_button.config(state=tk.NORMAL)
                self.difficulty_menu.config(state="normal")  # ✅ Re-enable difficulty selector
                self.update_difficulty_description()

                self.root.unbind("<Return>")  # Disable Enter after game ends

                self.update_scoreboard()
                self.save_profiles()

            elif abs(guess - self.secret_number) <= 5:
                self.flash_entry("yellow")
                direction = "Too low!" if guess < self.secret_number else "Too high!"
                self.result_label.config(text=f"Very close! {direction}")

            elif guess < self.secret_number:
                self.flash_entry("yellow")  # 👈 ADD THIS
                self.result_label.config(text="Too low.")

            else:
                self.flash_entry("yellow")  # 👈 ADD THIS
                self.result_label.config(text="Too high.")


        except ValueError:
            self.result_label.config(text="Please enter a valid number.")

        self.entry.delete(0, tk.END)

    def update_scoreboard(self):
        self.scoreboard.config(state=tk.NORMAL)
        self.scoreboard.delete("1.0", tk.END)  # 🧽 Clear previous content

        if self.current_profile is None:
            self.scoreboard.insert(tk.END, "No profile selected.\n")
        else:
            history = self.profiles[self.current_profile]["game_history"]
            if not history:
                self.scoreboard.insert(tk.END, "No games played yet.\n")
            else:
                for game in history:
                    diff = game.get("Difficulty", "N/A")
                    line = f"Game {game['Game']} [{diff}]: {game['Guesses']} guesses (Number was {game['Number']})\n"
                    self.scoreboard.insert(tk.END, line)

        self.scoreboard.config(state=tk.DISABLED)

    def show_confetti(self):
        self.confetti_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.confetti_canvas.lift(self.root)
        self.confetti_canvas.delete("all")

        # Get canvas size
        self.root.update_idletasks()  # Make sure geometry is updated
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Display large "GG!" text centered
        self.confetti_canvas.create_text(
            width // 2, height // 2,
            text="Good Game!",
            font=("Arial", 58, "bold"),
            fill="green"
        )

        self.root.after(1500, self.confetti_canvas.place_forget)

    def clear_scoreboard(self):
        if self.current_profile is None:
            messagebox.showwarning("No profile", "No profile selected to reset scoreboard.")
            return

        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the scoreboard for this profile?")
        if confirm:
            profile = self.profiles[self.current_profile]
            profile["game_history"].clear()
            profile["games_played"] = 0
            profile["best_score"] = None

            self.stats_label.config(text="Best Score: N/A")
            self.update_scoreboard()
            self.result_label.config(text="Scoreboard reset.")
            self.save_profiles()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = GuessingGameGUI(root)
    root.mainloop()
