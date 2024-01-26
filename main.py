import algorithm
import parser

if __name__ == "__main__":
    string = "a -> b"
    ok, res = parser.parse(string)

    if not ok:
        print("Parse error!")
        print(res)
        exit(1)

    proposition = res

    print(str(proposition))

    algorithm.print_truthtable(proposition)

