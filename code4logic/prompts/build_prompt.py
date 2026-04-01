# -------------------------------------------------------------------
# build_prompt.py
# Construct the full in-context learning prompt for CODE4LOGIC
#
# Includes:
#   1. High-level instruction docstring
#   2. Basis FOL function definitions
#   3. K demonstration examples
#   4. The final query
#
# Demos file format (prompts/demos.json):
# [
#   {
#     "nl": "If a person is a doctor, they treat patients.",
#     "code": "formula_1 = Variable('x')\n ... \n formula = End(formula_8)"
#   },
#   ...
# ]
# -------------------------------------------------------------------

import json
import os
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

from prompts.fol_to_code import fol_to_code

_TOP_MATCH_MODULE = None


# -------------------------------------------------------------------
# Load basis function source code
# -------------------------------------------------------------------
def load_basis_functions():
    """
    Load the entire fol_functions.py file as text.
    This is inserted directly into the prompt so the LLM
    understands the API it must use.
    """
    base_dir = os.path.dirname(__file__)
    repo_dir = os.path.dirname(base_dir)
    path = os.path.join(repo_dir, "basis_functions", "fol_functions.py")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# -------------------------------------------------------------------
# Load demonstration examples
# -------------------------------------------------------------------
def load_demos(k: int = None):
    """
    Load demonstration examples from prompts/demos.json.
    If k is provided, take the first k examples.
    """
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "demos.json")

    with open(path, "r", encoding="utf-8") as f:
        demos = json.load(f)

    if k is not None:
        return demos[:k]

    return demos


# -------------------------------------------------------------------
# Load related examples via top-match script
# -------------------------------------------------------------------
def _escape_py_string(text: str) -> str:
    text = str(text)
    return text.replace("\\", "\\\\").replace("\"", "\\\"")


def _load_top_match_module():
    global _TOP_MATCH_MODULE
    if _TOP_MATCH_MODULE is not None:
        return _TOP_MATCH_MODULE
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "top-match-find.py")
    loader = SourceFileLoader("top_match_find", path)
    spec = spec_from_loader(loader.name, loader)
    if spec is None:
        raise ImportError("Failed to create spec for top-match-find.py")
    module = module_from_spec(spec)
    loader.exec_module(module)
    _TOP_MATCH_MODULE = module
    return module


def _resolve_related_dataset_path(custom_path: str = None) -> str:
    if custom_path:
        return custom_path

    base_dir = os.path.dirname(__file__)
    repo_dir = os.path.dirname(base_dir)
    candidates = [
        os.path.join(repo_dir, "data", "support_1.jsonl"),
        os.path.join(repo_dir, "data", "support.jsonl"),
        os.path.join(base_dir, "demos.json"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


def load_related_examples(
    nl_sentence: str,
    top_k: int = 5,
    dataset_path: str = None,
):
    dataset_path = _resolve_related_dataset_path(dataset_path)
    if not dataset_path or top_k <= 0:
        return []

    try:
        top_match = _load_top_match_module()
        rows, text_col, fol_col = top_match.get_top_k_example_rows(
            dataset_path=dataset_path,
            target_sentence=nl_sentence,
            top_k=top_k,
        )
    except Exception:
        return []

    examples = []
    for row in rows:
        ex = {"nl": row.get(text_col, "")}
        if "code" in row:
            ex["code"] = row.get("code")
        if fol_col:
            ex["fol"] = row.get(fol_col)
        examples.append(ex)

    return examples


# -------------------------------------------------------------------
# Build the final prompt
# -------------------------------------------------------------------
def build_prompt(
    nl_sentence: str,
    k: int = 3,
    related_k: int = 5,
    related_dataset_path: str = None,
):
    """
    Build the complete prompt for in-context learning.

    Args:
        nl_sentence: The new natural language query to translate.
        k: How many demonstration examples to include.

    Returns:
        A large string containing the prompt to send to the LLM.
    """

    # 1. Instruction block (from paper: inside a Python docstring)
    instruction_block = (
        "'''\n"
        "You are provided with several Python functions that allow you to "
        "construct first-order logic formulas. Using ONLY these functions, "
        "translate the natural language statement into a corresponding FOL formula.\n\n"

        "Your output MUST be valid Python code that:\n"
        "  - Defines intermediate variables formula_1, formula_2, ...\n"
        "  - Uses the provided basis functions exactly as demonstrated\n"
        "  - Ends with:  formula = End(<final_formula_var>)\n\n"

        "Follow the structure of the examples below.\n"
        "'''\n\n"
    )

    # 2. Basis functions
    basis_code = load_basis_functions()
    basis_block = (
        "# --------------------------------------------------------\n"
        "# Basis functions for building FOL (exact API definitions)\n"
        "# --------------------------------------------------------\n"
        f"{basis_code}\n\n"
    )

    # 3. Few-shot demonstration examples
    related_examples = load_related_examples(
        nl_sentence=nl_sentence,
        top_k=related_k,
        dataset_path=related_dataset_path,
    )

    related_examples = [
        ex for ex in related_examples
        if ex.get("nl") and (ex.get("code") or ex.get("fol"))
    ]
    use_related = len(related_examples) > 0
    demos = related_examples if use_related else load_demos(k)
    demo_block = (
        "# --------------------------------------------------------\n"
        "# FEW-SHOT DEMONSTRATION EXAMPLES\n"
        "# --------------------------------------------------------\n"
    )

    for ex in demos:
        demo_block += (
            f"\n# Example\n"
            f"natural_language_statement = \"{_escape_py_string(ex['nl'])}\"\n"
        )
        if "code" in ex and ex["code"]:
            demo_block += f"{ex['code']}\n"
        elif "fol" in ex and ex["fol"]:
            demo_block += f"# FOL: {ex['fol']}\n"
            try:
                demo_block += f"{fol_to_code(ex['fol'])}\n"
            except Exception:
                demo_block += "# [WARN] Failed to convert FOL to code for this example.\n"
        else:
            demo_block += "# FOL: <missing>\n"

    # Optional: include related examples as reference if we did not use them as demos
    if (not use_related) and related_examples:
        demo_block += (
            "\n# --------------------------------------------------------\n"
            "# RELATED EXAMPLES (NL -> FOL, reference)\n"
            "# --------------------------------------------------------\n"
        )
        for ex in related_examples:
            if not ex.get("nl"):
                continue
            fol = ex.get("fol", "<missing>")
            demo_block += (
                f"\n# Related Example\n"
                f"natural_language_statement = \"{_escape_py_string(ex['nl'])}\"\n"
                f"# FOL: {fol}\n"
            )

    # 4. Final query
    final_query = (
        "\n# --------------------------------------------------------\n"
        "# NEW QUERY (LLM MUST COMPLETE CODE BELOW)\n"
        "# --------------------------------------------------------\n"
        f"natural_language_statement = \"{_escape_py_string(nl_sentence)}\"\n"
    )

    # Combine all parts
    prompt = instruction_block + basis_block + demo_block + final_query
    return prompt


# -------------------------------------------------------------------
# Manual test (optional)
# -------------------------------------------------------------------
if __name__ == "__main__":
    test_prompt = build_prompt("Every city has a mayor.", k=2)
    print(test_prompt)
