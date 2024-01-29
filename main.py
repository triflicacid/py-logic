import logic.algorithm as algorithm
from logic.parser import Parser

truth_tables = True

if __name__ == "__main__":
    result_symbol = 'φ'
    # string = "[a,b,![![a, b]]]"
    string = "a (+) b"
    parser = Parser()
    ok, proposition = parser.parse(string)

    if not ok:
        print("Parse error!")
        print("Input:", string)
        print(proposition)
        exit(1)

    print(f"{result_symbol}: {proposition}")
    print(f"Const {result_symbol}: {proposition.eval_const()}")
    print(f"Simplified {result_symbol}: {proposition.simplify()}")
    if truth_tables:
        algorithm.print_truth_table(proposition, result_symbol=result_symbol)
    print()

    print("----- CNF -----")
    cnf = algorithm.conjunctive_normal_form(proposition)
    print(f"{result_symbol}: {cnf}")
    print(f"Simplified {result_symbol}: {(simplified := cnf.simplify())}")
    print(f"Simplified decomposed {result_symbol}: {simplified.decompose(True)}")
    if truth_tables:
        algorithm.print_truth_table(cnf, result_symbol=result_symbol)
    print()

    print("----- DNF -----")
    dnf = algorithm.disjunctive_normal_form(proposition)
    print(f"{result_symbol}: {dnf}")
    print(f"Simplified {result_symbol}: {(simplified := dnf.simplify())}")
    print(f"Simplified decomposed {result_symbol}: {simplified.decompose(True)}")
    if truth_tables:
        algorithm.print_truth_table(dnf, result_symbol=result_symbol)
    print()
