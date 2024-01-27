from formula import Formula


class Literal(Formula):
    def __init__(self):
        pass


class Top(Literal):
    symbol = '⊤'

    def __init__(self):
        pass

    def __str__(self):
        return Top.symbol

    def get_variables(self):
        return set()

    def eval_const(self):
        return True

    def eval(self, symbols):
        return True

    def equals(self, other: 'Formula') -> bool:
        return isinstance(other, Top)


class Bottom(Literal):
    symbol = '⊥'

    def __init__(self):
        pass

    def __str__(self):
        return Bottom.symbol

    def get_variables(self):
        return set()

    def eval_const(self):
        return False

    def eval(self, symbols):
        return False

    def equals(self, other: 'Formula') -> bool:
        return isinstance(other, Bottom)


class Symbol(Literal):
    def __init__(self, symbol: str):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def eval_const(self):
        # Value of symbol is not const
        return None

    def eval(self, symbols):
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

    def get_variables(self):
        return {self.symbol}

    def equals(self, other: 'Formula') -> bool:
        return isinstance(other, Symbol) and self.symbol == other.symbol
