import json

def create_support_jsonl(input_file, fopl_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    with open(fopl_file, "r", encoding="utf-8") as f:
        fopl_data = json.load(f)

    # Map by id
    input_map = {item["id"]: item["input_text"] for item in input_data}
    fopl_map = {item["id"]: item["fopl"] for item in fopl_data}

    common_ids = sorted(set(input_map.keys()) & set(fopl_map.keys()))

    with open(output_file, "w", encoding="utf-8") as f:
        for idx, item_id in enumerate(common_ids, start=1):
            record = {
                "id": f"ex{idx}",
                "nl": input_map[item_id],
                "fol": fopl_map[item_id]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Created {output_file} with {len(common_ids)} lines.")


# Example usage
create_support_jsonl(
    "data/input_dataset_1.json",
    "data/ground_truth_fopl_1.json",
    "data/support_1.jsonl"
)