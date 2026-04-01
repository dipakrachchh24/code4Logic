# -------------------------------------------------------------------
# fol_grammar.py
# First-Order Logic Grammar + Parser using Lark
# Converts FOL strings into structured Python objects (AST)
# -------------------------------------------------------------------

from lark import Lark, Transformer, v_args # type: ignore
from basis_functions.fol_functions import (
    Variable, Constant, Function, Predicate,
    Negation, Conjunction, Disjunction, Implication,
    Equivalence, Nonequivalence,
    ExistentialQuantification, UniversalQuantification,
    Equal, NonEqual
)

# -------------------------------------------------------------------
# 1. FOL Grammar (compatible with CODE4LOGIC paper, Appendix A)
# -------------------------------------------------------------------

fol_grammar = r"""
    ?start: expr

    ?expr: equivalence

    ?equivalence: implication
        | implication "<->" implication   -> equivalence
        | implication "<>" implication    -> nonequivalence

    ?implication: disjunction
        | disjunction "->" disjunction    -> implication

    ?disjunction: conjunction
        | disjunction "∨" conjunction      -> disjunction
        | disjunction "|" conjunction      -> disjunction

    ?conjunction: unary
        | conjunction "∧" unary            -> conjunction
        | conjunction "&" unary            -> conjunction

    ?unary: atom
        | "¬" unary                        -> negation
        | "~" unary                        -> negation

    ?atom: quantifier
        | term_predicate
        | variable
        | constant
        | "(" expr ")"

    // Quantifiers:
    // Attached:  ∀x ( ... )
    // Spaced  :  ∀ x ( ... )
    QVAR: /(∀|∃)[a-z]/

    quantifier: QVAR "(" expr ")"                -> quantification_qvar
              | quant_op variable "(" expr ")"   -> quantification

    quant_op: "∀" | "forall" | "ForAll" 
            | "∃" | "exists" | "Exists"

    // VARIABLE = single lowercase letter
    VARIABLE: /[a-z]/

    // CONSTANT = uppercase starting symbol
    CONSTANT: /[A-Z]/

    // Predicate or function name
    NAME: /[A-Z][A-Za-z0-9_]+/

    variable: VARIABLE
    constant: CONSTANT

    term_predicate: NAME "(" args ")"      -> pred_node

    args: expr ("," expr)*

    %import common.WS
    %ignore WS
"""

# -------------------------------------------------------------------
# 2. AST Transformer → convert parse tree → Python objects
# -------------------------------------------------------------------

@v_args(inline=True)
class FOLTransformer(Transformer):

    # Terminals
    def VARIABLE(self, t):
        return Variable(str(t))

    def CONSTANT(self, t):
        return Constant(str(t))

    def NAME(self, t):
        return str(t)
    
    # Simple wrappers so rules don't leave Tree nodes
    def variable(self, item): return item
    def constant(self, item): return item

    # Predicate (everything is a predicate)
    def pred_node(self, name, args):
        return Predicate(name, args)
    
    # Connectives
    def negation(self, a):
        return Negation(a)

    def conjunction(self, a, b):
        return Conjunction(a, b)

    def disjunction(self, a, b):
        return Disjunction(a, b)

    def implication(self, a, b):
        return Implication(a, b)

    def equivalence(self, a, b):
        return Equivalence(a, b)

    def nonequivalence(self, a, b):
        return Nonequivalence(a, b)

    # Quantifiers: ∀x(…) or ∀ x (…)
    def quantification(self, op, var, expr):
        op = str(op)
        if op in ["∀", "forall", "ForAll"]:
            return UniversalQuantification(expr, var)
        else:
            return ExistentialQuantification(expr, var)

    # Quantifiers: attached QVAR → variable extracted from token like "∀x"
    def quantification_qvar(self, qv, expr):
        text = str(qv)     # e.g., "∀x"
        symbol = text[0]   # ∀ or ∃
        var = Variable(text[1])
        if symbol == "∀":
            return UniversalQuantification(expr, var)
        else:
            return ExistentialQuantification(expr, var)

    # Arguments
    def args(self, *items):
        return list(items)

    # Identity for expr
    def expr(self, x):
        return x
    
    def atom(self, x):
        return x
    
    # removing for now because throwing error dont know why but earlier it was working
    # # IMPORTANT: remove leftover Tree wrappers
    # def __default__(self, data, children, meta):
    #     # Flatten any rule producing a single child
    #     if len(children) == 1:
    #         return children[0]
    #     return children


# -------------------------------------------------------------------
# 3. Make Parser
# -------------------------------------------------------------------

fol_parser = Lark(
    fol_grammar,
    parser="lalr",
    transformer=FOLTransformer()
)

# -------------------------------------------------------------------
# 4. Helper: parse FOL string → Python object
# -------------------------------------------------------------------

def parse_fol(fol_string):
    """
    Converts an FOL formula string into a nested Python structure.
    """
    return fol_parser.parse(fol_string)

# -------------------------------------------------------------------
# END OF FILE
# -------------------------------------------------------------------
