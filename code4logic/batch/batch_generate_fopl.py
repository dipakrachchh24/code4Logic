# -------------------------------------------------------------------
# batch_generate_fopl.py
# Batch Processing Script for Generating First-Order Predicate Logic (FOPL)
# -------------------------------------------------------------------

import os
import csv
import json
from datetime import datetime, timezone

from inference.infer import translate_nl_to_fol
from utils.file_selector import select_input_file
from utils.output_namer import get_generation_output_paths
from utils.range_selector import parse_id_range


# =========================
# CONFIGURATION
# =========================

INPUT_DATA_PATH = "data/input_dataset.json"
OUTPUT_DIR = "results/generation"
# OUTPUT_CSV = "code4logic_fopl_outputs.csv"
# OUTPUT_JSON = "code4logic_fopl_outputs.json"


# =========================
# UTILS
# =========================

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def init_csv(path):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "input_text",
                "generated_fopl",
                "status",
                "timestamp"
            ])


def append_csv(path, row):
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# =========================
# CORE PIPELINE
# =========================

def generate_fopl_for_sample(sample):
    try:
        generated_fopl = translate_nl_to_fol(sample["input_text"])
        
        if generated_fopl is None:
            return None, "no_formula"

        return generated_fopl, "success"


    except Exception as e:
        return None, f"error: {str(e)}"


def run_batch():
    ensure_dirs()

    input_path, selected_index = select_input_file(
        data_dir="data",
        base_name="input_dataset"
    )

    dataset = load_dataset(input_path)

    # dataset = load_dataset(INPUT_DATA_PATH)
    csv_path, json_path = get_generation_output_paths(
        OUTPUT_DIR,
        base_name="code4logic_fopl_outputs",
        selected_index=selected_index
    )

    # csv_path = os.path.join(OUTPUT_DIR, OUTPUT_CSV)
    # json_path = os.path.join(OUTPUT_DIR, OUTPUT_JSON)

    init_csv(csv_path)

    all_results = []

    all_ids = [sample.get("id", idx) for idx, sample in enumerate(dataset)]

    user_range = input(
        "Enter ID range (empty = all, N = from n to end, range = A-B): "
    )

    try:
        selected_ids = set(parse_id_range(user_range, all_ids))
    except Exception as e:
        print(f"[ERROR] {e}")
        return


    for idx, sample in enumerate(dataset):
        sample_id = sample.get("id", idx)
        input_text = sample["input_text"]

        if sample_id not in selected_ids:
            continue

        generated_fopl, status = generate_fopl_for_sample(sample)

        timestamp = datetime.now(timezone.utc).isoformat()

        append_csv(csv_path, [
            sample_id,
            input_text,
            generated_fopl,
            status,
            timestamp
        ])

        all_results.append({
            "id": sample_id,
            "input_text": input_text,
            "generated_fopl": generated_fopl,
            "status": status,
            "timestamp": timestamp
        })

        if idx % 10 == 0:
            print(f"[{idx}] Processed")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    run_batch()
    