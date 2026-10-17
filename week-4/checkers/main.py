"""Start the Checkers application."""

import sys
import tkinter as tk

from gui import CheckersGUI


def main():
    if sys.platform == "darwin" and tk.TkVersion < 8.6:
        raise SystemExit(
            "This app needs Tk 8.6 or newer on macOS. The system Python "
            "uses older Tk. Use a Python installation with Tk 8.6, such as "
            "Miniforge or the installer from python.org. See README.md.")
    root = tk.Tk()
    CheckersGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
