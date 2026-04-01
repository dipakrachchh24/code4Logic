import os
import csv
import json
import openpyxl
from utils.file_selector_gui import select_nl_fopl_dataset

# =========================
# CONFIG
# =========================


csv_or_excel_path = select_nl_fopl_dataset()
print("[INFO] Selected dataset file:")
print(csv_or_excel_path)
# CSV_INPUT_PATH = "data/dataset.csv"

OUTPUT_DIR = "data"

INPUT_BASE_NAME = "input_dataset"
GT_BASE_NAME = "ground_truth_fopl"


# =========================
# UTILS
# =========================

def get_next_index(output_dir, base_name):
    indices = []
    for fname in os.listdir(output_dir):
        if not fname.startswith(base_name):
            continue
        name = fname.replace(".json", "")
        parts = name.split("_")
        if len(parts) > 1 and parts[-1].isdigit():
            indices.append(int(parts[-1]))
        elif name == base_name:
            indices.append(1)
    return max(indices, default=0) + 1

def read_dataset(csv_or_excel_path):
    rows = []

    # ---------- CSV ----------
    if csv_or_excel_path.lower().endswith(".csv"):
        with open(csv_or_excel_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows

    # ---------- EXCEL ----------
    if csv_or_excel_path.lower().endswith((".xlsx", ".xls")):
        if openpyxl is None:
            raise ImportError(
                "openpyxl is required to read Excel files. "
                "Install it using: pip install openpyxl"
            )

        wb = openpyxl.load_workbook(csv_or_excel_path, data_only=True)
        sheet = wb.active

        headers = [cell.value for cell in sheet[1]]

        for row in sheet.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, row)))

        return rows

    # ---------- UNSUPPORTED ----------
    raise ValueError("Unsupported file format. Only CSV and Excel are allowed.")

# def read_csv(path):
#     rows = []
#     with open(path, newline="", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             rows.append(row)
#     return rows


# =========================
# MAIN LOGIC
# =========================

def build_datasets():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows = read_dataset(csv_or_excel_path)
    # rows = read_csv(CSV_INPUT_PATH)
    if not rows:
        print("[ERROR] CSV file is empty.")
        return

    # Decide index
    idx = get_next_index(OUTPUT_DIR, INPUT_BASE_NAME)

    # Output paths
    input_path = os.path.join(
        OUTPUT_DIR,
        f"{INPUT_BASE_NAME}.json" if idx == 1 else f"{INPUT_BASE_NAME}_{idx}.json"
    )

    gt_path = os.path.join(
        OUTPUT_DIR,
        f"{GT_BASE_NAME}.json" if idx == 1 else f"{GT_BASE_NAME}_{idx}.json"
    )

    input_data = []
    gt_data = []

    idx_counter = 1

    for row in rows:
        sample_id = (
            int(row["id"])
            if row.get("id") is not None
            else idx_counter
        )

        nl = row.get("NL")
        gt = row.get("FOL")

        input_data.append({
            "id": sample_id,
            "input_text": nl
        })

        gt_data.append({
            "id": sample_id,
            "fopl": gt
        })

        idx_counter += 1

    # Write files
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(input_data, f, indent=2, ensure_ascii=False)

    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(gt_data, f, indent=2, ensure_ascii=False)

    print(
        f"[SUCCESS] Dataset files created with index {idx}\n"
        f"  - {input_path}\n"
        f"  - {gt_path}"
    )


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    build_datasets()
