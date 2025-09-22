"""
Project: Serial_to_CSV
File: serial_gui.py
Created: 22.09.2025 13:58
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
import re
import os


class CSVLoggerTrainer(ctk.CTk):
    def __init__(self, serial_handler):
        super().__init__()
        self.title("ESP32 CSV Trainer")
        self.geometry("800x520")
        self.serial_handler = serial_handler

        # Data storage
        self.current_action_data = []       # Buffer for the currently recorded action
        self.labeled_data = {}              # Dict: label -> list of blocks, each block = list of rows
        self.noise_data = []                # Data collected between actions (noise/idle)
        self.recording = False

        # GUI Widgets
        self.text_box = ctk.CTkTextbox(self, width=760, height=340)
        self.text_box.pack(pady=(12, 6))

        # Controls frame
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=6, fill="x", padx=12)

        # Action name entry
        ctk.CTkLabel(self.control_frame, text="Action name:").grid(row=0, column=0, padx=(8, 4), pady=4, sticky="w")
        self.action_name_var = ctk.StringVar()
        self.action_entry = ctk.CTkEntry(self.control_frame, textvariable=self.action_name_var, width=220)
        self.action_entry.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="w")

        # Toggle record button (single button)
        self.toggle_button = ctk.CTkButton(self.control_frame, text="Start Recording", command=self.toggle_recording, width=160)
        self.toggle_button.grid(row=0, column=2, padx=8, pady=4)

        # Save all button
        self.save_button = ctk.CTkButton(self.control_frame, text="Save All Data", command=self.save_all_data, width=160)
        self.save_button.grid(row=0, column=3, padx=8, pady=4)

        # Instructions
        self.instr_label = ctk.CTkLabel(
            self,
            text="Workflow: type action name → Start Recording → perform action → Stop Recording → repeat. "
                 "Noise data is saved to noise.csv"
        )
        self.instr_label.pack(pady=(4, 8))

        # Register callback
        self.serial_handler.set_callback(self.new_line)

    # ---------- Recording control ----------
    def toggle_recording(self):
        if not self.recording:
            # Start recording
            action_name = self.action_name_var.get().strip()
            if not action_name:
                messagebox.showwarning("Missing action name", "Please enter an action name before starting recording.")
                return
            self.current_action_data = []
            self.recording = True
            self.toggle_button.configure(text="Stop Recording")
            self.text_box.insert("end", f"--- Started recording action '{action_name}' ---\n")
            self.text_box.see("end")
        else:
            # Stop recording
            self.recording = False
            self.toggle_button.configure(text="Start Recording")
            action_name = self.action_name_var.get().strip()
            if not self.current_action_data:
                self.text_box.insert("end", f"--- Stopped recording '{action_name}' (no samples collected) ---\n")
                self.text_box.see("end")
                return

            # Save into labeled_data dict under this action name
            if action_name not in self.labeled_data:
                self.labeled_data[action_name] = []
            # append block
            self.labeled_data[action_name].append(self.current_action_data.copy())

            self.text_box.insert(
                "end",
                f"--- Stopped recording and saved {len(self.current_action_data)} rows to action '{action_name}' ---\n"
            )
            self.text_box.see("end")

            self.current_action_data = []

    # ---------- Serial callback ----------
    def new_line(self, line):
        self.after(0, lambda: self._handle_line(line))

    def _handle_line(self, line):
        values = [v.strip() for v in line.split(",")]
        if len(values) >= 6:
            row = values[:6]
            if self.recording:
                self.current_action_data.append(row)
            else:
                # not recording -> treat as noise samples
                self.noise_data.append(row)

        self.text_box.insert("end", line + "\n")
        self.text_box.see("end")

    # ---------- Saving ----------
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        if not name:
            return "noise"
        name = re.sub(r"\s+", "_", name.strip())
        name = re.sub(r"[^\w\-.]", "", name)
        return name if name else "action"

    def save_all_data(self):
        if not self.labeled_data and not self.noise_data:
            messagebox.showwarning("No data", "No recorded data to save.")
            return

        folder = filedialog.askdirectory(title="Select folder to save CSV files")
        if not folder:
            return

        # Save per-action CSVs
        for label, blocks in self.labeled_data.items():
            safe = self._sanitize_filename(label)
            path = os.path.join(folder, f"{safe}.csv")
            try:
                with open(path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ax", "ay", "az", "gx", "gy", "gz"])
                    for block in blocks:
                        writer.writerows(block)
                        writer.writerow([])  # newline between blocks
                self.text_box.insert("end", f"Saved {sum(len(b) for b in blocks)} rows to {path}\n")
            except Exception as e:
                messagebox.showerror("Save error", f"Failed to write {path}:\n{e}")
                return

        # Save noise data
        if self.noise_data:
            noise_path = os.path.join(folder, "noise.csv")
            try:
                with open(noise_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ax", "ay", "az", "gx", "gy", "gz"])
                    writer.writerows(self.noise_data)
                self.text_box.insert("end", f"Saved {len(self.noise_data)} noise rows to {noise_path}\n")
            except Exception as e:
                messagebox.showerror("Save error", f"Failed to write {noise_path}:\n{e}")
                return

        self.text_box.insert("end", "--- All files saved ---\n")
        self.text_box.see("end")
        messagebox.showinfo("Saved", f"CSV files written to:\n{folder}")
