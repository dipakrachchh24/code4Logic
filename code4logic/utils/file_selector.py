import os
import sys


def select_input_file(
    data_dir: str,
    base_name: str,
    max_retries: int = 5
):
    """
    Input file selector with controlled retries.

    Rules:
    - Enter 0 or press Enter → use base_name.json
    - Enter digit N > 0:
        - If base_name_N.json exists → use it
        - Else retry up to max_retries:
            - y / 0 → use base file
            - n     → exit
            - digit → retry with new index
    - Enter non-digit → error & exit
    """

    base_path = os.path.join(data_dir, f"{base_name}.json")

    def use_base():
        if os.path.exists(base_path):
            return base_path, None
        print(f"[ERROR] file not found: {base_path}")
        sys.exit(1)

    # -------- First input --------
    user_input = input(
        f"Select data file index "
    ).strip()

    # Base file: Enter or 0
    if user_input == "" or user_input == "0":
        return use_base()

    # Non-digit → error
    if not user_input.isdigit():
        print("[ERROR] Invalid input. Only digits are allowed.")
        sys.exit(1)

    # -------- Indexed selection with retries --------
    retries = 0
    idx = int(user_input)

    while retries < max_retries:
        indexed_path = os.path.join(data_dir, f"{base_name}_{idx}.json")

        if os.path.exists(indexed_path):
            return indexed_path, idx

        retries += 1
        print(
            f"[WARNING] File not found: {indexed_path} "
            f"({retries}/{max_retries})"
        )

        choice = input(
            "Enter another index or use default file y/n? "
        ).strip().lower()

        if choice in ("y", "0"):
            return use_base()

        if choice == "n":
            print("[INFO] Exiting as per user choice.")
            sys.exit(1)

        if choice.isdigit():
            idx = int(choice)
            continue

        # print("[ERROR] Invalid input. Only digits, y, 0, or n allowed.")

    print("[ERROR] Maximum retries exceeded. Exiting.")
    sys.exit(1)


# import os


def select_inputs_once(gen_dir, gen_base, gt_dir, gt_base):
    """
    Ask for run index once and resolve generation + ground-truth JSON paths.

    gen_base, gt_base are base names WITHOUT extension and WITHOUT index.
    Example:
      gen_base = "code4logic_fopl_outputs"
      gt_base  = "ground_truth_fopl"
    """

    run_inp = input(
        f"Enter run index (press Enter for base files '{gen_base}.json' and '{gt_base}.json'): "
    ).strip()

    # --- Generation path ---
    if run_inp:
        if not run_inp.isdigit():
            raise ValueError("Run index must be a number.")

        gen_name = f"{gen_base}_{run_inp}.json"
        run_id = int(run_inp)
    else:
        gen_name = f"{gen_base}.json"
        run_id = 0

    gen_path = os.path.join(gen_dir, gen_name)

    if not os.path.exists(gen_path):
        raise FileNotFoundError(f"Generation file not found: {gen_path}")

    # --- Ground truth path ---
    if run_inp:
        gt_indexed = os.path.join(gt_dir, f"{gt_base}_{run_inp}.json")
        gt_base_path = os.path.join(gt_dir, f"{gt_base}.json")

        if os.path.exists(gt_indexed):
            gt_path = gt_indexed
        elif os.path.exists(gt_base_path):
            gt_path = gt_base_path
        else:
            raise FileNotFoundError(
                f"Ground truth not found: {gt_indexed} OR {gt_base_path}"
            )
    else:
        gt_path = os.path.join(gt_dir, f"{gt_base}.json")
        if not os.path.exists(gt_path):
            raise FileNotFoundError(f"Ground truth file not found: {gt_path}")

    return gen_path, gt_path, run_id
