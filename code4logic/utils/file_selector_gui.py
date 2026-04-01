import tkinter as tk
from tkinter import filedialog
import sys


def select_nl_fopl_dataset():
    """
    Open Windows file dialog to select NL–FOPL dataset file.
    Allowed formats: CSV, XLSX, XLS
    """

    root = tk.Tk()
    root.withdraw()  # hide root window

    file_path = filedialog.askopenfilename(
        title="Select Input NL–FOPL CSV or Excel File",
        initialdir=".",
        filetypes=(
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("All supported files", "*.csv *.xlsx *.xls"),
        )
    )

    root.destroy()

    if not file_path:
        print("[ERROR] No file selected. Exiting.")
        sys.exit(1)

    return file_path
