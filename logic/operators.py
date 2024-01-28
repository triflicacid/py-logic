from logic.formula import Formula


class Operator(Formula):
    pass


class GeneralisedOperator(Operator):
    def __init__(self, formulae: list[Formula], open_tag: str, close_tag: str):
        self.formulae = list(formulae)
        self.open_tag = open_tag
        self.close_tag = close_tag

    def __getitem__(self, idx: int):
        return self.formulae[idx]

    def __setitem__(self, idx: int, value: Formula):
        self.formulae[idx] = value

    def __len__(self):
        return len(self.formulae)

    def __str__(self):
        return self.open_tag + ','.join(map(str, self.formulae)) + self.close_tag

    def append(self, *formula: list[Formula]):
        self.formulae.extend(*formula)

    def remove(self, index: int):
        self.formulae.pop(index)

    def get_variables(self):
        return set().union(*(formula.get_variables() for formula in self.formulae))

    def equals(self, other: Formula) -> bool:
        if not isinstance(other, self.__class__) or len(self.formulae) != len(other.formulae):
            return False

        for i in range(len(self.formulae)):
            if not self.formulae[i].equals(other.formulae[i]):
                return False

        return True

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
        super().__init__()
        self.symbol = symbol
        self.left = left
        self.right = right

    def eval(self, symbols):
        return self.op(self.left.eval(symbols), self.right.eval(symbols))

    def eval_const(self):
        left = self.left.eval_const()
        right = self.right.eval_const()

        if left is None and right is None:
            return None

        # If one is None, try with the other
        if left is None:
            return True if self.op(True, right) and self.op(False, right) else None

        else:
            return True if self.op(left, True) and self.op(left, False) else None

    def __str__(self):
        return f"({self.left}) {self.symbol} ({self.right})"

    def equals(self, other: Formula) -> bool:
        return isinstance(other, self.__class__) and self.left.equals(other.left) and self.right.equals(other.right)

    def get_variables(self):
        return self.left.get_variables() | self.right.get_variables()

    def op(self, a, b):
        # Please override
        raise NotImplementedError


class AndOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('∧', left, right)

    def op(self, a, b):
        return a and b


class NandOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↑', left, right)

    def op(self, a, b):
        return not (a and b)


class GeneralisedConjunction(GeneralisedOperator):
    def __init__(self, *formulae):
        super().__init__(formulae, '⟨', '⟩')

    def eval_const(self):
        encountered_none = False

        for formula in self.formulae:
            ans = formula.eval_const()

            if ans is None:
                encountered_none = True

            elif not ans:
                return False

        return None if encountered_none else True

    def eval(self, symbols):
        for formula in self.formulae:
            if not formula.eval(symbols):
                return False

        return True


class OrOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('∨', left, right)

    def op(self, a, b):
        return a or b


class GeneralisedDisjunction(GeneralisedOperator):
    def __init__(self, *formulae):
        super().__init__(formulae, '[', ']')

    def eval_const(self):
        encountered_none = False

        for formula in self.formulae:
            ans = formula.eval_const()

            if ans is None:
                encountered_none = True

            elif ans:
                return True

        return None if encountered_none else False

    def eval(self, symbols):
        for formula in self.formulae:
            if formula.eval(symbols):
                return True

        return False


class NorOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↓', left, right)

    def op(self, a, b):
        return not (a or b)


class ImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('→', left, right)

    def op(self, a, b):
        return not a or b


class NotImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↛', left, right)

    def op(self, a, b):
        return not (not a or b)


class ReverseImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('←', left, right)

    def op(self, a, b):
        return a or not b


class ReverseNotImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↚', left, right)

    def op(self, a, b):
        return not (a or not b)


class EqualityOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('=', left, right)

    def op(self, a, b):
        return a == b


class NonEqualityOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('≠', left, right)

    def op(self, a, b):
        return a != b


class Negation(Operator):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return '¬' + str(self.data)

    def get_variables(self):
        return self.data.get_variables()

    def eval(self, symbols):
        return not self.data.eval(symbols)

    def eval_const(self):
        ans = self.data.eval_const()
        return None if ans is None else not ans

    def equals(self, other: Formula) -> bool:
        return isinstance(other, Negation) and self.data.equals(other.data)

    @staticmethod
    def nest(formula: Formula, n: int) -> Formula:
        """ Nest `n` negations on the given formula. """
        while n > 0:
            formula = Negation(formula)
            n -= 1

        return formula
