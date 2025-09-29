"""
Project: Serial_to_CSV
File: split_csv_samples.py
Created: 29.09.2025 14:15
"""

import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def split_csv_samples(input_folder):
    """Split CSV files at blank lines into separate sample files."""
    for file in os.listdir(input_folder):
        if file.lower().endswith(".csv"):
            file_path = os.path.join(input_folder, file)
            base_name = os.path.splitext(file)[0]
            output_folder = os.path.join(input_folder, base_name)
            os.makedirs(output_folder, exist_ok=True)

            with open(file_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = None
                sample_rows = []
                sample_index = 1

                for row in reader:
                    if not any(row):  # blank line
                        if sample_rows:
                            output_path = os.path.join(
                                output_folder, f"{base_name}.s{sample_index}.csv"
                            )
                            with open(output_path, "w", newline="", encoding="utf-8") as out:
                                writer = csv.writer(out)
                                if header:
                                    writer.writerow(header)
                                writer.writerows(sample_rows)
                            sample_index += 1
                            sample_rows = []
                        continue

                    if header is None:
                        header = row
                    else:
                        sample_rows.append(row)

                if sample_rows:  # final sample
                    output_path = os.path.join(
                        output_folder, f"{base_name}.s{sample_index}.csv"
                    )
                    with open(output_path, "w", newline="", encoding="utf-8") as out:
                        writer = csv.writer(out)
                        if header:
                            writer.writerow(header)
                        writer.writerows(sample_rows)


def clean_csv_files(input_folder):
    """Remove blank lines and save cleaned CSVs into one 'cleaned' folder."""
    output_folder = os.path.join(input_folder, "cleaned")
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.lower().endswith(".csv"):
            file_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)

            with open(file_path, "r", newline="", encoding="utf-8") as f_in, \
                 open(output_path, "w", newline="", encoding="utf-8") as f_out:
                writer = csv.writer(f_out)
                for row in csv.reader(f_in):
                    if any(row):  # skip blank lines
                        writer.writerow(row)


# ---------------- GUI ---------------- #

def run_process():
    folder = folder_path.get()
    if not os.path.isdir(folder):
        messagebox.showerror("Error", "Invalid folder path.")
        return

    if mode.get() == "split":
        split_csv_samples(folder)
        messagebox.showinfo("Done", "CSV files split into sample folders.")
    else:
        clean_csv_files(folder)
        messagebox.showinfo("Done", "CSV files cleaned and saved in 'cleaned' folder.")


def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV Splitter / Cleaner")

    folder_path = tk.StringVar()
    mode = tk.StringVar(value="split")

    frm = ttk.Frame(root, padding=10)
    frm.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frm, text="Select folder:").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=folder_path, width=40).grid(row=0, column=1, padx=5)
    ttk.Button(frm, text="Browse", command=browse_folder).grid(row=0, column=2)

    ttk.Label(frm, text="Mode:").grid(row=1, column=0, sticky="w", pady=5)
    ttk.Radiobutton(frm, text="Split into samples", variable=mode, value="split").grid(row=1, column=1, sticky="w")
    ttk.Radiobutton(frm, text="Clean only (no blank lines)", variable=mode, value="clean").grid(row=2, column=1, sticky="w")

    ttk.Button(frm, text="Run", command=run_process).grid(row=3, column=0, columnspan=3, pady=10)

    root.mainloop()
