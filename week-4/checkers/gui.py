"""Tkinter display and mouse interaction for the checkers game."""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from game import Game, format_duration


class CheckersGUI:
    BACKGROUND = "#111827"
    PANEL = "#1e293b"
    TEXT = "#f1f5f9"
    MUTED = "#b4c0d3"
    ACCENT = "#7dd3fc"

    def __init__(self, root):
        self.root = root
        self.game = None
        self.selected = None
        self.destinations = {}
        self.board_left = 0
        self.board_top = 0
        self.square_size = 1
        self.root.title("Hometask3 — Checkers")
        self.root.geometry("1000x760")
        self.root.minsize(860, 660)
        self.root.configure(bg=self.BACKGROUND)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._configure_styles()
        self._build_widgets()
        self.root.after(100, self.new_game)
        self.root.after(500, self._tick)

    def _configure_styles(self):
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background=self.BACKGROUND)
        style.configure("Card.TFrame", background=self.PANEL)
        style.configure("TLabel", background=self.BACKGROUND,
                        foreground=self.TEXT, font=("Arial", 11))
        style.configure("Title.TLabel", font=("Arial", 25, "bold"))
        style.configure("Muted.TLabel", foreground=self.MUTED)
        style.configure("Card.TLabel", background=self.PANEL)
        style.configure("Name.TLabel", background=self.PANEL,
                        font=("Arial", 13, "bold"))
        style.configure("Turn.TLabel", foreground=self.ACCENT,
                        font=("Arial", 15, "bold"))
        style.configure("TButton", font=("Arial", 11), padding=(12, 10),
                        background="#334155", foreground=self.TEXT)
        style.map("TButton", background=[("active", "#475569")],
                  foreground=[("disabled", "#8492a6")])

    def _build_widgets(self):
        header = ttk.Frame(self.root, padding=(24, 18, 24, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Checkers",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="WEEK 4  /  PYTHON OOP  /  TWO PLAYERS",
                  style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        content = ttk.Frame(self.root, padding=(16, 0, 24, 0))
        content.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(content, width=620, height=620,
                                bg=self.BACKGROUND, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.draw_board)
        self.canvas.bind("<Button-1>", self.on_board_click)

        sidebar = ttk.Frame(content, width=260, padding=(16, 18, 0, 0))
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="CURRENT TURN",
                  style="Muted.TLabel").pack(anchor="w")
        self.turn_label = ttk.Label(sidebar, text="Welcome",
                                    style="Turn.TLabel", wraplength=235)
        self.turn_label.pack(anchor="w", pady=(6, 18))
        self.player_labels = []
        for color in ("Black", "White"):
            card = ttk.Frame(sidebar, style="Card.TFrame", padding=12)
            card.pack(fill="x", pady=(0, 12))
            ttk.Label(card, text=color.upper(),
                      style="Card.TLabel").pack(anchor="w")
            name = ttk.Label(card, text="—", style="Name.TLabel",
                             wraplength=210)
            name.pack(anchor="w", pady=(4, 8))
            details = ttk.Label(card, text="", style="Card.TLabel",
                                justify="left")
            details.pack(anchor="w")
            self.player_labels.append((name, details))

        self.total_label = ttk.Label(sidebar, text="Total moves: 0")
        self.total_label.pack(anchor="w", pady=(2, 8))
        self.duration_label = ttk.Label(sidebar, text="Duration: 00:00:00")
        self.duration_label.pack(anchor="w", pady=(0, 18))
        ttk.Button(sidebar, text="New Game",
                   command=self.new_game).pack(fill="x", pady=(0, 8))
        self.finish_button = ttk.Button(sidebar, text="Finish Game",
                                        command=self.finish_game,
                                        state="disabled")
        self.finish_button.pack(fill="x", pady=(0, 8))
        self.summary_button = ttk.Button(sidebar, text="Game Summary",
                                         command=self.show_summary,
                                         state="disabled")
        self.summary_button.pack(fill="x")
        self.status = tk.StringVar(
            value="Enter the two player names to begin.")
        ttk.Label(self.root, textvariable=self.status, wraplength=810,
                  padding=(24, 10, 24, 16),
                  style="Muted.TLabel").pack(fill="x")

    def _ask_name(self, title, prompt, initial):
        while True:
            name = simpledialog.askstring(title, prompt, initialvalue=initial,
                                          parent=self.root)
            if name is None:
                return None
            name = name.strip()
            if name and len(name) <= 30:
                return name
            messagebox.showinfo(
                "Player name", "Enter a name of 1–30 characters.",
                parent=self.root)
            initial = name[:30]

    def new_game(self):
        if self.game is not None and self.game.state == "playing":
            if not messagebox.askyesno(
                    "New game", "Finish the current game and start another?",
                    parent=self.root):
                return
        black_default = "Player 1"
        white_default = "Player 2"
        if self.game is not None:
            black_default = self.game.players[0].name
            white_default = self.game.players[1].name

        black_name = self._ask_name(
            "Player 1", "Player 1 — Black (moves first):",
            black_default)
        if black_name is None:
            if self.game is None:
                self.root.destroy()
            return
        white_name = self._ask_name(
            "Player 2", "Player 2 — White:", white_default)
        if white_name is None:
            if self.game is None:
                self.root.destroy()
            return
        if self.game is not None and self.game.state == "playing":
            self.game.finish()
            self.show_summary()
        self.game = Game(black_name, white_name)
        self.selected = None
        self.destinations = {}
        self.update_information()
        self._set_turn_message()
        self.draw_board()

    def _set_turn_message(self):
        if self.game.state != "playing":
            if self.game.winner is not None:
                self.status.set(
                    f"{self.game.winner.name} wins! "
                    "Start a new game to play again.")
            else:
                self.status.set(
                    "Game manually terminated. No winner was declared.")
        elif self.game.forced_position is not None:
            self.status.set(
                "Another jump is required. Use the selected checker.")
        else:
            moves = self.game.get_legal_moves()
            capture_required = False
            for destinations in moves.values():
                for jumped in destinations.values():
                    if jumped is not None:
                        capture_required = True
            if capture_required:
                self.status.set(
                    "A capture is required. Select a capturing checker.")
            else:
                self.status.set(
                    "Select a checker, then a highlighted destination.")

    def on_board_click(self, event):
        if self.game is None:
            return
        if self.game.state != "playing":
            self.status.set(
                "This game has ended. Click New Game to play again.")
            return
        column = int((event.x - self.board_left) // self.square_size)
        row = int((event.y - self.board_top) // self.square_size)
        position = (row, column)
        if not self.game.board.is_inside(position):
            self.status.set("Click a square inside the board.")
            return

        if self.selected is not None and position in self.destinations:
            try:
                self.game.make_move(self.selected, position)
            except ValueError as error:
                self.status.set(str(error))
                return
            self.selected = self.game.forced_position
            self.destinations = self.game.get_legal_moves().get(
                self.selected, {})
            self.update_information()
            self._set_turn_message()
            self.draw_board()
            if self.game.state != "playing":
                self.show_summary()
            return

        checker = self.game.board.get_checker(position)
        legal_moves = self.game.get_legal_moves()
        if position in legal_moves:
            self.selected = position
            self.destinations = legal_moves[position]
            self.status.set(
                "Click a highlighted destination to move this checker.")
        elif self.game.forced_position is not None:
            self.status.set(
                "You must complete the jumps with the selected checker.")
        elif (checker is not None
              and checker.color != self.game.current_player.color):
            self.status.set(
                "That checker belongs to your opponent. Select your own.")
        elif checker is not None:
            self.status.set(
                "This checker cannot move now. Check for mandatory captures.")
        else:
            self.status.set(
                "Choose a highlighted destination, or a movable checker.")
        self.draw_board()

    def draw_board(self, event=None):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.square_size = max(1, (min(width, height) - 48) / 8)
        board_size = self.square_size * 8
        self.board_left = (width - board_size) / 2
        self.board_top = (height - board_size) / 2
        for row in range(8):
            for column in range(8):
                position = (row, column)
                x = self.board_left + column * self.square_size
                y = self.board_top + row * self.square_size
                if (row + column) % 2 == 0:
                    color = "#cbd5e1"
                else:
                    color = "#52677d"
                if position == self.selected:
                    color = "#987b36"
                self.canvas.create_rectangle(
                    x, y, x + self.square_size, y + self.square_size,
                    fill=color, outline=color)
                if self.game is not None:
                    checker = self.game.board.get_checker(position)
                    if checker is not None:
                        self._draw_checker(checker, x, y)
                if position in self.destinations:
                    center_x = x + self.square_size / 2
                    center_y = y + self.square_size / 2
                    radius = self.square_size * 0.16
                    self.canvas.create_oval(
                        center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        fill="#86efac", outline="#14532d", width=2)
        for index in range(8):
            center = (index + 0.5) * self.square_size
            self.canvas.create_text(
                self.board_left - 14, self.board_top + center,
                text=str(8 - index), fill=self.MUTED, font=("Arial", 10))
            self.canvas.create_text(
                self.board_left + center, self.board_top + board_size + 14,
                text="abcdefgh"[index], fill=self.MUTED,
                font=("Arial", 10))

    def _draw_checker(self, checker, x, y):
        margin = self.square_size * 0.13
        if checker.color == "black":
            fill = "#151923"
            outline = "#94a3b8"
            king_text = "#facc15"
        else:
            fill = "#f7f3e8"
            outline = "#ffffff"
            king_text = "#795400"
        self.canvas.create_oval(
            x + margin, y + margin,
            x + self.square_size - margin, y + self.square_size - margin,
            fill=fill, outline=outline, width=2)
        inner = self.square_size * 0.23
        if checker.is_king:
            ring_color = "#d6ad49"
        else:
            ring_color = "#718096"
        self.canvas.create_oval(
            x + inner, y + inner,
            x + self.square_size - inner, y + self.square_size - inner,
            outline=ring_color, width=2)
        if checker.is_king:
            self.canvas.create_text(
                x + self.square_size / 2, y + self.square_size / 2,
                text="K", fill=king_text,
                font=("Arial", max(12, int(self.square_size * 0.3)), "bold"))

    def update_information(self):
        if self.game is None:
            return
        playing = self.game.state == "playing"
        if playing:
            player = self.game.current_player
            self.turn_label.configure(
                text=f"{player.name}\n{player.color.title()} to move")
        elif self.game.winner is not None:
            self.turn_label.configure(text="Game complete")
        else:
            self.turn_label.configure(text="Game finished")

        for index, player in enumerate(self.game.players):
            name_label, details_label = self.player_labels[index]
            name_label.configure(text=player.name)
            count = len(self.game.board.get_checkers(player.color))
            turn_time = format_duration(self.game.get_player_time(player))
            details_label.configure(
                text=f"Moves: {player.moves}    Checkers: {count}\n"
                     f"Turn time: {turn_time}")
        self.total_label.configure(
            text=f"Total moves: {self.game.total_moves}")
        self.duration_label.configure(
            text=f"Duration: {format_duration(self.game.get_duration())}")
        if playing:
            self.finish_button.configure(state="normal")
            self.summary_button.configure(state="disabled")
        else:
            self.finish_button.configure(state="disabled")
            self.summary_button.configure(state="normal")

    def _tick(self):
        self.update_information()
        self.root.after(500, self._tick)

    def finish_game(self):
        if self.game is None or self.game.state != "playing":
            return
        if messagebox.askyesno(
                "Finish game", "Finish this game without declaring a winner?",
                parent=self.root):
            self.game.finish()
            self.selected = None
            self.destinations = {}
            self.update_information()
            self._set_turn_message()
            self.draw_board()
            self.show_summary()

    def show_summary(self):
        if self.game is not None:
            messagebox.showinfo("Game summary", self.game.get_summary(),
                                parent=self.root)

    def close(self):
        if self.game is not None and self.game.state == "playing":
            if not messagebox.askyesno(
                    "Close Checkers", "Finish this game and close the app?",
                    parent=self.root):
                return
            self.game.finish()
            self.show_summary()
        self.root.destroy()
