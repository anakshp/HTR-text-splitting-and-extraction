import os
import csv
import pandas as pd
from thefuzz import fuzz
from natsort import natsorted


def split_lines(input_file, split_phrase, threshold=80, verdict_num=1):
    data = []

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    line_number = 0
    for line in lines:
        line_number += 1

        if fuzz.partial_ratio(split_phrase.lower(), line.lower()) >= threshold:
            verdict_num += 1

        data.append([
            verdict_num,
            os.path.basename(input_file).strip(),
            line_number,
            line.strip()
        ])

    return data, verdict_num


def split_files(folder_path, split_phrase, threshold=80, verdict_num=1):
    files = natsorted(os.listdir(folder_path))
    data = []

    output_folder = os.path.join(folder_path, "output")
    os.makedirs(output_folder, exist_ok=True)
    output_csv_path = os.path.join(output_folder, "verdict_output.csv")

    for file in files:
        file_path = os.path.join(folder_path, file)

        if not os.path.isfile(file_path):
            continue
        if file.lower().endswith(".csv"):
            continue

        file_data, verdict_num = split_lines(
            file_path,
            split_phrase,
            threshold=threshold,
            verdict_num=verdict_num
        )
        data.extend(file_data)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Verdict", "Page Name", "Serial Number", "Line"])
        writer.writerows(data)

    df = pd.DataFrame(
        data,
        columns=["Verdict", "Page Name", "Serial Number", "Line"]
    )

    print(f"CSV saved at: {output_csv_path}")
    return df


def folder_to_csv():
    folder_path = input("Enter folder path with HTR text files: ").strip()
    split_phrase = input("Enter split phrase (e.g. 'Vonnis'): ").strip()
    threshold = int(input("Enter fuzzy threshold (e.g. 80): ").strip())

    return split_files(folder_path, split_phrase, threshold)


if __name__ == "__main__":
    df = folder_to_csv()
    print(df.head())
