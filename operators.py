from formula import Formula


class Operator(Formula):
    pass


class BinaryOperator(Operator):
    def __init__(self, symbol: str, left, right):
        self.symbol = symbol
        self.left = left
        self.right = right

    def eval(self, symbols):
        return self.op(self.left.eval(symbols), self.right.eval(symbols))

    def __str__(self):
        return "(" + str(self.left) + " " + self.symbol + " " + str(self.right) + ")"

    def set_left(self, left):
        self.left = left
        return self

    def set_right(self, right):
        self.right = right
        return self

    def get_variables(self):
        return self.left.get_variables() | self.right.get_variables()

    def op(self, a, b):
        # Please override
        pass


class AndOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('∧', l, r)

    def op(self, a, b):
        return a and b


class NandOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('↑', l, r)

    def op(self, a, b):
        return not (a and b)


class GeneralisedConjunction(Operator):
    def __init__(self, *formulae):
        self.formulae = formulae

    def __str__(self):
        return '⟨' + ','.join(map(str, self.formulae)) + '⟩'

    def get_variables(self):
        return set().union(*(formula.get_variables() for formula in self.formulae))

    def eval(self, symbols):
        for formula in self.formulae:
            if not formula.eval(symbols):
                return False

        return True


class OrOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('∨', l, r)

    def op(self, a, b):
        return a or b


class GeneralisedDisjunction(Operator):
    def __init__(self, *formulae):
        self.formulae = formulae

    def __str__(self):
        return '[' + ','.join(map(str, self.formulae)) + ']'

    def get_variables(self):
        return set().union(*(formula.get_variables() for formula in self.formulae))

    def eval(self, symbols):
        for formula in self.formulae:
            if formula.eval(symbols):
                return True

        return False


class NorOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('↓', l, r)

    def op(self, a, b):
        return not (a or b)


class ImpliesOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('→', l, r)

    def op(self, a, b):
        return not a or b


class NimpliesOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('↛', l, r)

    def op(self, a, b):
        return not (not a or b)


class ReverseImpliesOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('←', l, r)

    def op(self, a, b):
        return a or not b


class ReverseNimpliesOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('↚', l, r)

    def op(self, a, b):
        return not (a or not b)


class Negation(Operator):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return '¬' + str(self.data)

    def get_variables(self):
        return self.data.get_variables()

    def set(self, data):
        self.data = data
        return self

    def eval(self, symbols):
        return not self.data.eval(symbols)

    @staticmethod
    def nest(formula: Formula, n: int) -> Formula:
        """ Nest `n` negations on the given formula """
        while n > 0:
            formula = Negation(formula)
            n -= 1

        return formula
