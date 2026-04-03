import os
import pandas as pd
import sys


# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from paths import CAMS_1DAY, CAMS_1MONTH


def get_files(time_step_folder):
    folder_path = os.path.join(time_step_folder, "processed_data")
    files_set = []
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            files_set.append(file)
    return set(files_set)


def compare_files_sets(month_set, day_set):
    only_in_month = month_set - day_set
    only_in_day = day_set - month_set
    in_both = month_set & day_set

    print(f"Files in both sets: {len(in_both)}")

    print(f"Files only in 1month: {only_in_month}")
    print(f"Files only in 1day: {only_in_day}")
    return


def main():

    day_files = get_files(CAMS_1DAY)
    month_files = get_files(CAMS_1MONTH)

    compare_files_sets(month_files, day_files)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
