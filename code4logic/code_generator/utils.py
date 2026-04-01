# -------------------------------------------------------------------
# utils.py
#
# Helper utilities for the CODE4LOGIC-style pipeline, focused on:
#   - Converting FOL strings to code sequences
#   - Building few-shot demo entries
#   - Batch generation of demos.json
#
# Typical usage:
#   from code_generator.utils import (
#       fol_to_code_string,
#       build_demo_entry,
#       build_demos_from_pairs,
#       save_demos_to_json
#   )
#
#   demos = build_demos_from_pairs(pairs)
#   save_demos_to_json(demos, "prompts/demos.json")
# -------------------------------------------------------------------

from typing import List, Dict, Tuple
import json
import os

from fol_parser.fol_tree_builder import fol_string_to_tree
from code_generator.tree_to_code import fol_to_code


# -------------------------------------------------------------------
# Single FOL → Code sequence
# -------------------------------------------------------------------

def fol_to_code_string(fol_string: str, include_import: bool = False) -> str:
    """
    Convert a First-Order Logic (FOL) formula in string form into
    a Python code sequence that reconstructs it using fol_functions.py.

    Args:
        fol_string: FOL formula as a string.
        include_import: If True, prepend the import line:
            'from basis_functions.fol_functions import *'

    Returns:
        A string with Python code (sequence of assignments + End(...)),
        or None if parsing fails.
    """
    tree = fol_string_to_tree(fol_string)
    if tree is None:
        return None

    code_str = fol_to_code(tree, include_import=include_import, wrap_end=True)
    return code_str


# -------------------------------------------------------------------
# Build a single demo entry
# -------------------------------------------------------------------

def build_demo_entry(nl: str, fol: str) -> Dict[str, str]:
    """
    Build a single demo dict entry from (natural language, FOL string).

    The output format is suitable for prompts/demos.json, e.g.:

        {
          "nl": "If a person is a doctor, they treat patients.",
          "fol": "∀x (Doctor(x) -> ∃y (Patient(y) ∧ Treats(x,y)))",
          "code": "formula_1 = Variable('x')\\n..."
        }

    Args:
        nl: Natural language sentence.
        fol: Corresponding FOL string.

    Returns:
        A dict with keys: "nl", "fol", "code".
        If conversion fails, "code" will be None.
    """
    code_str = fol_to_code_string(fol, include_import=False)

    return {
        "nl": nl,
        "fol": fol,
        "code": code_str,
    }


# -------------------------------------------------------------------
# Batch conversion: list of (NL, FOL) pairs → list of demo dicts
# -------------------------------------------------------------------

def build_demos_from_pairs(pairs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    """
    Convert a list of (NL, FOL) pairs into a list of demo dicts.

    Args:
        pairs: List of tuples (nl_string, fol_string).

    Returns:
        List of demo dicts as produced by build_demo_entry().
    """
    demos = []
    for nl, fol in pairs:
        demo = build_demo_entry(nl, fol)
        if demo["code"] is None:
            print(f"[WARNING] Skipping example due to parse failure:\n  NL : {nl}\n  FOL: {fol}")
            continue
        demos.append(demo)
    return demos


# -------------------------------------------------------------------
# Save demos to JSON file
# -------------------------------------------------------------------

def save_demos_to_json(demos: List[Dict[str, str]], path: str = "prompts/demos.json"):
    """
    Save a list of demo dicts to a JSON file.

    Args:
        demos: List of demo dicts from build_demos_from_pairs().
        path: Output JSON file path.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(demos, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Saved {len(demos)} demos to {path}")


# -------------------------------------------------------------------
# Manual test
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Example pair
    nl_example = "If a person is a doctor, then they treat some patient."
    fol_example = "∀x (Doctor(x) -> ∃y (Patient(y) ∧ Treats(x,y)))"

    print("[TEST] Single FOL → code:")
    code = fol_to_code_string(fol_example)
    print(code)

    print("\n[TEST] Build single demo entry:")
    demo = build_demo_entry(nl_example, fol_example)
    print(demo)

    print("\n[TEST] Build demos and save to prompts/demos.json")
    demos_list = build_demos_from_pairs([(nl_example, fol_example)])
    # save_demos_to_json(demos_list, "prompts/demos.json")
