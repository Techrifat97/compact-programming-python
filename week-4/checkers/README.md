# Week 4 — Python Checkers Game

A local two-player Checkers game with a dark Tkinter interface. All game
logic works independently of the interface and uses Python's standard library.

**Course:** Compact Programming (Python)  
**University:** FH Dortmund  
**Programme:** Master's in Digital Transformation  
**Lecturer:** Prof. Galyna Tabunshchyk  
**Assignment:** Hometask3 — Week 4, Object-Oriented Programming

## Assignment objective

Model a Checkers game using the four required classes: `Player`, `Checker`,
`Board`, and `Game`. The application displays player and board information
after every move, allows a player to finish the game, and presents a final
summary. The optional graphical interface is implemented with Tkinter.

## OOP concepts demonstrated

- Classes and objects represent players, individual checkers, the board, and a game.
- Constructors (`__init__`) set each object's initial state.
- Instance attributes store names, positions, statistics, and game state.
- Instance methods use `self`, parameters, and return values to update objects.
- Modules and imports separate responsibilities.
- A `Game` contains players and a board; a `Board` contains checkers.
  Inheritance is unnecessary for these relationships.

## Features

- Resizable dark interface with board coordinates and distinct black/white pieces.
- Selected-checker highlighting, green destination markers, and a `K` for kings.
- Mandatory captures, multiple jumps, promotion, and automatic winner detection.
- Player names, current turn, move counts, remaining pieces, and live timers.
- New Game, Finish Game, and a final summary that can be reopened.
- Input validation and helpful messages for invalid clicks.
- No AI, network access, or third-party Python packages.

## Project structure

```text
week-4/checkers/
├── main.py             # Application entry point
├── player.py           # Player information and statistics
├── checker.py          # Checker position, directions, and promotion
├── board.py            # Board setup, legal moves, movement, and captures
├── game.py             # Turns, timing, results, and summary
├── gui.py              # Tkinter widgets, drawing, and input
├── test_checkers.py    # Standard-library unittest tests
└── README.md
```

## Installation and execution

Use Python 3.9 or newer with Tkinter and an available graphical desktop.
On macOS, use Tk 8.6 or newer.
No `pip install` command is needed.

From the repository root:

```bash
cd week-4/checkers
python3 main.py
```

On Windows, `py main.py` is an alternative if `python3` is unavailable.
Tkinter is normally included in the standard Python installers for macOS and
Windows. If `import tkinter` fails, install a Python distribution with Tcl/Tk
support. A terminal without a graphical desktop cannot display the interface,
but it can still run the logic tests.

**macOS system Python:** If the app reports an old Tk version, use another
Python installation. Apple's Tk 8.5 can display blank windows on this machine;
[Python's macOS Tk guidance](https://www.python.org/download/mac/tcltk/)
also advises against Apple's bundled Tk. With an existing Miniforge installation,
you can activate its base environment and use the same launch command:

```bash
conda activate base
python3 main.py
```

Alternatively, run `~/miniforge3/bin/python3 main.py` directly if that is where
your Miniforge is installed. The project does not change your Python installation.

## Game rules

1. Use a standard 8×8 board with play on dark squares only. Each side starts
   with 12 checkers. Black starts at the top and moves first, toward the bottom;
   White starts at the bottom and moves toward the top.
2. A normal checker moves one diagonal square forward into an empty square.
   It also captures forward only, jumping over one adjacent opponent into an
   empty square immediately beyond it. The captured piece is removed.
3. Captures are mandatory across the whole board. If any checker can capture,
   ordinary moves are unavailable. When several captures are available, the
   player may choose any of them; the longest sequence is not required.
4. After a jump, the same checker must keep capturing while another jump is
   available. The player may choose between available branches.
5. Reaching the opposite end promotes a normal checker to a king. In this
   implementation of English draughts (American checkers), **promotion ends
   the turn**, including during a capture sequence.
6. Kings move one diagonal square in either direction, or jump over one
   adjacent enemy. Kings cannot slide across multiple empty squares.
7. A player wins when the opponent has no checkers or no legal moves.
8. Finish Game manually terminates the game without declaring a winner.
   It remains available during a multiple-capture turn.

**Scope and simplifications:** The assignment mentions two possible board types
without defining them. This project implements only the standard 8×8 board.
Tournament clocks, repetition/no-progress draw rules, draw offers, resignation,
undo, saving, and AI are outside its scope. Players can use Finish Game to stop
a repeated position. There is no automatic draw detection.

**Statistics:** A move means one player's turn. A multiple-jump turn counts
once, on its first step; it still counts if the game is manually finished before
the remaining jumps. Total moves are the sum of both players' moves. Game
duration is elapsed time from game creation until it ends. Each player's turn
time is the accumulated time while it is their turn, including thinking time.
Timers stop when the game ends. There is no time limit. Confirmation and name
dialogs opened during an existing game do not pause its timers.

## How to play

1. Start the application and enter Player 1's name (Black), then Player 2's name
   (White). Names must contain 1–30 characters after trimming whitespace.
   Canceling the initial setup closes the application.
2. Click one of the current player's checkers. Its legal destinations appear
   as green markers. Click a marker to move.
3. Follow the status message when a capture or another jump is required.
   Invalid clicks leave the position unchanged.
4. Use Finish Game to stop, or play until a winner is detected. The summary
   shows the outcome, names, total and individual moves, remaining checkers,
   start/end times, total duration, and each player's turn time.
5. Use Game Summary to reopen a finished game's result. Use New Game to enter
   names and reset the board. Replacing an active game asks for confirmation
   and shows its terminated summary. Canceling either new-name dialog keeps
   an existing game. Closing an active game also offers to finish it and shows
   its summary before exiting.

## The four main classes

| Class | Responsibility |
| --- | --- |
| `Player` | Stores name, checker color, move count, result, and accumulated turn time. |
| `Checker` | Stores color, `(row, column)` position, and king status; supplies move directions and handles promotion. |
| `Board` | Owns an 8×8 list of squares containing checkers or `None`; initializes pieces, calculates legal moves, moves pieces, and removes captures. |
| `Game` | Owns the two players and board; manages the current player, forced jump sequences, move totals, times, game state, winner, and final summary. |

`Board.get_valid_moves()` examines one piece. `Board.get_legal_moves()` applies
mandatory captures across the board. `Game.make_move()` enforces ownership,
the current turn, and continuation with the same checker. The GUI calls these
methods rather than deciding which moves are legal itself.

Positions use zero-based `(row, column)` tuples. Row 0 is the top of the board
(displayed as rank 8), and column 0 is file `a`. For example, `(2, 1)` is `b6`.

## Testing

From `week-4/checkers/`, run:

```bash
python3 -m unittest -v
```

The tests require no graphical desktop. They cover initialization, both colors'
moves, invalid moves, ownership, captures, mandatory and multiple captures,
promotion ending a turn, king movement, both winning conditions, manual finish,
summaries, timing, and a fresh game after finishing.

For an interactive check, run `python3 main.py`, enter two names, and try a turn
for each side. Check the destination highlights and invalid-click messages,
resize the window, finish the game, review its summary, and start another game.
The rule-specific positions are checked by the automated tests.
