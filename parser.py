from operators import *
from literals import Literal, Symbol, Top, Bottom
from formula import Formula
from typing import Any

# Map of binary operators; string => (Operator, Not Variant)
binary_operators = {
    '&': (AndOperator, NandOperator), '.': (AndOperator, NandOperator),
    '|': (OrOperator, NorOperator), '+': (OrOperator, NorOperator),
    '->': (ImpliesOperator, NimpliesOperator),
    '<-': (ReverseImpliesOperator, ReverseNimpliesOperator),
    '=': (EqualityOperator, NonEqualityOperator)
}


def parse(string: str) -> (bool, Formula | str):
    """ Given a string, return parsed Formula, or error message: X [op Y] """

    index = 0

    def eat_whitespace():
        """ Each whitespace from string[index] """
        nonlocal index

        while index < len(string) and string[index] == ' ':
            index += 1

    def parse_negation(limit: int = None) -> int:
        """ Return number of negations encountered """
        nonlocal index
        count = 0

        while index < len(string) and (limit is None or count < limit) and string[index] in ('!', '¬', '~'):
            count += 1
            index += 1

        return count

    def parse_literal() -> (bool, Literal | str):
        """ Parse a literal """
        nonlocal index

        # Is literal negated?
        negations = parse_negation()
        eat_whitespace()

        literal = None

        # Literal: top
        if string[index] in (Top.symbol, 'T', '1'):
            index += 1
            literal = Top()

        # Literal: bottom
        elif string[index] in (Bottom.symbol, 'F', '0'):
            index += 1
            literal = Bottom()

        # Literal: symbol
        elif string[index].isalpha():
            start = index
            while index < len(string) and string[index].isalnum():
                index += 1

            literal = Symbol(string[start:index])

        else:
            return False, f"Index {index}: expected literal, got '{string[index:index+5]}'"

        return True, Negation.nest(literal, negations)

    def parse_operator():
        """ Parse operator; return class constructor """
        nonlocal index

        negations = parse_negation(1)

        for op in binary_operators:
            if string[index:].startswith(op):
                index += len(op)
                return binary_operators[op][1 if negations else 0]

        return None

    def parse_surrounded_clause(close: str, parse_fn, default = None) -> (bool, Any | str):
        """ Parse a clause surrounded by `open` and `close`. Note,  open` has already been encountered. """
        nonlocal index

        eat_whitespace()

        if default is not None and string[index:].startswith(close):
            index += len(close)
            return True, default

        ok, res = parse_fn()
        if not ok:
            return ok, res

        if index >= len(string):
            return False, f"Index {index}: unexpected end of input, expected '{close}'"
        if not string[index:].startswith(close):
            return False, f"Index {index}: expected '{close}', got '{string[index:index + 5]}'"

        index += len(close)
        return True, res

    def parse_group() -> (bool, Formula | str):
        """ Parse group (bracketed) or literal or generalised con- or disjunction """
        nonlocal index

        negations = parse_negation()

        if index >= len(string):
            return False, f"Index {index}: expected '(', '[', '<' or literal, got end of input"

        if string[index] == '(':
            # Group
            index += 1
            ok, res = parse_surrounded_clause(')', lambda: parse_formula({')'}))
            if not ok:
                return ok, res

            group = res

        elif string[index] == '[':
            index += 1
            ok, res = parse_surrounded_clause(']', lambda: parse_comma_seperated(']'), [])
            if not ok:
                return ok, res

            group = GeneralisedDisjunction(*res)

        elif string[index] == '<':
            index += 1
            ok, res = parse_surrounded_clause('>', lambda: parse_comma_seperated('>'), [])
            if not ok:
                return ok, res

            group = GeneralisedConjunction(*res)

        else:
            # Literal
            ok, res = parse_literal()
            if not ok:
                return ok, res

            group = res

        return True, Negation.nest(group, negations)

    def parse_comma_seperated(close: str) -> (bool, list[Formula] | str):
        """ Parse a comma-seperated list of formulae. List ends with end-of-input or `close` """
        nonlocal index
        formulae = []

        while True:
            # Parse formula
            ok, res = parse_formula({close, ')', ','})
            if not ok:
                return ok, res

            formulae.append(res)
            eat_whitespace()

            # End of input?
            if index >= len(string) or string[index:].startswith(close):
                break

            # Comma: expected next formula
            if string[index] == ',':
                index += 1
                eat_whitespace()
                continue

            return False, f"Index {index}: expected ',' or '{close}' or end of input, got '{string[index:index+5]}'"

        return True, formulae

    def parse_formula(terminal: set[str] = None) -> (bool, Formula | str):
        """ Parse a group in the form `[lit/formula] [[op] [lit/formula]]` """
        nonlocal index

        # Literal/Group 1
        ok, res = parse_group()
        if not ok:
            return ok, res

        arg1 = res
        eat_whitespace()

        # EOL?
        if index >= len(string):
            return True, arg1
        elif terminal is not None and any(string[index:].startswith(s) for s in terminal):
            return True, arg1

        # Operator
        op = parse_operator()
        if op is None:
            return False, f"Index {index}: expected operator, got '{string[index:index+5]}'"

        eat_whitespace()

        # Literal 2
        ok, res = parse_group()
        if not ok:
            return ok, res

        arg2 = res
        eat_whitespace()

        return True, op(arg1, arg2)

    # Driver: start parsing as formula
    ok, res = parse_formula()

    # Expect end of input
    if ok and index < len(string):
        return False, f"Index {index}: expected end of input, got '{string[index:index + 5]}'"

    return ok, res
