from logic.algorithm import rank
from logic.normal_form import NormalForm
from logic.parser import Parser
from logic.truth_table import TruthTable

truth_tables = True
truth_table = TruthTable() if truth_tables else None

if __name__ == "__main__":
    result_symbol = 'φ'
    string = "(a . b) + (!a . !b)"
    parser = Parser()
    ok, proposition = parser.parse(string)

    if not ok:
        print("Parse error!")
        print("Input:", string)
        print(proposition)
        exit(1)

    print(f"{result_symbol}: {proposition}")
    print(f"Const {result_symbol}: {proposition.eval_const()}")
    print(f"Rank: {rank(proposition)}")
    print(f"Simplified {result_symbol}: {proposition.simplify()}")
    if truth_tables:
        truth_table.set_formula(proposition) \
            .generate() \
            .print(result_symbol=result_symbol)
    print()

    print("----- CNF -----")
    cnf = NormalForm.conjunctive_normal_form(proposition)
    print(f"{result_symbol}: {cnf}")
    print(f"Rank: {rank(cnf)}")
    print(f"Simplified {result_symbol}: {(simplified := cnf.simplify())}")
    if hasattr(simplified, 'decompose'):
        print(f"Simplified decomposed {result_symbol}: {simplified.decompose(True)}")
    if truth_tables:
        truth_table.set_formula(cnf) \
            .generate() \
            .print(result_symbol=result_symbol)
    print()

    print("----- DNF -----")
    dnf = NormalForm.disjunctive_normal_form(proposition)
    print(f"{result_symbol}: {dnf}")
    print(f"Rank: {rank(dnf)}")
    print(f"Simplified {result_symbol}: {(simplified := dnf.simplify())}")
    if hasattr(simplified, 'decompose'):
        print(f"Simplified decomposed {result_symbol}: {simplified.decompose(True)}")
    if truth_tables:
        truth_table.set_formula(dnf) \
            .generate() \
            .print(result_symbol=result_symbol)
    print()
