from typing import override

from logic.formula import Formula
from logic.operators import Operator, Negation, AndOperator, OrOperator
from logic.literals import Literal, Top, Bottom


class GeneralisedOperator(Operator, list):
    def __init__(self, formulae: list[Formula], open_tag: str, close_tag: str):
        super().__init__(formulae)
        self.open_tag = open_tag
        self.close_tag = close_tag

    def __str__(self):
        return self.open_tag + ','.join(map(str, self)) + self.close_tag

    @override
    def get_variables(self):
        return set().union(*(formula.get_variables() for formula in self))

    @override
    def equals(self, other: Formula) -> bool:
        if not isinstance(other, self.__class__) or len(self) != len(other):
            return False

        for i in range(len(self)):
            if not self[i].equals(other[i]):
                return False

        return True

    def get_neutral(self) -> bool:
        """ Get neutral element """
        # Please override
        raise NotImplementedError

    def remove_empty_nested(self):
        """ Nested generalised formulae: remove empty formulae """
        i = 0
        while i < len(self):
            formula = self[i]

            if isinstance(formula, GeneralisedOperator):
                formula.remove_empty_nested()

                if len(formula) == 0:
                    self.pop(i)
                    continue

            i += 1

    @override
    def simplify(self) -> Formula:
        # Check if constant
        value = self.eval_const()
        if value is not None:
            return Literal.from_bool(value)

        # Simplify all formulae
        formulae = [formula.simplify() for formula in self]

        # Atomic?
        if len(formulae) == 1:
            return formulae[0]

        simplified = self._simplify(formulae)

        # Have we simplified into something
        if simplified is not None:
            # Empty?
            if isinstance(simplified, GeneralisedOperator) and len(simplified) == 0:
                return Literal.from_bool(simplified.get_neutral())

            return simplified

        # Else, reconstruct with simplified arguments
        return self.__class__(*formulae)

    def _simplify(self, formulae: list[Formula]) -> Formula | None:
        # Please override
        raise NotImplementedError


class GeneralisedConjunction(GeneralisedOperator):
    def __init__(self, *formulae):
        super().__init__(formulae, '⟨', '⟩')

    @override
    def eval_const(self):
        encountered_none = False

        for formula in self:
            ans = formula.eval_const()

            if ans is None:
                encountered_none = True

            elif not ans:
                return False

        return None if encountered_none else True

    @override
    def get_neutral(self) -> bool:
        return False

    @override
    def eval(self, symbols):
        for formula in self:
            if not formula.eval(symbols):
                return False

        return True

    @override
    def _simplify(self, formulae: list[Formula]) -> Formula | None:
        new_formulae = []
        found_top = False

        for formula in formulae:
            # Remove Top
            if isinstance(formula, Top):
                found_top = True
                continue

            # Does this instance already exist?
            if formula in new_formulae:
                continue

            # Does the negation occur in new_formulae?
            if any(map(lambda f: (isinstance(f, Negation) and formula.equals(f.data)) or
                                 (isinstance(formula, Negation) and formula.data.equals(f)), new_formulae)):
                return Bottom()

            # Preserve element
            new_formulae.append(formula)

        # If empty, we would default to the neutral element. However, if we found Top...
        if len(new_formulae) == 0 and found_top:
            return Top()

        return GeneralisedConjunction(*new_formulae)

    @staticmethod
    def get_operator():
        return AndOperator


class GeneralisedDisjunction(GeneralisedOperator):
    def __init__(self, *formulae):
        super().__init__(formulae, '[', ']')

    @override
    def eval_const(self):
        encountered_none = False

        for formula in self:
            ans = formula.eval_const()

            if ans is None:
                encountered_none = True

            elif ans:
                return True

        return None if encountered_none else False

    @override
    def eval(self, symbols):
        for formula in self:
            if formula.eval(symbols):
                return True

        return False

    @override
    def get_neutral(self) -> bool:
        return True

    @override
    def _simplify(self, formulae: list[Formula]) -> Formula | None:
        new_formulae = []
        found_bottom = False

        for formula in formulae:
            # Remove Bottom
            if isinstance(formula, Bottom):
                found_bottom = True
                continue

            # Does this instance already exist?
            if formula in new_formulae:
                continue

            # Does the negation occur in new_formulae?
            if any(map(lambda f: (isinstance(f, Negation) and formula.equals(f.data)) or
                                 (isinstance(formula, Negation) and formula.data.equals(f)), new_formulae)):
                return Top()

            # Preserve element
            new_formulae.append(formula)

        # If empty, we would default to the neutral element. However, if Bottom was found...
        if len(new_formulae) == 0 and found_bottom:
            return Bottom()

        return GeneralisedDisjunction(*new_formulae)

    @staticmethod
    def get_operator():
        return OrOperator
