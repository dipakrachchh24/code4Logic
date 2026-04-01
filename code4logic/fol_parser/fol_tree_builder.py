from fol_parser.fol_grammar import parse_fol
from basis_functions.fol_functions import (
    Variable, Constant, Predicate,
    Negation, Conjunction, Disjunction, Implication,
    Equivalence, Nonequivalence,
    ExistentialQuantification, UniversalQuantification
)

def fol_string_to_tree(fol_string: str):
    try:
        return parse_fol(fol_string)
    except Exception as e:
        print("\n[ERROR] Failed to parse FOL string:")
        print("Input:", fol_string)
        print("Exception:", e)
        return None

def print_tree(node, indent=0):
    prefix = "  " * indent
    print(prefix + repr(node))

    if isinstance(node, (Variable, Constant)):
        return

    if isinstance(node, Predicate):
        for a in node.args:
            print_tree(a, indent + 1)
        return

    if isinstance(node, Negation):
        print_tree(node.formula, indent + 1)
        return

    if isinstance(node, (Conjunction, Disjunction, Implication,
                         Equivalence, Nonequivalence)):
        print_tree(node.left, indent + 1)
        print_tree(node.right, indent + 1)
        return

    if isinstance(node, (ExistentialQuantification, UniversalQuantification)):
        print_tree(node.var, indent + 1)
        print_tree(node.formula, indent + 1)
        return


if __name__ == "__main__":
    test = "∀x (Doctor(x) -> ∃y (Patient(y) ∧ Treats(x,y)))"
    print("[INPUT]:", test)
    tree = fol_string_to_tree(test)
    print("\n[AST]:")
    print_tree(tree)
