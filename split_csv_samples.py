"""
Project: Serial_to_CSV
File: split_csv_samples.py
Created: 29.09.2025 14:15
"""

import os
import csv

def split_csv_samples(input_folder):
    # Loop through all files in the given folder
    for file in os.listdir(input_folder):
        if file.lower().endswith(".csv"):
            file_path = os.path.join(input_folder, file)
            base_name = os.path.splitext(file)[0]
            output_folder = os.path.join(input_folder, base_name)

            # Create folder for split files if not exists
            os.makedirs(output_folder, exist_ok=True)

            with open(file_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = None
                sample_rows = []
                sample_index = 1

                for row in reader:
                    # Check if row is empty (blank line → new sample)
                    if not any(row):
                        if sample_rows:
                            # Write current sample to file
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

                    # First non-empty row = header
                    if header is None:
                        header = row
                    else:
                        sample_rows.append(row)

                # Write last sample if file didn’t end with blank line
                if sample_rows:
                    output_path = os.path.join(
                        output_folder, f"{base_name}.s{sample_index}.csv"
                    )
                    with open(output_path, "w", newline="", encoding="utf-8") as out:
                        writer = csv.writer(out)
                        if header:
                            writer.writerow(header)
                        writer.writerows(sample_rows)


if __name__ == "__main__":
    folder_path = input("Enter the folder path containing CSV files: ").strip()
    if os.path.isdir(folder_path):
        split_csv_samples(folder_path)
        print("✅ Splitting complete.")
    else:
        print("❌ Invalid folder path.")
