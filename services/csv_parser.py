import csv
import io
from pathlib import Path


def parse_csv(file_or_path, has_header=True):
    """Parses a CSV file (from a file path or file-like object) and determines the table type.

    Args:
        file_or_path: Either a string (file path) or a file-like object (e.g., FileStorage).
        has_header: A boolean flag indicating whether the CSV file has a header row.

    Returns:
        tuple: A tuple containing the recognized table name (str) and the parsed data (list of lists).
    """

    # Determine input type and read CSV data
    if isinstance(file_or_path, str) or isinstance(file_or_path, Path):
        file_path = Path(file_or_path)
        file_name = file_path.name
        with open(file_path, 'r', encoding="utf-8", newline=None) as f:
            reader = csv.reader(f)
            if not has_header:
                next(reader, None)  # Skip the first row if it's not a header
            data = list(reader)
    elif hasattr(file_or_path, 'filename'):
        file_name = file_or_path.filename
        stream = io.StringIO(file_or_path.stream.read().decode("utf-8"), newline=None)
        reader = csv.reader(stream)
        if not has_header:
            next(reader, None)  # Skip the first row if it's not a header
        data = list(reader)
    else:
        raise ValueError("Input must be a file path or a file-like object")

    # Table recognition (rest of this part remains the same)
    file_base_name = file_name.split('.')[0].lower()  # Extract base name before extension
    name_to_table = {
        "jobs": "Job",
        "departments": "Department",
        "employee": "Employee"
    }

    recognized_table = None
    for name in name_to_table:
        if name in file_base_name:
            recognized_table = name_to_table[name]
            break

    if recognized_table is None:
        raise ValueError("File name must contain one of the recognized names: 'jobs', 'departments', or 'employees'")

    return recognized_table, data

