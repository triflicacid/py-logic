from typing import Callable

from logic.algorithm import extract_alpha_formula, extract_beta_formula
from logic.formula import Formula
from logic.generalised_operators import GeneralisedConjunction, GeneralisedDisjunction, GeneralisedOperator
from logic.literals import Bottom, Top
from logic.operators import Negation, BinaryOperator


class NormalForm:
    def __init__(self, formula: Formula = None):
        self.original = formula
        self.inner: type[GeneralisedConjunction | GeneralisedDisjunction] | None = None
        self.outer: type[GeneralisedConjunction | GeneralisedDisjunction] | None = None
        self.inner_op: BinaryOperator | None = None

    def configure(self,
                  inner: type[GeneralisedConjunction | GeneralisedDisjunction],
                  outer: type[GeneralisedConjunction | GeneralisedDisjunction]):
        """ Configure normal form algorithm. `inner` and `outer` specify inner/outer generalised groups. """
        self.inner = inner
        self.inner_op = inner.get_operator()
        self.outer = outer

    def configure_conjunctive_normal_form(self):
        """ Configure for CNF. """
        self.inner = GeneralisedDisjunction
        self.inner_op = self.inner.get_operator()
        self.outer = GeneralisedConjunction

    def configure_disjunctive_normal_form(self):
        """ Configure for DNF. """
        self.inner = GeneralisedConjunction
        self.inner_op = self.inner.get_operator()
        self.outer = GeneralisedDisjunction

    def split_formula(self, parts: list[Formula], outer_formulae: list[GeneralisedOperator], outer_index: int,
                      inner_index_skip: int):
        """ Given a list of formulae, create a split in outer_formula. `outer_index` points to the current outer
        formula; copy all segments but `inner_index_skip`. """
        copy_segment = outer_formulae[outer_index][:inner_index_skip] + outer_formulae[outer_index][inner_index_skip+1:]

        for part in parts:
            outer_formulae.append(self.inner(*copy_segment, part))
            self.prepare_formula(outer_formulae, len(outer_formulae) - 1, len(copy_segment))

    def prepare_formula(self, outer_formulae: list[GeneralisedOperator], outer_index: int, inner_index=0,
                        inner_index_upper: int | None = None):
        """ Prepare formula for algorithm: replace all `inner_op` with commas,
        resolve generalised (con/dis)junctions. """
        formulae = outer_formulae[outer_index]

        while (inner_index_upper is None or inner_index < inner_index_upper) and inner_index < len(formulae):
            formula: Formula = formulae[inner_index]

            # Operator: separate via commas
            if isinstance(formula, self.inner_op):
                formulae.append(formula.left)
                formulae.append(formula.right)
                formulae.pop(inner_index)

            # inner generalised: merge into current
            elif isinstance(formula, self.inner):
                formulae.extend(formula)
                formulae.pop(inner_index)

            # outer generalised: split across
            elif isinstance(formula, self.outer):
                self.split_formula(formula, outer_formulae, outer_index, inner_index)
                formulae.pop(inner_index)

            else:
                inner_index += 1

    def process_formula(self, outer_formulae: list[GeneralisedOperator], outer_index: int,
                        inner_formulae: list[Formula], inner_index: int,
                        extract_fn: Callable[[Formula], tuple[Formula | None, Formula | None]],
                        do_split: bool) -> tuple[bool, bool | None]:
        """ Handle alpha or beta formula, splitting or cloning as necessary,
        return (was action taken, requires break). """
        formula: Formula = outer_formulae[outer_index][inner_index]
        p1, p2 = extract_fn(formula)

        if p1 is not None:
            if do_split:
                # Split formula, remove current part
                self.split_formula([p1, p2], outer_formulae, outer_index, inner_index)
                outer_formulae.pop(outer_index)
                return True, True
            else:
                # Add both to current clause, remove old formula
                inner_formulae.append(p1)
                inner_formulae.append(p2)
                inner_formulae.pop(inner_index)
                self.prepare_formula(outer_formulae, outer_index, len(inner_formulae) - 2)
                return True, False

        return False, None

    def transform(self, original: Formula) -> GeneralisedOperator:
        """ Run normal form given loaded configuration. Return result. """

        # Place in inner/outer groups to seed
        outer_formulae = [self.inner(original)]
        self.prepare_formula(outer_formulae, 0)

        # Split alpha formula: alpha formulae involve conjunction, so split if inner is disjunction
        alpha_split = self.inner == GeneralisedDisjunction

        i = 0
        while i < len(outer_formulae):
            inner_formulae = outer_formulae[i]
            j = 0

            while j < len(inner_formulae):
                formula = inner_formulae[j]

                # neg top = bottom
                if isinstance(formula, Negation) and isinstance(formula.data, Top):
                    inner_formulae[j] = Bottom()
                    j += 1
                    continue

                # neg bottom = top
                if isinstance(formula, Negation) and isinstance(formula.data, Bottom):
                    inner_formulae[j] = Top()
                    j += 1
                    continue

                # neg neg X = X
                if isinstance(formula, Negation) and isinstance(formula.data, Negation):
                    inner_formulae[j] = formula.data.data
                    continue

                # Break up any generalised operators to make them decomposable
                if isinstance(formula, GeneralisedOperator):
                    inner_formulae[j] = formula.decompose(True)
                    break

                if isinstance(formula, Negation) and isinstance(formula.data, GeneralisedOperator):
                    inner_formulae[j] = Negation(formula.data.decompose(True))
                    break

                # alpha formula
                ok, requires_break = self.process_formula(outer_formulae, i, inner_formulae, j,
                                                          extract_alpha_formula, alpha_split)
                if ok:
                    if requires_break:
                        break

                    continue

                # beta formula
                ok, requires_break = self.process_formula(outer_formulae, i, inner_formulae, j,
                                                          extract_beta_formula, not alpha_split)
                if ok:
                    if requires_break:
                        break

                    continue

                j += 1

            else:
                i += 1

        # Remove empty clauses
        normal_formula = self.outer(*outer_formulae)
        normal_formula.remove_empty_nested()
        return normal_formula

    @staticmethod
    def conjunctive_normal_form(formula: Formula) -> GeneralisedOperator:
        nf = NormalForm()
        nf.configure_conjunctive_normal_form()
        return nf.transform(formula)

    @staticmethod
    def disjunctive_normal_form(formula: Formula) -> GeneralisedOperator:
        nf = NormalForm()
        nf.configure_disjunctive_normal_form()
        return nf.transform(formula)
