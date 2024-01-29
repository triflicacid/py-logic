from typing import Any, Callable

from logic.formula import Formula
from logic.generalised_operators import GeneralisedDisjunction, GeneralisedConjunction
from logic.literals import Symbol, Top, Bottom
from logic.operators import AndOperator, OrOperator, ImpliesOperator, ReverseImpliesOperator, EqualityOperator, \
    Negation, BinaryOperator

# Map of binary operators; string => operator
binary_operators: dict[str, type(BinaryOperator)] = {
    '&': AndOperator,
    '.': AndOperator,
    '|': OrOperator,
    '+': OrOperator,
    '->': ImpliesOperator,
    '<-': ReverseImpliesOperator,
    '=': EqualityOperator,
}


class Parser:
    def __init__(self):
        self.index = 0
        self.string = ""

    def eat_whitespace(self):
        """ Each whitespace from string[index]. """
        while self.index < len(self.string) and self.string[self.index] == ' ':
            self.index += 1

    def parse_negation(self, limit: int = None) -> int:
        """ Return number of negations encountered. """
        count = 0

        while self.index < len(self.string) and (limit is None or count < limit) \
                and self.string[self.index] in ('!', '¬', '~'):
            count += 1
            self.index += 1

        return count

    def parse_operator(self) -> type(BinaryOperator) | None:
        """ Parse operator and return it, or None if no operator found. """
        negations = self.parse_negation(1)

        for op in binary_operators:
            if self.string[self.index:].startswith(op):
                self.index += len(op)
                return binary_operators[op].get_negated() if negations else binary_operators[op]

        return None, False

    def parse_literal(self) -> tuple[bool, Formula | str]:
        """ Parse a literal: top, bottom, symbol. """
        # Is literal negated?
        negations = self.parse_negation()
        self.eat_whitespace()

        # Literal: top
        if self.string[self.index] in (Top.symbol, 'T', '1'):
            self.index += 1
            literal = Top()

        # Literal: bottom
        elif self.string[self.index] in (Bottom.symbol, 'F', '0'):
            self.index += 1
            literal = Bottom()

        # Literal: symbol
        elif self.string[self.index].isalpha():
            start = self.index
            while self.index < len(self.string) and self.string[self.index].isalnum():
                self.index += 1

            literal = Symbol(self.string[start:self.index])

        else:
            return False, f"Index {self.index}: expected literal, got '{self.string[self.index:self.index + 5]}'"

        return True, Negation.nest(literal, negations)

    def parse_surrounded_clause(self, close_tag: str, parse_fn: Callable[[], Any], default=None) \
            -> tuple[bool, Any | str]:
        """ Parse a group surrounded by tags. Assumes that open_tag has already been encountered and consumed -
        group ends in `close_tag` """
        self.eat_whitespace()

        # Does this group immediately close?
        if default is not None and self.string[self.index:].startswith(close_tag):
            self.index += len(close_tag)
            return True, default

        ok, res = parse_fn()

        if not ok:
            return ok, res

        if self.index >= len(self.string):
            return False, f"Index {self.index}: unexpected end of input, expected '{close_tag}'"

        if not self.string[self.index:].startswith(close_tag):
            return False, f"Index {self.index}: expected '{close_tag}', got '{self.string[self.index:self.index + 5]}'"

        self.index += len(close_tag)

        return True, res

    def parse_group(self) -> tuple[bool, Formula | str]:
        """ Parse group (bracketed) or literal or generalised con- or disjunction. """
        negations = self.parse_negation()

        if self.index >= len(self.string):
            return False, f"Index {self.index}: expected '(', '[', '<' or literal, got end of input"

        if self.string[self.index] == '(':
            # Group
            self.index += 1
            ok, res = self.parse_surrounded_clause(')', lambda: self.parse_formula({')'}))
            if not ok:
                return ok, res

            group = res

        elif self.string[self.index] == '[':
            self.index += 1
            ok, res = self.parse_surrounded_clause(']', lambda: self.parse_comma_seperated(']'), [])
            if not ok:
                return ok, res

            group = GeneralisedDisjunction(*res)

        elif self.string[self.index] == '<':
            self.index += 1
            ok, res = self.parse_surrounded_clause('>', lambda: self.parse_comma_seperated('>'), [])
            if not ok:
                return ok, res

            group = GeneralisedConjunction(*res)

        else:
            # Literal
            ok, res = self.parse_literal()
            if not ok:
                return ok, res

            group = res

        return True, Negation.nest(group, negations)

    def parse_comma_seperated(self, close_tag: str) -> tuple[bool, list[Formula] | str]:
        """ Parse a comma-seperated list of formulae. List ends with end-of-input or `close`. """
        formulae = []

        while True:
            # Parse formula
            ok, res = self.parse_formula({close_tag, ')', ','})
            if not ok:
                return ok, res

            formulae.append(res)
            self.eat_whitespace()

            # End of input?
            if self.index >= len(self.string) or self.string[self.index:].startswith(close_tag):
                break

            # Comma: expected next formula
            if self.string[self.index] == ',':
                self.index += 1
                self.eat_whitespace()
                continue

            return False, f"Index {self.index}: expected ',' or '{close_tag}' or end of input, got '{self.string[self.index:self.index + 5]}'"

        return True, formulae

    def parse_formula(self, terminal: set[str] = None) -> tuple[bool, Formula | str]:
        """ Parse a group in the form `[lit/formula] [[op] [lit/formula]]`. """
        # Literal/Group 1
        ok, res = self.parse_group()
        if not ok:
            return ok, res

        arg1 = res
        self.eat_whitespace()

        # EOL?
        if self.index >= len(self.string):
            return True, arg1
        elif terminal is not None and any(self.string[self.index:].startswith(s) for s in terminal):
            return True, arg1

        # Operator
        op = self.parse_operator()
        if op is None:
            return False, f"Index {self.index}: expected operator, got '{self.string[self.index:self.index + 5]}'"

        self.eat_whitespace()

        # Literal 2
        ok, res = self.parse_group()
        if not ok:
            return ok, res

        arg2 = res
        self.eat_whitespace()

        return True, op(arg1, arg2)

    def parse(self, string: str) -> tuple[bool, Formula | str]:
        """ Given a string, return parsed Formula, or error message: X [op Y]. """
        self.index = 0
        self.string = string

        # Driver: start parsing as formula
        ok, res = self.parse_formula()

        # Expect end of input
        if ok and self.index < len(string):
            return False, f"Index {self.index}: expected end of input, got '{string[self.index:self.index + 5]}'"

        return ok, res
