# -----------------------------------------------------------
# fol_functions.py
# Basis Functions for Building First-Order Logic Expressions
# -----------------------------------------------------------

class Term:
    """Base class for variables and constants."""
    def __init__(self, name):
        self.name = name


class Constant(Term):
    """Represents a constant symbol."""
    def __repr__(self):
        return f"Constant({self.name})"


class Variable(Term):
    """Represents a variable symbol."""
    def __repr__(self):
        return f"Variable({self.name})"


class Function:
    """Represents a function term."""
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Function({self.name}, {self.args})"


class Predicate:
    """Represents a predicate with arguments."""
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Predicate({self.name}, {self.args})"


# -------------------------------
# Logical Connectives
# -------------------------------

class Negation:
    def __init__(self, formula):
        self.formula = formula

    def __repr__(self):
        return f"Negation({self.formula})"


class Conjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Conjunction({self.left}, {self.right})"


class Disjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Disjunction({self.left}, {self.right})"


class Implication:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Implication({self.left}, {self.right})"


class Equivalence:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Equivalence({self.left}, {self.right})"


class Nonequivalence:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Nonequivalence({self.left}, {self.right})"


# -------------------------------
# Quantifiers
# -------------------------------

class ExistentialQuantification:
    def __init__(self, formula, var):
        self.formula = formula
        self.var = var

    def __repr__(self):
        return f"Exists({self.var}, {self.formula})"


class UniversalQuantification:
    def __init__(self, formula, var):
        self.formula = formula
        self.var = var

    def __repr__(self):
        return f"ForAll({self.var}, {self.formula})"


# -------------------------------
# Equality / Non-Equality
# -------------------------------

class Equal:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Equal({self.left}, {self.right})"


class NonEqual:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"NonEqual({self.left}, {self.right})"


class GreaterThan(Predicate):
    def __init__(self, left, right):
        super().__init__("GreaterThan", [left, right])


class LessThan(Predicate):
    def __init__(self, left, right):
        super().__init__("LessThan", [left, right])


class GreaterEqual(Predicate):
    def __init__(self, left, right):
        super().__init__("GreaterEqual", [left, right])


class LessEqual(Predicate):
    def __init__(self, left, right):
        super().__init__("LessEqual", [left, right])


# -------------------------------
# End Node (final FOL output)
# -------------------------------

class End:
    """
    Wraps the final formula object and provides a string output
    in proper First-Order Logic syntax.
    """
    def __init__(self, formula):
        self.formula = formula

    def __repr__(self):
        return f"End({self.formula})"

    def __str__(self):
        return self._to_fol(self.formula)

    # -----------------------------------------
    # FOL Printer
    # -----------------------------------------
    def _to_fol(self, node):
        # Term types
        if isinstance(node, Variable):
            return node.name

        if isinstance(node, Constant):
            return node.name

        if isinstance(node, Function):
            args = ",".join([self._to_fol(a) for a in node.args])
            return f"{node.name}({args})"

        if isinstance(node, Predicate):
            args = ",".join([self._to_fol(a) for a in node.args])
            return f"{node.name}({args})"

        # Logical Connectives
        if isinstance(node, Negation):
            return f"¬{self._to_fol(node.formula)}"

        if isinstance(node, Conjunction):
            return f"({self._to_fol(node.left)} ∧ {self._to_fol(node.right)})"

        if isinstance(node, Disjunction):
            return f"({self._to_fol(node.left)} ∨ {self._to_fol(node.right)})"

        if isinstance(node, Implication):
            return f"({self._to_fol(node.left)} → {self._to_fol(node.right)})"

        if isinstance(node, Equivalence):
            return f"({self._to_fol(node.left)} ↔ {self._to_fol(node.right)})"

        if isinstance(node, Nonequivalence):
            return f"({self._to_fol(node.left)} ⊕ {self._to_fol(node.right)})"

        # Quantifiers
        if isinstance(node, ExistentialQuantification):
            return f"∃{node.var.name} {self._to_fol(node.formula)}"

        if isinstance(node, UniversalQuantification):
            return f"∀{node.var.name} {self._to_fol(node.formula)}"

        # Equality
        if isinstance(node, Equal):
            return f"({self._to_fol(node.left)} = {self._to_fol(node.right)})"

        if isinstance(node, NonEqual):
            return f"({self._to_fol(node.left)} ≠ {self._to_fol(node.right)})"

        # Fallback
        return str(node)