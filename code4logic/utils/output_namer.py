import os


def _next_available_index(output_dir, base_name):
    indices = []
    for fname in os.listdir(output_dir):
        if not fname.startswith(base_name):
            continue
        name = fname.replace(".csv", "").replace(".json", "")
        parts = name.split("_")
        if parts[-1].isdigit():
            indices.append(int(parts[-1]))
    return max(indices, default=0) + 1


def get_generation_output_paths(
    output_dir: str,
    base_name: str,
    selected_index: int | None
):
    """
    Decide output file names.

    Rules:
    - If selected_index is None:
        → auto-increment index (1,2,3...)
    - If selected_index is provided:
        → use that index (overwrite if exists)
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if selected_index is None:
        run_id = _next_available_index(output_dir, base_name)
    else:
        run_id = selected_index

    csv_path = os.path.join(
        output_dir, f"{base_name}_{run_id}.csv"
    )
    json_path = os.path.join(
        output_dir, f"{base_name}_{run_id}.json"
    )

    print(
        f"[INFO] Output files will be saved as:\n"
        f"       {base_name}_{run_id}.csv\n"
        f"       {base_name}_{run_id}.json"
    )

    return csv_path, json_path

def get_evaluation_output_paths(
    output_dir: str,
    base_name: str,
    run_id: int
):
    """
    Decide output file names for evaluation results.

    Rules:
    - run_id MUST be provided
    - Uses the same run_id as generation
    - Overwrites existing files if present
    """

    if run_id is None:
        raise ValueError(
            "Evaluation run_id must be provided to match generation index."
        )
    
    os.makedirs(output_dir, exist_ok=True)
    if run_id == 0:
        csv_path = os.path.join(
            output_dir, f"{base_name}.csv"
        )

        json_path = os.path.join(
            output_dir, f"{base_name}.json"
        )

        print(
            f"[INFO] Evaluation output files will be saved as:\n"
            f"       {base_name}.csv\n"
            f"       {base_name}.json"
        )

        return csv_path, json_path

    csv_path = os.path.join(
        output_dir, f"{base_name}_{run_id}.csv"
    )

    json_path = os.path.join(
        output_dir, f"{base_name}_{run_id}.json"
    )

    print(
        f"[INFO] Evaluation output files will be saved as:\n"
        f"       {base_name}_{run_id}.csv\n"
        f"       {base_name}_{run_id}.json"
    )

    return csv_path, json_path

# # -------------------------------------------------------------------
# # output_namer.py
# # Centralized output naming logic with automatic run indexing
# # -------------------------------------------------------------------

# import os


# def _get_next_run_index(output_dir, base_name):
#     """
#     Find the next available run index for files like:
#     base_name_1.csv, base_name_2.json, etc.
#     """
#     if not os.path.exists(output_dir):
#         return 1

#     indices = []

#     for fname in os.listdir(output_dir):
#         if not fname.startswith(base_name):
#             continue

#         name = fname.replace(".csv", "").replace(".json", "")
#         parts = name.split("_")

#         if parts[-1].isdigit():
#             indices.append(int(parts[-1]))

#     return max(indices, default=0) + 1


# # -------------------------------------------------------------------
# # Generation output paths
# # -------------------------------------------------------------------

# def get_generation_output_paths(output_dir, base_name):
#     """
#     Decide output file names for generation results.
#     Adds automatic run index.
#     """

#     run_id = _get_next_run_index(output_dir, base_name)

#     csv_path = os.path.join(
#         output_dir, f"{base_name}_{run_id}.csv"
#     )

#     json_path = os.path.join(
#         output_dir, f"{base_name}_{run_id}.json"
#     )

#     return csv_path, json_path


# # -------------------------------------------------------------------
# # Evaluation output paths
# # -------------------------------------------------------------------

# def get_evaluation_output_paths(output_dir, base_name):
#     """
#     Decide output file names for evaluation results.
#     Adds automatic run index.
#     """

#     run_id = _get_next_run_index(output_dir, base_name)

#     csv_path = os.path.join(
#         output_dir, f"{base_name}_{run_id}.csv"
#     )

#     json_path = os.path.join(
#         output_dir, f"{base_name}_{run_id}.json"
#     )

#     return csv_path, json_path


# # -------------------------------------------------------------------
# # output_namer.py
# # Centralized output file naming logic
# # -------------------------------------------------------------------

# import os


# def get_generation_output_paths(output_dir, base_name):
#     """
#     Decide output file names for generation results.

#     Args:
#         output_dir: directory where files are stored
#         base_name: logical base name (e.g., 'code4logic_fopl_outputs')

#     Returns:
#         (csv_path, json_path)
#     """

#     csv_path = os.path.join(output_dir, f"{base_name}.csv")
#     json_path = os.path.join(output_dir, f"{base_name}.json")

#     return csv_path, json_path


# def get_evaluation_output_paths(output_dir, base_name):
#     """
#     Decide output file names for evaluation results.

#     Args:
#         output_dir: directory where files are stored
#         base_name: logical base name (e.g., 'logic_equivalence_results')

#     Returns:
#         (csv_path, json_path)
#     """

#     csv_path = os.path.join(output_dir, f"{base_name}.csv")
#     json_path = os.path.join(output_dir, f"{base_name}.json")

#     return csv_path, json_path
