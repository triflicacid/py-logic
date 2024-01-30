from logic.formula import Formula
from logic.generalised_operators import GeneralisedOperator
from logic.literals import Symbol, Top, Bottom
from logic.operators import Negation, AndOperator, OrOperator, ImpliesOperator, ReverseImpliesOperator, NandOperator, \
    NorOperator, NotImpliesOperator, ReverseNotImpliesOperator, NonEqualityOperator, EqualityOperator


def rank(formula: Formula) -> int:
    """ Determine a formula's rank. """
    # r([x1, x2, ...]) = SUM r(r_i)
    if isinstance(formula, GeneralisedOperator):
        return sum(map(rank, formula))

    # r(x) = rank(neg x) = 0
    if isinstance(formula, Symbol) or (isinstance(formula, Negation) and isinstance(formula.data, Symbol)):
        return 0

    # r(top) = rank(bottom) = 0
    if isinstance(formula, Top) or isinstance(formula, Bottom):
        return 0

    # r(neg top) = r(neg bottom) = 1
    if isinstance(formula, Negation) and (isinstance(formula.data, Top) or isinstance(formula.data, Bottom)):
        return 1

    # r(neg neg X) = r(X)
    if isinstance(formula, Negation) and isinstance(formula.data, Negation):
        return 1 + rank(formula.data.data)

    # decompose if necessary
    if isinstance(formula, GeneralisedOperator):
        return rank(formula.decompose(True))

    if isinstance(formula, Negation) and isinstance(formula.data, GeneralisedOperator):
        return rank(Negation(formula.data.decompose(True)))

    # Alpha/Beta formula
    a1, a2 = extract_alpha_formula(formula)
    if a1 is not None:
        return 1 + rank(a1) + rank(a2)

    b1, b2 = extract_beta_formula(formula)
    if b1 is not None:
        return 1 + rank(b1) + rank(b2)

    print(formula)

    raise ValueError


def extract_alpha_formula(formula: Formula) -> tuple[Formula | None, Formula | None]:
    """ Given a formula, return alpha_1, alpha_2 if it is in alpha (conjunction) formula. """

    # X AND Y
    if isinstance(formula, AndOperator):
        return formula.left, formula.right

    # NOT (X OR Y)
    if isinstance(formula, Negation) and isinstance(formula.data, OrOperator):
        return Negation(formula.data.left), Negation(formula.data.right)

    # NOT (X IMPLIES Y)
    if isinstance(formula, Negation) and isinstance(formula.data, ImpliesOperator):
        return formula.data.left, Negation(formula.data.right)

    # NOT (X REV. IMPLIES Y)
    if isinstance(formula, Negation) and isinstance(formula.data, ReverseImpliesOperator):
        return Negation(formula.data.left), formula.data.right

    # NOT (X NAND Y)
    if isinstance(formula, Negation) and isinstance(formula.data, NandOperator):
        return formula.data.left, formula.data.right

    # X NOR Y
    if isinstance(formula, NorOperator):
        return Negation(formula.left), Negation(formula.right)

    # X NOT IMPLIES Y
    if isinstance(formula, NotImpliesOperator):
        return formula.left, Negation(formula.right)

    # X REV. NOT IMPLIES Y
    if isinstance(formula, ReverseNotImpliesOperator):
        return Negation(formula.left), formula.right

    # X NOT EQUALS Y
    if isinstance(formula, NonEqualityOperator):
        return OrOperator(formula.left, formula.right), Negation(AndOperator(formula.left, formula.right))

    # NOT (X EQUALS Y)
    if isinstance(formula, Negation) and isinstance(formula.data, EqualityOperator):
        return OrOperator(formula.data.left, formula.data.right), Negation(AndOperator(formula.data.left,
                                                                                       formula.data.right))

    return None, None


def extract_beta_formula(formula: Formula) -> tuple[Formula | None, Formula | None]:
    """ Given a formula, return beta_a, beta_2 if it is a beta (disjunction) formula. """

    # NOT (X AND Y)
    if isinstance(formula, Negation) and isinstance(formula.data, AndOperator):
        return Negation(formula.data.left), Negation(formula.data.right)

    # X OR Y
    if isinstance(formula, OrOperator):
        return formula.left, formula.right

    # X IMPLIES Y
    if isinstance(formula, ImpliesOperator):
        return Negation(formula.left), formula.right

    # X REV. IMPLIES Y
    if isinstance(formula, ReverseImpliesOperator):
        return formula.left, Negation(formula.right)

    # X NAND Y
    if isinstance(formula, NandOperator):
        return Negation(formula.left), Negation(formula.right)

    # NOT (X NOR Y)
    if isinstance(formula, Negation) and isinstance(formula.data, NorOperator):
        return formula.data.left, formula.data.right

    #  NOT (X NOT IMPLIES Y)
    if isinstance(formula, Negation) and isinstance(formula.data, NotImpliesOperator):
        return Negation(formula.data.left), formula.data.right

    # NOT (X REV. NOT IMPLIES Y)
    if isinstance(formula, Negation) and isinstance(formula.data, ReverseNotImpliesOperator):
        return formula.data.left, Negation(formula.data.right)

    # X EQUALS Y
    if isinstance(formula, EqualityOperator):
        return AndOperator(Negation(formula.left), Negation(formula.right)), AndOperator(formula.left, formula.right)

    # NOT (X NOT EQUALS Y)
    if isinstance(formula, Negation) and isinstance(formula.data, NonEqualityOperator):
        return AndOperator(Negation(formula.data.left), Negation(formula.data.right)), AndOperator(formula.data.left,
                                                                                                   formula.data.right)

    return None, None


