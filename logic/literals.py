from __future__ import annotations
from typing import override
from logic.formula import Formula


class Literal(Formula):
    def __init__(self):
        super().__init__()

    @staticmethod
    def from_bool(boolean: bool) -> Literal:
        return Top() if boolean else Bottom()


class Top(Literal):
    symbol = '⊤'

    def __init__(self):
        super().__init__()

    def __str__(self):
        return Top.symbol

    @override
    def get_variables(self):
        return set()

    @override
    def eval_const(self):
        return True

    @override
    def eval(self, symbols: set[str]):
        return True

    @override
    def equals(self, other: Formula) -> bool:
        return isinstance(other, Top)

    @override
    def substitute(self, symbol: str, formula: Formula) -> Formula:
        return self


class Bottom(Literal):
    symbol = '⊥'

    def __init__(self):
        super().__init__()

    def __str__(self):
        return Bottom.symbol

    @override
    def get_variables(self):
        return set()

    @override
    def eval_const(self):
        return False

    @override
    def eval(self, symbols: set[str]):
        return False

    @override
    def equals(self, other: Formula) -> bool:
        return isinstance(other, Bottom)

    @override
    def substitute(self, symbol: str, formula: Formula) -> Formula:
        return self


class Symbol(Literal):
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    @override
    def eval_const(self):
        # Value of symbol is not const
        return None

    @override
    def eval(self, symbols: dict[str, bool]):
        if self.symbol in symbols:
            return symbols[self.symbol]

        user = input(f"Provide truth value of '{self.symbol}' [T/F]: ")
        while True:
            if user == 'T':
                value = True
                break
            elif user == 'F':
                value = False
                break
            else:
                user = input('Invalid response. Please enter [T/F]: ')

        symbols[self.symbol] = value
        return value

    @override
    def substitute(self, symbol: str, formula: Formula) -> Formula:
        return formula if self.symbol == symbol else self

    @override
    def get_variables(self):
        return {self.symbol}

    @override
    def equals(self, other: Formula) -> bool:
        return isinstance(other, Symbol) and self.symbol == other.symbol
