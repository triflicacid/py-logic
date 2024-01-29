import logic.algorithm as algorithm
from logic.parser import Parser

if __name__ == "__main__":
    result_symbol = 'φ'
    # string = "[a,b,![a, b]]"
    string = "[a, b, !(a + b)]"
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
    algorithm.print_truth_table(proposition, result_symbol=result_symbol)
    print()

    cnf = algorithm.conjunctive_normal_form(proposition)
    print(f"CNF {result_symbol}: {cnf}")
    print(f"Simplified CNF {result_symbol}: {cnf.simplify()}")
    algorithm.print_truth_table(cnf, result_symbol=result_symbol)
    print()

    dnf = algorithm.disjunctive_normal_form(proposition)
    print(f"DNF {result_symbol}: {dnf}")
    print(f"Simplified DNF {result_symbol}: {dnf.simplify()}")
    algorithm.print_truth_table(dnf, result_symbol=result_symbol)
    print()
