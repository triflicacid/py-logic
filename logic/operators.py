from __future__ import annotations
from typing import override

from logic.formula import Formula
from logic.literals import Bottom, Top, Literal


class Operator(Formula):
    pass


class BinaryOperator(Operator):
    def __init__(self, symbol: str, left, right):
        super().__init__()
        self.symbol = symbol
        self.left = left
        self.right = right

    @override
    def eval(self, symbols):
        return self.op(self.left.eval(symbols), self.right.eval(symbols))

    @override
    def eval_const(self):
        left = self.left.eval_const()
        right = self.right.eval_const()

        # left=T/F, right=T/F
        if left is not None and right is not None:
            return self.op(left, right)

        # left=None, right=None
        if left is None and right is None:
            return None

        # left=None, right=T/F
        # If one is None, try with the other
        if left is None:
            eval_true, eval_false = self.op(True, right), self.op(False, right)
            return eval_true if eval_true == eval_false else None

        # left=T/F, right=None
        eval_true, eval_false = self.op(left, True), self.op(left, False)
        return eval_true if eval_true == eval_false else None

    def __str__(self):
        return f"({self.left} {self.symbol} {self.right})"

    @override
    def equals(self, other: Formula) -> bool:
        return isinstance(other, self.__class__) and self.left.equals(other.left) and self.right.equals(other.right)

    @override
    def get_variables(self):
        return self.left.get_variables() | self.right.get_variables()

    def negate(self) -> type(BinaryOperator):
        """ Negate this operator """
        raise NotImplementedError

    def __neg__(self):
        return self.negate()

    @override
    def simplify(self) -> Formula:
        """ Simplify the given formula (basic only; no fancy expansions). """
        # Check if constant; that'd be silly
        value = self.eval_const()
        if value is not None:
            return Literal.from_bool(value)

        # Call __simplify with simplified arguments
        left, right = self.left.simplify(), self.right.simplify()
        simplified = self._simplify(left, right)

        # Pass with simplified arguments, or return fully simplified stub
        return self.__class__(left, right) if simplified is None else simplified

    def _simplify(self, left: Formula, right: Formula) -> Formula | None:
        """ Helper for simplify(): Default is to negate the simplified negated variant, so override
        lest a stack overflow ensue. Note, this method assumes that this operator does not return a constant value. """
        # Please override in at least one negation pair for each operator
        return Negation(self.negate()).simplify()

    def op(self, a, b):
        # Please override
        raise NotImplementedError


class AndOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('∧', left, right)

    @override
    def op(self, a, b):
        return a and b

    @override
    def _simplify(self, left: Formula, right: Formula) -> Formula | None:
        # L = R
        if left.equals(right):
            return left

        # One is true
        if left.eval_const() is True:
            return right

        if right.eval_const() is True:
            return left

        # L = !R / !L = R
        if (isinstance(right, Negation) and left.equals(right.data)) or \
                (isinstance(left, Negation) and right.equals(left.data)):
            return Bottom()

    @override
    def negate(self):
        return NandOperator(self.left, self.right)

    @staticmethod
    def get_negated():
        return NandOperator


class NandOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↑', left, right)

    @override
    def op(self, a, b):
        return not (a and b)

    @override
    def negate(self) -> type(BinaryOperator):
        return AndOperator(self.left, self.right)

    @staticmethod
    def get_negated():
        return AndOperator

class OrOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('∨', left, right)

    @override
    def op(self, a, b):
        return a or b

    @override
    def _simplify(self, left: Formula, right: Formula) -> Formula | None:
        # L = R
        if left.equals(right):
            return left

        # One is false
        if left.eval_const() is False:
            return right

        if right.eval_const() is False:
            return left

        # L = !R / !L = R
        if (isinstance(right, Negation) and left.equals(right.data)) or \
                (isinstance(left, Negation) and right.equals(left.data)):
            return Top()

    @override
    def negate(self) -> type(BinaryOperator):
        return NorOperator(self.left, self.right)

    @staticmethod
    def get_negated():
        return NorOperator


class NorOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↓', left, right)

    @override
    def op(self, a, b):
        return not (a or b)

    @override
    def negate(self) -> type(BinaryOperator):
        return OrOperator(self.left, self.right)

    @staticmethod
    def get_negated():
        return OrOperator


class ImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('→', left, right)

    @override
    def op(self, a, b):
        return not a or b

    @override
    def negate(self) -> type(BinaryOperator):
        return NotImpliesOperator(self.left, self.right)

    @override
    def _simplify(self, left: Formula, right: Formula) -> Formula | None:
        # If equal, always True
        if left.equals(right):
            return Top()

        # !a -> a ==> a
        if isinstance(left, Negation) and left.data.equals(right):
            return right

        # a -> !a ==> !a
        if isinstance(right, Negation) and left.equals(right.data):
            return right

        # If left is Top, depends on right
        if left.eval_const() is True:
            return right

        # If right is Bottom, depends on negated left
        if right.eval_const() is False:
            return Negation(left)

    @staticmethod
    def get_negated():
        return NotImpliesOperator


class NotImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↛', left, right)

    def op(self, a, b):
        return not (not a or b)

    def negate(self) -> type(BinaryOperator):
        return ImpliesOperator(self.left, self.right)

    @staticmethod
    def get_negated():
        return ImpliesOperator


class ReverseImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('←', left, right)

    @override
    def op(self, a, b):
        return a or not b

    @override
    def negate(self) -> type(BinaryOperator):
        return ReverseNotImpliesOperator(self.left, self.right)

    @override
    def _simplify(self, left: Formula, right: Formula) -> Formula | None:
        # If equal, always True
        if left.equals(right):
            return Top()

        # a <- !a ==> a
        if isinstance(right, Negation) and left.equals(right.data):
            return left

        # !a <- a ==> !a
        if isinstance(left, Negation) and left.data.equals(right):
            return left

        # If left is Bottom, depends on negated right
        if left.eval_const() is False:
            return Negation(right)

        # If right is Top, depends on left
        if right.eval_const() is True:
            return left

    @staticmethod
    def get_negated():
        return ReverseNotImpliesOperator


class ReverseNotImpliesOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('↚', left, right)

    def op(self, a, b):
        return not (a or not b)

    def negate(self) -> type(BinaryOperator):
        return ReverseImpliesOperator(self.left, self.right)

    @staticmethod
    def get_negated():
        return ReverseImpliesOperator


class EqualityOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('=', left, right)

    @override
    def op(self, a, b):
        return a == b

    @override
    def negate(self) -> type(BinaryOperator):
        return NonEqualityOperator(self.left, self.right)

    @override
    def _simplify(self, left: Formula, right: Formula) -> Formula | None:
        # Equal
        if left.equals(right):
            return Top()

        # Equal negation
        if (isinstance(left, Negation) and left.data.equals(right)) or \
                (isinstance(right, Negation) and left.equals(right.data)):
            return Bottom()

    @staticmethod
    def get_negated():
        return NonEqualityOperator


class NonEqualityOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__('≠', left, right)

    @override
    def op(self, a, b):
        return a != b

    @override
    def negate(self) -> type(BinaryOperator):
        return EqualityOperator(self.left, self.right)

    @staticmethod
    def get_negated():
        return EqualityOperator


class Negation(Operator):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return '¬' + str(self.data)

    @override
    def get_variables(self):
        return self.data.get_variables()

    @override
    def eval(self, symbols):
        return not self.data.eval(symbols)

    @override
    def eval_const(self):
        ans = self.data.eval_const()
        return None if ans is None else not ans

    @override
    def equals(self, other: Formula) -> bool:
        return isinstance(other, Negation) and self.data.equals(other.data)

    @override
    def simplify(self) -> Formula:
        # Double negation? We can be slightly more efficient.
        if isinstance(self.data, Negation):
            simplified = self.data.data.simplify()
            value = simplified.eval_const()

            if value is None:
                return simplified
            else:
                return Literal.from_bool(value)
        else:
            simplified = self.data.simplify()
            value = simplified.eval_const()

            if value is None:
                # Check for last-minute double-negation
                return simplified.data if isinstance(simplified, Negation) else Negation(simplified)
            else:
                return Literal.from_bool(not value)

    @staticmethod
    def nest(formula: Formula, n: int) -> Formula:
        """ Nest `n` negations on the given formula. """
        while n > 0:
            formula = Negation(formula)
            n -= 1

        return formula
