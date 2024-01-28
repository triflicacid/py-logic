import logic.algorithm as algorithm
import logic.parser as parser

if __name__ == "__main__":
    result_symbol = 'φ'
    string = "a -> a"
    ok, res = parser.parse(string)

    if not ok:
        print("Parse error!")
        print("Input:", string)
        print(res)
        exit(1)

    proposition = res

    print(result_symbol + ": " + str(proposition))
    print("const: " + str(proposition.eval_const()))
    algorithm.print_truth_table(proposition, result_symbol=result_symbol)
    print()

    cnf = algorithm.conjunctive_normal_form(proposition)
    print("CNF " + result_symbol + ": " + str(cnf))
    algorithm.print_truth_table(cnf, result_symbol=result_symbol)
    print()

    dnf = algorithm.disjunctive_normal_form(proposition)
    print("DNF " + result_symbol + ": " + str(dnf))
    algorithm.print_truth_table(dnf, result_symbol=result_symbol)
    print()
