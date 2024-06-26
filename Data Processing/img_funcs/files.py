import os
import re
from datetime import datetime

# Regular expression pattern to match filenames and extract date and time
pattern = re.compile(r'\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}\+(tomato|disease).(json|png)')

def get_file_date(filename):
    match = pattern.match(filename)
    if match:
        date_str = match.group().rsplit('+', 1)[0]
        return datetime.strptime(date_str, '%d-%m-%Y_%H-%M-%S')
    return None

def get_latest_files(directory, n, typ):
    try:
        files = os.listdir(directory)
    except FileNotFoundError:
        return ([], [])
    json_files = [f for f in files if f.endswith(typ + '.json') and pattern.match(f)]
    png_files = [f for f in files if f.endswith(typ + '.png') and pattern.match(f)]
    
    # Sort files by date
    json_files.sort(key=get_file_date, reverse=True)
    png_files.sort(key=get_file_date, reverse=True)

    # Get the latest n files of each type
    latest_json_files = json_files[:n] if json_files else []
    latest_png_files = png_files[:n] if png_files else []

    return latest_json_files, latest_png_files

def clean_old_files(directory, n):
    json_files, png_files = get_latest_files(directory, n)

    all_files = os.listdir(directory)
    json_files_to_keep = set(json_files)
    png_files_to_keep = set(png_files)

    # Remove old JSON files
    for file in all_files:
        if file.endswith('.json') and file not in json_files_to_keep:
            os.remove(os.path.join(directory, file))
            print(f"Deleted old JSON file: {file}")

    # Remove old PNG files
    for file in all_files:
        if file.endswith('.png') and file not in png_files_to_keep:
            os.remove(os.path.join(directory, file))
            print(f"Deleted old PNG file: {file}")
