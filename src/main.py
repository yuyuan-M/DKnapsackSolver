# main.py
import tkinter as tk
from gui import DKnapsackGUI

def main():
    root = tk.Tk()
    app = DKnapsackGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()