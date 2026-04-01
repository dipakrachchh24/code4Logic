# -------------------------------------------------------------------
# batch_evaluate_equivalence.py
# Batch Processing Script for Evaluating Logical Equivalence of Generated FOPL
# -------------------------------------------------------------------

import os
import csv
import json
from datetime import datetime, timezone

from evaluation.logic_equivalence import check_equivalence
from utils.output_namer import get_evaluation_output_paths
from utils.file_selector import select_inputs_once


# =========================
# CONFIGURATION
# =========================

# GENERATION_INPUT_PATH = "results/generation/code4logic_fopl_outputs.json"
# GROUND_TRUTH_PATH = "data/ground_truth_fopl.json"

OUTPUT_DIR = "results/evaluation"
# OUTPUT_CSV = "logic_equivalence_results.csv"
# OUTPUT_JSON = "logic_equivalence_summary.json"


# =========================
# UTILS
# =========================

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def init_csv(path):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "generated_fopl",
                "ground_truth_fopl",
                "structural_match",
                "alpha_equivalent",
                "normalized_match",
                "status",
                "timestamp"
            ])


def append_csv(path, row):
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# =========================
# CORE EVALUATION
# =========================

def evaluate_sample(gen_entry, gt_map):
    sample_id = gen_entry["id"]
    gen_fopl = gen_entry["generated_fopl"]

    gt_fopl = gt_map.get(sample_id, None)
    if gt_fopl is None or gen_fopl is None:
        return None, None, None, "missing_fopl"

    try:
        result = check_equivalence(gen_fopl, gt_fopl)

        return (
            int(result.get("structural", False)),
            int(result.get("alpha", False)),
            int(result.get("normalized", False)),
            "success"
        )

    except Exception as e:
        return None, None, None, f"error: {str(e)}"


def run_batch_evaluation():
    ensure_dirs()

    try:
        generation_path, ground_truth_path, run_id = select_inputs_once(
            gen_dir="results/generation",
            gen_base="code4logic_fopl_outputs",
            gt_dir="data",
            gt_base="ground_truth_fopl"
        )
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    generation_data = load_json(generation_path)
    ground_truth_data = load_json(ground_truth_path)

    # generation_data = load_json(GENERATION_INPUT_PATH)
    # ground_truth_data = load_json(GROUND_TRUTH_PATH)

    gt_map = {item["id"]: item["fopl"] for item in ground_truth_data}

    csv_path, json_path = get_evaluation_output_paths(
        OUTPUT_DIR,
        base_name="logic_equivalence_results",
        run_id=run_id
    )

    # csv_path = os.path.join(OUTPUT_DIR, OUTPUT_CSV)
    # json_path = os.path.join(OUTPUT_DIR, OUTPUT_JSON)

    init_csv(csv_path)

    summary = {
        "total": 0,
        "structural_match": 0,
        "alpha_equivalent": 0,
        "normalized_match": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    for idx, gen_entry in enumerate(generation_data):
        sample_id = gen_entry["id"]

        structural, alpha, normalized, status = evaluate_sample(gen_entry, gt_map)

        timestamp = datetime.now(timezone.utc).isoformat()

        append_csv(csv_path, [
            sample_id,
            gen_entry["generated_fopl"],
            gt_map.get(sample_id),
            structural,
            alpha,
            normalized,
            status,
            timestamp
        ])

        if status == "success":
            summary["total"] += 1
            summary["structural_match"] += structural
            summary["alpha_equivalent"] += alpha
            summary["normalized_match"] += normalized

        if idx % 10 == 0:
            print(f"[{idx}] Evaluated")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    run_batch_evaluation()

# think about this later in the future if wanted to add.
# if gen_entry.get("status") != "success":
#     append_csv(csv_path, [
#         sample_id,
#         gen_entry["generated_fopl"],
#         gt_map.get(sample_id),
#         None,
#         None,
#         None,
#         "skipped",
#         timestamp
#     ])
#     continue
