from __future__ import annotations

from typing import Dict, List, Tuple

from basis_functions.fol_functions import (
    Variable,
    Constant,
    Function,
    Predicate,
    Negation,
    Conjunction,
    Disjunction,
    Implication,
    Equivalence,
    Nonequivalence,
    ExistentialQuantification,
    UniversalQuantification,
    Equal,
    NonEqual,
)
from fol_parser.fol_grammar import parse_fol


class _CodeBuilder:
    def __init__(self):
        self.lines: List[str] = []
        self.counter = 1
        self.var_cache: Dict[str, str] = {}
        self.const_cache: Dict[str, str] = {}

    def _next_name(self) -> str:
        name = f"formula_{self.counter}"
        self.counter += 1
        return name

    def _emit(self, line: str) -> None:
        self.lines.append(line)

    def _build(self, node) -> str:
        # Variables / Constants (cache by name)
        if isinstance(node, Variable):
            if node.name in self.var_cache:
                return self.var_cache[node.name]
            name = self._next_name()
            self._emit(f"{name} = Variable('{node.name}')")
            self.var_cache[node.name] = name
            return name

        if isinstance(node, Constant):
            if node.name in self.const_cache:
                return self.const_cache[node.name]
            name = self._next_name()
            self._emit(f"{name} = Constant('{node.name}')")
            self.const_cache[node.name] = name
            return name

        # Functions / Predicates
        if isinstance(node, Function):
            arg_names = [self._build(a) for a in node.args]
            name = self._next_name()
            self._emit(f"{name} = Function('{node.name}', [{', '.join(arg_names)}])")
            return name

        if isinstance(node, Predicate):
            arg_names = [self._build(a) for a in node.args]
            name = self._next_name()
            self._emit(f"{name} = Predicate('{node.name}', [{', '.join(arg_names)}])")
            return name

        # Unary / Binary connectives
        if isinstance(node, Negation):
            inner = self._build(node.formula)
            name = self._next_name()
            self._emit(f"{name} = Negation({inner})")
            return name

        if isinstance(node, Conjunction):
            left = self._build(node.left)
            right = self._build(node.right)
            name = self._next_name()
            self._emit(f"{name} = Conjunction({left}, {right})")
            return name

        if isinstance(node, Disjunction):
            left = self._build(node.left)
            right = self._build(node.right)
            name = self._next_name()
            self._emit(f"{name} = Disjunction({left}, {right})")
            return name

        if isinstance(node, Implication):
            left = self._build(node.left)
            right = self._build(node.right)
            name = self._next_name()
            self._emit(f"{name} = Implication({left}, {right})")
            return name

        if isinstance(node, Equivalence):
            left = self._build(node.left)
            right = self._build(node.right)
            name = self._next_name()
            self._emit(f"{name} = Equivalence({left}, {right})")
            return name

        if isinstance(node, Nonequivalence):
            left = self._build(node.left)
            right = self._build(node.right)
            name = self._next_name()
            self._emit(f"{name} = Nonequivalence({left}, {right})")
            return name

        # Quantifiers
        if isinstance(node, UniversalQuantification):
            var_name = self._build(node.var)
            formula_name = self._build(node.formula)
            name = self._next_name()
            self._emit(f"{name} = UniversalQuantification({formula_name}, {var_name})")
            return name

        if isinstance(node, ExistentialQuantification):
            var_name = self._build(node.var)
            formula_name = self._build(node.formula)
            name = self._next_name()
            self._emit(f"{name} = ExistentialQuantification({formula_name}, {var_name})")
            return name

        # Equality
        if isinstance(node, Equal):
            left = self._build(node.left)
            right = self._build(node.right)
            name = self._next_name()
            self._emit(f"{name} = Equal({left}, {right})")
            return name

        if isinstance(node, NonEqual):
            left = self._build(node.left)
            right = self._build(node.right)
            name = self._next_name()
            self._emit(f"{name} = NonEqual({left}, {right})")
            return name

        raise ValueError(f"Unsupported node type: {type(node)}")

    def build(self, fol_string: str) -> Tuple[List[str], str]:
        root = parse_fol(fol_string)
        final_var = self._build(root)
        return self.lines, final_var


def fol_to_code(fol_string: str) -> str:
    """
    Convert a FOL string into CODE4LOGIC-style Python code.
    """
    builder = _CodeBuilder()
    lines, final_var = builder.build(fol_string)
    lines.append(f"formula = End({final_var})")
    return "\n".join(lines)
