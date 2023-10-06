import csv
import os
import math
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def get_expected_probability(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))


def update_elo(r1, r2, outcome, goal_diff, k=40, goal_difference_weight=0.2, elo_sensitivity=1.5):
    expectation_A = get_expected_probability(r1, r2)
    expectation_B = get_expected_probability(r2, r1)
    g = 1 + goal_difference_weight * (math.log2(goal_diff + 1) - 1)

    update_value_A = k * (elo_sensitivity * (outcome - expectation_A)) * g
    update_value_B = k * (elo_sensitivity * ((1 - outcome) - expectation_B)) * g

    # Apply max Elo change cap
    update_value_A = max(min(update_value_A, k), -k)
    update_value_B = max(min(update_value_B, k), -k)

    return r1 + update_value_A, r2 + update_value_B


def read_csv_elo(file_name, player_name):
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip() == player_name:
                for i in range(len(row) - 1, 0, -1):
                    try:
                        return float(row[i])
                    except ValueError:
                        pass
    return 1000


def write_to_csv_file(filename, player_name, value, elo=False):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            pass

    with open(filename, "r") as f:
        lines = f.readlines()

    found = False
    updated_lines = []
    for line in lines:
        row = line.strip().split(",")
        if row and row[0].strip() == player_name:
            found = True
            if elo:
                row[-1] = str(value)
            else:
                row.append(str(value))
            updated_line = ",".join(row) + ","
            updated_lines.append(updated_line + "\n")
        else:
            updated_lines.append(line)

    if not found:
        updated_lines.append(f"{player_name},{value},\n")

    with open(filename, "w") as f:
        f.writelines(updated_lines)


class EloUpdater(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Elo Update for Online Soccer Manager")
        self.geometry("450x450")

        self.create_widgets()

    def create_widgets(self):
        self.label_player1 = ttk.Label(self, text="Joueur 1:")
        self.label_player1.grid(column=0, row=0, sticky=tk.W, padx=20, pady=10)

        self.entry_player1 = ttk.Entry(self)
        self.entry_player1.grid(column=1, row=0, padx=20, pady=10)


        self.label_player2 = ttk.Label(self, text="Joueur 2:")
        self.label_player2.grid(column=0, row=2, sticky=tk.W, padx=20, pady=10)

        self.entry_player2 = ttk.Entry(self)
        self.entry_player2.grid(column=1, row=2, padx=20, pady=10)


        self.label_score1 = ttk.Label(self, text="Buts marqués par Joueur 1:")
        self.label_score1.grid(column=0, row=4, sticky=tk.W, padx=20, pady=10)

        self.entry_score1 = ttk.Entry(self)
        self.entry_score1.grid(column=1, row=4, padx=20, pady=10)

        self.label_score2 = ttk.Label(self, text="Buts marqués par Joueur 2:")
        self.label_score2.grid(column=0, row=5, sticky=tk.W, padx=20, pady=10)

        self.entry_score2 = ttk.Entry(self)
        self.entry_score2.grid(column=1, row=5, padx=20, pady=10)

        self.submit_button = ttk.Button(self, text="Mettre à jour Elo", command=self.update_elo_ratings)
        self.submit_button.grid(column=0, row=6, columnspan=2, pady=20)

    def update_elo_ratings(self):
        player1 = self.entry_player1.get()
        player2 = self.entry_player2.get()
        score1 = int(self.entry_score1.get())
        score2 = int(self.entry_score2.get())

        goal_diff = abs(score1 - score2)
        outcome = 1 if score1 > score2 else 0 if score1 < score2 else 0.5

        elo_data = "elo_data.csv"

        all_player_ratings = {}
        with open(elo_data, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    for i in range(len(row) - 1, 0, -1):
                        try:
                            all_player_ratings[row[0].strip()] = float(row[i])
                            break
                        except ValueError:
                            pass

        player_rating1 = all_player_ratings.get(player1, 1000)
        player_rating2 = all_player_ratings.get(player2, 1000)
        print(str(player_rating1), str(player_rating2))

        new_rating1, new_rating2 = update_elo(player_rating1, player_rating2, outcome, goal_diff)

        write_to_csv_file("elo_data.csv", player1, int(new_rating1), elo=True)
        write_to_csv_file("elo_data.csv", player2, int(new_rating2), elo=True)

        messagebox.showinfo("Mise à jour réussie", f"Classement Elo mis à jour:\n{player1}: {new_rating1}\n{player2}: {new_rating2}")

if __name__ == "__main__":
    app = EloUpdater()
    app.mainloop()