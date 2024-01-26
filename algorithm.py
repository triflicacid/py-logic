from formula import Formula
from operators import *
from literals import Symbol, Top, Bottom


def truthtable(formula: Formula) -> list[(dict[str, bool], bool)]:
    """ Return truthtable for the given formula """
    variables = sorted(formula.get_variables())
    state = [False] * len(variables)
    table = []

    while True:
        # Create variable assignments
        symbols = dict()
        for i in range(len(variables)):
            symbols[variables[i]] = state[i]

        # Calculate result
        result = formula.eval(symbols)

        # Add to truth table
        table.append((symbols, result))

        # Next Boolean iteration (boolean addition)
        for i in range(len(variables) - 1, -1, -1):
            if state[i]:
                state[i] = False
            else:
                state[i] = True
                break

        if not any(state):
            break

    return table


def print_truthtable(formula: Formula, true_symbol = "T", false_symbol = "F", result_symbol = "φ"):
    """ Same as truthtable(), but print table """
    # Generate the truth table
    table = truthtable(formula)

    if len(table) == 0:
        return

    # Max length of true/false symbols
    max_tf_len = max(len(true_symbol), len(false_symbol))

    # Print symbol headers
    for symbol in table[0][0]:
        print('| ' + symbol.center(max_tf_len, ' ') + ' ', end='')

    print('|| ' + result_symbol.center(max_tf_len) + ' |')

    # Print seperator line
    for symbol in table[0][0]:
        print('|-' + '-' * max(len(symbol), max_tf_len) + '-', end='')

    print('||-' + '-' * max_tf_len + '-|')

    for (symbols, result) in table:
        for symbol in symbols:
            print('| ' + str(true_symbol if symbols[symbol] else false_symbol).center(max(max_tf_len, len(symbol)), ' ') + ' ', end='')

        print('|| ' + str(true_symbol if result else false_symbol).center(max(max_tf_len, len(result_symbol))) + ' |')


def rank(formula: Formula) -> int:
    """ Determine a formula's rank """
    # r([x1, x2, ...]) = SUM r(r_i)
    if isinstance(formula, GeneralisedDisjunction) or isinstance(formula, GeneralisedConjunction):
        return sum(map(rank, formula.formulae))

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

    # Alpha/Beta formula
    (a1, a2) = extract_alpha_formula(formula)
    if a1 is not None:
        return 1 + rank(a1) + rank(a2)

    (b1, b2) = extract_beta_formula(formula)
    if b1 is not None:
        return 1 + rank(b1) + rank(b2)

    raise ValueError(formula)


def extract_alpha_formula(formula: Formula) -> (Formula | None, Formula | None):
    """ Given a formula, return alpha_1, alpha_2 if it is in alpha (conjunction) formula """

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
        return Negation(formula.data.left), Negation(formula.data.right)

    # X NIMPLIES Y
    if isinstance(formula, NimpliesOperator):
        return formula.left, Negation(formula.right)

    # X REV. NIMPLIES Y
    if isinstance(formula, ReverseNimpliesOperator):
        return Negation(formula.left), formula.right

    return None, None


def extract_beta_formula(formula: Formula) -> (Formula | None, Formula | None):
    """ Given a formula, return beta_a, beta_2 if it is a beta (disjunction) formula """

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

    #  NOT (X NIMPLIES Y)
    if isinstance(formula, Negation) and isinstance(formula.data, NimpliesOperator):
        return Negation(formula.data.left), formula.data.right

    # NOT (X REV. NIMPLIES Y)
    if isinstance(formula, Negation) and isinstance(formula.data, ReverseNimpliesOperator):
        return formula.data.left, Negation(formula.data.right)

    return None, None

