from formula import Formula


class Operator(Formula):
    pass


class GeneralisedOperator(Operator):
    def __init__(self, formulae: list[Formula], open: str, close: str):
        self.formulae = list(formulae)
        self.open = open
        self.close = close

    def __getitem__(self, idx: int):
        return self.formulae[idx]

    def __setitem__(self, idx: int, value: Formula):
        self.formulae[idx] = value

    def __len__(self):
        return len(self.formulae)

    def __str__(self):
        return self.open + ','.join(map(str, self.formulae)) + self.close

    def append(self, *formula: list[Formula]):
        self.formulae.extend(formula)

    def remove(self, index: int):
        self.formulae.pop(index)

    def get_variables(self):
        return set().union(*(formula.get_variables() for formula in self.formulae))

    def remove_empty_nested(self):
        """ Nested generalised formulae: remove empty formulae """
        i = 0
        while i < len(self.formulae):
            formula = self.formulae[i]

            if isinstance(formula, GeneralisedOperator):
                formula.remove_empty_nested()

                if len(formula) == 0:
                    self.formulae.pop(i)
                    continue

            i += 1


class BinaryOperator(Operator):
    def __init__(self, symbol: str, left, right):
        self.symbol = symbol
        self.left = left
        self.right = right

    def eval(self, symbols):
        return self.op(self.left.eval(symbols), self.right.eval(symbols))

    def eval_const(self):
        l = self.left.eval_const()
        r = self.right.eval_const()

        if l is None and r is None:
            return None

        # If one is None, try with the other
        if l is None:
            return True if self.op(True, r) and self.op(False, r) else None

        else:
            return True if self.op(l, True) and self.op(l, False) else None

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
        raise NotImplementedError


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


class GeneralisedConjunction(GeneralisedOperator):
    def __init__(self, *formulae):
        super().__init__(formulae, '⟨', '⟩')

    def eval_const(self):
        encountered_none = False

        for formula in self.formulae:
            x = formula.eval_const()

            if x is None:
                encountered_none = True

            elif not x:
                return False

        return None if encountered_none else True

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


class GeneralisedDisjunction(GeneralisedOperator):
    def __init__(self, *formulae):
        super().__init__(formulae, '[', ']')

    def eval_const(self):
        encountered_none = False

        for formula in self.formulae:
            x = formula.eval_const()

            if x is None:
                encountered_none = True

            elif x:
                return True

        return None if encountered_none else False

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


class EqualityOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('=', l, r)

    def op(self, a, b):
        return a == b


class NonEqualityOperator(BinaryOperator):
    def __init__(self, l, r):
        super().__init__('≠', l, r)

    def op(self, a, b):
        return a != b


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

    def eval_const(self):
        x = self.data.eval_const()
        return None if x is None else not x

    @staticmethod
    def nest(formula: Formula, n: int) -> Formula:
        """ Nest `n` negations on the given formula """
        while n > 0:
            formula = Negation(formula)
            n -= 1

        return formula
