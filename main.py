import algorithm
import parser

if __name__ == "__main__":
    result_symbol = 'φ'
    string = "a = T"
    ok, res = parser.parse(string)

    if not ok:
        print("Parse error!")
        print(res)
        exit(1)

    proposition = res

    print("Proposition " + result_symbol + ": " + str(proposition))

    algorithm.print_truthtable(proposition, result_symbol=result_symbol)

