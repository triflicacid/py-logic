from logic.formula import Formula
from logic.generalised_operators import GeneralisedDisjunction, GeneralisedConjunction, GeneralisedOperator
from logic.literals import Symbol, Top, Bottom
from logic.operators import Negation, AndOperator, OrOperator, ImpliesOperator, ReverseImpliesOperator, NandOperator, \
    NorOperator, NotImpliesOperator, ReverseNotImpliesOperator, NonEqualityOperator, EqualityOperator

TruthTable = list[(dict[str, bool], bool)]


def truth_table(formula: Formula) -> TruthTable:
    """ Return truth table for the given formula """
    variables = sorted(formula.get_variables())
    state = [False] * len(variables)
    table = []

    while True:
        # Create variable assignments
        symbols = {}

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


def print_truth_table(formula: Formula, true_symbol='T', false_symbol='F', result_symbol='φ'):
    """ Same as truthtable(), but print table. """
    # Generate the truth table
    table = truth_table(formula)

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

    for symbols, result in table:
        for symbol in symbols:
            print('| ' + str(true_symbol if symbols[symbol] else false_symbol).center(max(max_tf_len, len(symbol)), ' ')
                  + ' ', end='')

        print('|| ' + str(true_symbol if result else false_symbol).center(max(max_tf_len, len(result_symbol))) + ' |')


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

    # Alpha/Beta formula
    a1, a2 = extract_alpha_formula(formula)
    if a1 is not None:
        return 1 + rank(a1) + rank(a2)

    b1, b2 = extract_beta_formula(formula)
    if b1 is not None:
        return 1 + rank(b1) + rank(b2)

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


def normal_form(original: Formula,
                inner: type[GeneralisedConjunction | GeneralisedDisjunction],
                outer: type[GeneralisedConjunction | GeneralisedDisjunction],
                alpha_split: bool,
                beta_split: bool) -> GeneralisedOperator:
    """ General normal form method. `inner` and `outer` specify inner/outer generalised groups. `_split` determines
    whether to split on the formula type. `inner_op` is the operator to simply replace with commas. """

    inner_op = inner.get_operator()

    def split_formula(parts: list[Formula], outer_index: int, inner_index_skip: int):
        """ Given a list of formulae, create a split in outer_formula. `outer_index` points to the current outer
        formula; copy all segments but `inner_index_skip`. """
        copy_segment = outer_formulae[outer_index][:inner_index_skip] + outer_formulae[outer_index][inner_index_skip+1:]

        for part in parts:
            outer_formulae.append(inner(*copy_segment, part))
            prepare_formula(len(outer_formulae) - 1, len(copy_segment))

    def prepare_formula(outer_index: int, inner_index=0, inner_index_upper: int | None = None):
        """ Prepare formula for algorithm: replace all `inner_op` with commas,
        resolve generalised (con/dis)junctions. """
        formulae = outer_formulae[outer_index]

        while (inner_index_upper is None or inner_index < inner_index_upper) and inner_index < len(formulae):
            formula = formulae[inner_index]

            # Operator: separate via commas
            if isinstance(formula, inner_op):
                formulae.append(formula.left)
                formulae.append(formula.right)
                formulae.pop(inner_index)

            # inner generalised: merge into current
            elif isinstance(formula, inner):
                formulae.extend(formula)
                formulae.pop(inner_index)

            # outer generalised: split across
            elif isinstance(formula, outer):
                split_formula(formula, outer_index, inner_index)
                formulae.pop(inner_index)

            else:
                inner_index += 1

    def process_formula(formula: Formula, extract_fn, do_split: bool) -> tuple[bool, bool | None]:
        """ Handle alpha or beta formula, return (was action taken, requires break) """
        p1, p2 = extract_fn(formula)

        if p1 is not None:
            if do_split:
                # Split formula, remove current part
                split_formula([p1, p2], i, j)
                outer_formulae.pop(i)
                return True, True
            else:
                # Add both to current clause, remove old formula
                inner_formulae.append(p1)
                inner_formulae.append(p2)
                inner_formulae.pop(j)
                prepare_formula(i, len(inner_formulae) - 2)
                return True, False

        return False, None

    # Place in inner/outer groups to seed
    outer_formulae = [inner(original)]
    prepare_formula(0)

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

            # alpha formula
            ok, requires_break = process_formula(formula, extract_alpha_formula, alpha_split)
            if ok:
                if requires_break:
                    break

                continue

            # beta formula
            ok, requires_break = process_formula(formula, extract_beta_formula, beta_split)
            if ok:
                if requires_break:
                    break

                continue

            j += 1

        else:
            i += 1

    # Remove empty clauses
    normal_formula = outer(*outer_formulae)
    normal_formula.remove_empty_nested()
    return normal_formula


def conjunctive_normal_form(formula: Formula):
    return normal_form(formula, GeneralisedDisjunction, GeneralisedConjunction, True, False)


def disjunctive_normal_form(formula: Formula):
    return normal_form(formula, GeneralisedConjunction, GeneralisedDisjunction, False, True)
