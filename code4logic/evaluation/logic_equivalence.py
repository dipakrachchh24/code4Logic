# -------------------------------------------------------------------
# logic_equivalence.py
#
# Logical Equivalence Evaluator for NL→FOL output.
#
# This module provides:
#   - Structural equivalence
#   - Alpha-equivalence (renaming variables)
#   - Normalization utilities
#
# It is compatible with fol_functions.py trees.
#
# NOTE:
#   This is a simplified but effective equivalence checker.
#   For full truth-table equivalence, integrate Prover9/Z3.
# -------------------------------------------------------------------

from basis_functions.fol_functions import (
    Variable, Constant, Function, Predicate,
    Negation, Conjunction, Disjunction, Implication,
    Equivalence, Nonequivalence,
    ExistentialQuantification, UniversalQuantification,
    Equal, NonEqual, End
)


def normalize_fol_symbols(fol: str) -> str:
    if fol is None:
        return None
    return (
        fol.replace("→", "->")
           .replace("↔", "<->")
           .replace("¬", "~")
           .replace("∧", "&")
           .replace("∨", "|")
    )


# -------------------------------------------------------------------
# Normalize variable names (to handle alpha-equivalence)
# -------------------------------------------------------------------

def normalize_vars(node, mapping=None, counter=None):
    """
    Rename variable names to a normalized sequence (x1, x2, x3...) so that
    expressions differing only in variable names still match.

    Example:
        ∀x P(x)     and     ∀y P(y)
    Both become something like:
        ∀v1 P(v1)
    """
    if mapping is None:
        mapping = {}
    if counter is None:
        counter = [1]  # mutable integer

    if isinstance(node, Variable):
        if node.name not in mapping:
            mapping[node.name] = f"v{counter[0]}"
            counter[0] += 1
        return Variable(mapping[node.name])

    if isinstance(node, Constant):
        return Constant(node.name)

    if isinstance(node, Function):
        args = [normalize_vars(a, mapping, counter) for a in node.args]
        return Function(node.name, args)

    if isinstance(node, Predicate):
        args = [normalize_vars(a, mapping, counter) for a in node.args]
        return Predicate(node.name, args)

    if isinstance(node, Negation):
        return Negation(normalize_vars(node.formula, mapping, counter))

    if isinstance(node, Conjunction):
        return Conjunction(
            normalize_vars(node.left, mapping, counter),
            normalize_vars(node.right, mapping, counter)
        )

    if isinstance(node, Disjunction):
        return Disjunction(
            normalize_vars(node.left, mapping, counter),
            normalize_vars(node.right, mapping, counter)
        )

    if isinstance(node, Implication):
        return Implication(
            normalize_vars(node.left, mapping, counter),
            normalize_vars(node.right, mapping, counter)
        )

    if isinstance(node, Equivalence):
        return Equivalence(
            normalize_vars(node.left, mapping, counter),
            normalize_vars(node.right, mapping, counter)
        )

    if isinstance(node, Nonequivalence):
        return Nonequivalence(
            normalize_vars(node.left, mapping, counter),
            normalize_vars(node.right, mapping, counter)
        )

    if isinstance(node, UniversalQuantification):
        new_var = normalize_vars(node.var, mapping, counter)
        new_formula = normalize_vars(node.formula, mapping, counter)
        return UniversalQuantification(new_formula, new_var)

    if isinstance(node, ExistentialQuantification):
        new_var = normalize_vars(node.var, mapping, counter)
        new_formula = normalize_vars(node.formula, mapping, counter)
        return ExistentialQuantification(new_formula, new_var)

    if isinstance(node, Equal):
        return Equal(
            normalize_vars(node.left, mapping, counter),
            normalize_vars(node.right, mapping, counter)
        )

    if isinstance(node, NonEqual):
        return NonEqual(
            normalize_vars(node.left, mapping, counter),
            normalize_vars(node.right, mapping, counter)
        )

    return node


# -------------------------------------------------------------------
# Structural comparison
# -------------------------------------------------------------------

def structurally_equal(a, b):
    """
    Recursively compare two normalized formula trees.
    """

    # Type mismatch
    if type(a) != type(b):
        return False

    # Atoms
    if isinstance(a, Variable):
        return a.name == b.name

    if isinstance(a, Constant):
        return a.name == b.name

    if isinstance(a, Function):
        return (a.name == b.name and
                len(a.args) == len(b.args) and
                all(structurally_equal(x, y) for x, y in zip(a.args, b.args)))

    if isinstance(a, Predicate):
        return (a.name == b.name and
                len(a.args) == len(b.args) and
                all(structurally_equal(x, y) for x, y in zip(a.args, b.args)))

    # Unary
    if isinstance(a, Negation):
        return structurally_equal(a.formula, b.formula)

    # Binary
    if isinstance(a, (Conjunction, Disjunction, Implication,
                      Equivalence, Nonequivalence, Equal, NonEqual)):
        return (structurally_equal(a.left, b.left) and
                structurally_equal(a.right, b.right))

    # Quantifiers
    if isinstance(a, (UniversalQuantification, ExistentialQuantification)):
        return (structurally_equal(a.var, b.var) and
                structurally_equal(a.formula, b.formula))

    return False


# -------------------------------------------------------------------
# USER-FACING FUNCTION
# -------------------------------------------------------------------

def logic_equivalent(tree1, tree2):
    """
    Check whether two FOL AST trees are logically equivalent under
    alpha-equivalence and structural normalization.

    Args:
        tree1, tree2: AST nodes produced from fol_parser/fol_tree_builder.py

    Returns:
        True if equivalent, False otherwise.
    """
    n1 = normalize_vars(tree1)
    n2 = normalize_vars(tree2)

    return structurally_equal(n1, n2)

# -------------------------------------------------------------------
# Batch-facing API
# -------------------------------------------------------------------

from fol_parser.fol_tree_builder import fol_string_to_tree

def check_equivalence(gen_fopl: str, gt_fopl: str):
    """
    Compare two FOL strings and report multiple equivalence signals.

    Returns:
        {
            "structural": bool,
            "alpha": bool,
            "normalized": bool
        }
    """

    gen_fopl = normalize_fol_symbols(gen_fopl)
    gt_fopl = normalize_fol_symbols(gt_fopl)

    tree1 = fol_string_to_tree(gen_fopl)
    tree2 = fol_string_to_tree(gt_fopl)

    if tree1 is None or tree2 is None:
        raise ValueError("Failed to parse one of the FOL expressions")

    # alpha + structural equivalence (your current logic)
    alpha_eq = logic_equivalent(tree1, tree2)

    # For now, structural == alpha == normalized
    # (you can refine later)
    return {
        "structural": alpha_eq,
        "alpha": alpha_eq,
        "normalized": alpha_eq
    }


# -------------------------------------------------------------------
# Manual test
# -------------------------------------------------------------------

if __name__ == "__main__":
    from fol_parser.fol_tree_builder import fol_string_to_tree

    a = fol_string_to_tree("∀x (Cat(x) -> Animal(x))")
    b = fol_string_to_tree("∀y (Cat(y) -> Animal(y))")
    # a = fol_string_to_tree("∀m ((HasElement(m,r) ∧ HasElement(m,c)) → Movie(m))")
    # b = fol_string_to_tree("∀m ((HasElement(m,r) ∧ HasElement(m,c)) → Movie(m))")

    print("Equivalent?", logic_equivalent(a, b))
