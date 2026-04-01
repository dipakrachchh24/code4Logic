# -------------------------------------------------------------------
# tree_to_code.py
# Convert FOL Python AST (built with fol_functions.py) into
# a sequential Python code snippet that reconstructs the formula.
#
# This is the "Tree → Code Sequence" step of the CODE4LOGIC pipeline.
# -------------------------------------------------------------------

from typing import List, Tuple

from basis_functions.fol_functions import (
    Variable, Constant, Function, Predicate,
    Negation, Conjunction, Disjunction, Implication,
    Equivalence, Nonequivalence,
    ExistentialQuantification, UniversalQuantification,
    Equal, NonEqual, End
)


class CodeGenerator:
    """
    Given a root node of a FOL expression tree (built using fol_functions),
    generate a sequence of Python assignment statements that reconstruct
    the formula using the same fol_functions API.

    Example usage:

        cg = CodeGenerator()
        code_str = cg.generate_code(root_formula, include_import=True)

    This produces something like:

        from basis_functions.fol_functions import *

        formula_1 = Variable('x')
        formula_2 = Predicate('Doctor', [formula_1])
        formula_3 = Predicate('Patient', [formula_4])
        formula_4 = ExistentialQuantification(formula_3, formula_1)
        formula = End(formula_4)
    """

    def __init__(self, var_prefix: str = "formula"):
        self.var_prefix = var_prefix
        self._counter = 0
        self._lines: List[str] = []
        # map node id -> variable name, so repeated subtrees reuse same var
        self._node_to_var = {}

    # -------------------------- internal helpers --------------------------

    def _new_var(self) -> str:
        self._counter += 1
        return f"{self.var_prefix}_{self._counter}"

    def _emit(self, line: str) -> None:
        self._lines.append(line)

    def _get_cached(self, node):
        key = id(node)
        return self._node_to_var.get(key, None)

    def _cache(self, node, var_name: str) -> None:
        key = id(node)
        self._node_to_var[key] = var_name

    # ----------------------- main recursive generator ---------------------

    def _gen_node(self, node) -> str:
        """
        Recursively generate code for a node and return
        the variable name that holds its value.
        """
        # Reuse variables if we’ve already generated code for this node
        cached = self._get_cached(node)
        if cached is not None:
            return cached

        # ---- Term types ----
        if isinstance(node, Variable):
            var_name = self._new_var()
            self._emit(f"{var_name} = Variable('{node.name}')")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Constant):
            var_name = self._new_var()
            self._emit(f"{var_name} = Constant('{node.name}')")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Function):
            arg_vars = [self._gen_node(a) for a in node.args]
            var_name = self._new_var()
            args_str = ", ".join(arg_vars)
            self._emit(f"{var_name} = Function('{node.name}', [{args_str}])")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Predicate):
            arg_vars = [self._gen_node(a) for a in node.args]
            var_name = self._new_var()
            args_str = ", ".join(arg_vars)
            self._emit(f"{var_name} = Predicate('{node.name}', [{args_str}])")
            self._cache(node, var_name)
            return var_name

        # ---- Logical connectives ----
        if isinstance(node, Negation):
            inner = self._gen_node(node.formula)
            var_name = self._new_var()
            self._emit(f"{var_name} = Negation({inner})")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Conjunction):
            left = self._gen_node(node.left)
            right = self._gen_node(node.right)
            var_name = self._new_var()
            self._emit(f"{var_name} = Conjunction({left}, {right})")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Disjunction):
            left = self._gen_node(node.left)
            right = self._gen_node(node.right)
            var_name = self._new_var()
            self._emit(f"{var_name} = Disjunction({left}, {right})")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Implication):
            left = self._gen_node(node.left)
            right = self._gen_node(node.right)
            var_name = self._new_var()
            self._emit(f"{var_name} = Implication({left}, {right})")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Equivalence):
            left = self._gen_node(node.left)
            right = self._gen_node(node.right)
            var_name = self._new_var()
            self._emit(f"{var_name} = Equivalence({left}, {right})")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, Nonequivalence):
            left = self._gen_node(node.left)
            right = self._gen_node(node.right)
            var_name = self._new_var()
            self._emit(f"{var_name} = Nonequivalence({left}, {right})")
            self._cache(node, var_name)
            return var_name

        # ---- Quantifiers ----
        if isinstance(node, ExistentialQuantification):
            inner = self._gen_node(node.formula)
            var_var = self._gen_node(node.var)
            var_name = self._new_var()
            self._emit(
                f"{var_name} = ExistentialQuantification({inner}, {var_var})"
            )
            self._cache(node, var_name)
            return var_name

        if isinstance(node, UniversalQuantification):
            inner = self._gen_node(node.formula)
            var_var = self._gen_node(node.var)
            var_name = self._new_var()
            self._emit(
                f"{var_name} = UniversalQuantification({inner}, {var_var})"
            )
            self._cache(node, var_name)
            return var_name

        # ---- Equality / inequality ----
        if isinstance(node, Equal):
            left = self._gen_node(node.left)
            right = self._gen_node(node.right)
            var_name = self._new_var()
            self._emit(f"{var_name} = Equal({left}, {right})")
            self._cache(node, var_name)
            return var_name

        if isinstance(node, NonEqual):
            left = self._gen_node(node.left)
            right = self._gen_node(node.right)
            var_name = self._new_var()
            self._emit(f"{var_name} = NonEqual({left}, {right})")
            self._cache(node, var_name)
            return var_name

        # Fallback – in case we hit an unsupported node type
        var_name = self._new_var()
        self._emit(f"# WARNING: Unsupported node type {type(node)}")
        self._emit(f"{var_name} = None  # placeholder")
        self._cache(node, var_name)
        return var_name

    # --------------------- public API: main entrypoint ---------------------

    def generate_code(
        self,
        root,
        include_import: bool = False,
        wrap_end: bool = True
    ) -> str:
        """
        Generate Python code for a given FOL root node.

        Args:
            root: The root node of the FOL expression (e.g., a Predicate,
                  Conjunction, Quantifier, etc.).
            include_import: If True, prepend
                'from basis_functions.fol_functions import *'.
            wrap_end: If True, add 'formula = End(<last_var>)' as the last line.

        Returns:
            A string containing the complete Python code.
        """
        # reset state
        self._counter = 0
        self._lines.clear()
        self._node_to_var.clear()

        last_var = self._gen_node(root)

        if wrap_end:
            self._emit(f"formula = End({last_var})")

        code_body = "\n".join(self._lines)

        if include_import:
            header = "from basis_functions.fol_functions import *\n\n"
            return header + code_body

        return code_body

    def generate_lines(
        self,
        root,
        wrap_end: bool = True
    ) -> Tuple[List[str], str]:
        """
        Same as generate_code, but returns (lines, final_var_name)
        instead of a joined string.
        """
        self._counter = 0
        self._lines.clear()
        self._node_to_var.clear()

        last_var = self._gen_node(root)
        if wrap_end:
            self._emit(f"formula = End({last_var})")

        return list(self._lines), last_var


# -------------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------------

def fol_to_code(root, include_import: bool = False, wrap_end: bool = True) -> str:
    """
    Convenience wrapper around CodeGenerator for simple use.
    """
    gen = CodeGenerator()
    return gen.generate_code(root, include_import=include_import, wrap_end=wrap_end)
