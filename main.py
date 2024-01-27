import algorithm
import parser

if __name__ == "__main__":
    result_symbol = 'φ'
    string = "[<a, b>, !b]"
    ok, res = parser.parse(string)

    if not ok:
        print("Parse error!")
        print("Input:", string)
        print(res)
        exit(1)

    proposition = res

    print(result_symbol + ": " + str(proposition))
    algorithm.print_truthtable(proposition, result_symbol=result_symbol)
    print()

    cnf = algorithm.conjunctive_normal_form(proposition)
    print("CNF " + result_symbol + ": " + str(cnf))
    algorithm.print_truthtable(cnf, result_symbol=result_symbol)
    print()

    dnf = algorithm.disjunctive_normal_form(proposition)
    print("DNF " + result_symbol + ": " + str(dnf))
    algorithm.print_truthtable(dnf, result_symbol=result_symbol)
    print()

