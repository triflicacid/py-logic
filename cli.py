from logic.algorithm import rank
from logic.formula import Formula
from logic.parser import Parser
from logic.normal_form import NormalForm
from logic.truth_table import TruthTable


class CLI:
    OPTION_VIEW_SAVED = "1"
    OPTION_WRITE_FORMULA = "2"
    OPTION_COPY_FORMULA = "3"
    OPTION_DELETE_FORMULA = "4"
    OPTION_EVALUATE_FORMULA = "5"
    OPTION_TRUTH_TABLE = "6"
    OPTION_SIMPLIFY_FORMULA = "7"
    OPTION_RANK = "8"
    OPTION_NORMAL_FORM = "9"
    OPTION_SUBSTITUTE = "10"
    OPTION_QUIT = "q"

    def __init__(self):
        self.saved_propositions: dict[str, Formula] = {}
        self.parser = Parser()

    def main(self):
        while True:
            self.print_options()
            option = input("Option: ")
            print()

            if option == CLI.OPTION_VIEW_SAVED:
                self.print_saved()
            elif option == CLI.OPTION_WRITE_FORMULA:
                self.write_formula()
            elif option == CLI.OPTION_COPY_FORMULA:
                self.copy_formula()
            elif option == CLI.OPTION_DELETE_FORMULA:
                self.delete_formula()
            elif option == CLI.OPTION_EVALUATE_FORMULA:
                self.evaluate_formula()
            elif option == CLI.OPTION_TRUTH_TABLE:
                self.show_truth_table()
            elif option == CLI.OPTION_SIMPLIFY_FORMULA:
                self.simplify_formula()
            elif option == CLI.OPTION_RANK:
                self.show_formula_rank()
            elif option == CLI.OPTION_NORMAL_FORM:
                self.to_normal_form()
            elif option == CLI.OPTION_SUBSTITUTE:
                self.substitute_saved_formulae()
            elif option == CLI.OPTION_QUIT:
                break
            else:
                print("Unknown option.\n")
                continue

            input()

    def print_options(self):
        """ Print all available options. """
        print("----- Options -----")
        print(f"{CLI.OPTION_VIEW_SAVED} - View saved propositions.")
        print(f"{CLI.OPTION_WRITE_FORMULA} - Create/overwrite saved proposition.")
        print(f"{CLI.OPTION_COPY_FORMULA} - Copy proposition.")
        print(f"{CLI.OPTION_DELETE_FORMULA} - Remove proposition from memory.")
        print(f"{CLI.OPTION_EVALUATE_FORMULA} - Evaluate proposition.")
        print(f"{CLI.OPTION_TRUTH_TABLE} - Show a proposition's truth table.")
        print(f"{CLI.OPTION_SIMPLIFY_FORMULA} - Simplify proposition.")
        print(f"{CLI.OPTION_RANK} - Calculate proposition's rank.")
        print(f"{CLI.OPTION_NORMAL_FORM} - Convert to normal form.")
        print(f"{CLI.OPTION_SUBSTITUTE} - Substitute saved propositions.")
        print(f"{CLI.OPTION_QUIT} - Quit.")

    def print_saved(self):
        """ Print saved proposiotions. """
        if self.saved_propositions == {}:
            print("(none.)")
        else:
            for symbol, formula in self.saved_propositions.items():
                print(f"{symbol}: {formula}")

    def write_formula(self, symbol: str | None = None, string: str | None = None):
        if symbol is None:
            symbol = input("Enter proposition's symbol: ")

        # Confirm if overwrite
        if symbol in self.saved_propositions:
            if input("A proposition is already stored against this symbol. Overwrite? [y/n] ") != 'y':
                return

        # Get and attempt to parse formula
        if string is None:
            string = input("Enter proposition: ")
        
        ok, parse_result = self.parser.parse(string)

        if ok:
            self.saved_propositions[symbol] = parse_result
            print(f"{symbol}: {parse_result}")
        else:
            print("Parse Error!")
            print(parse_result)

    def copy_formula(self):
        symbol = input("Enter proposition to fetch from memory: ")

        if symbol not in self.saved_propositions:
            print("Symbol not bound in memory.")
            return
        
        print(f"{symbol}: {self.saved_propositions[symbol]}")

        copy_symbol = input("Enter symbol to copy into: ")

        # Confirm if overwrite
        if copy_symbol in self.saved_propositions:
            if input("A proposition is already stored against this symbol. Overwrite? [y/n] ") != 'y':
                return
        
        self.saved_propositions[copy_symbol] = self.saved_propositions[symbol]

    def delete_formula(self, symbol: str | None = None):
        if symbol is None:
            symbol = input("Enter proposition to remove from memory: ")

        if symbol in self.saved_propositions:
            del self.saved_propositions[symbol]
            print("Removed.")
        else:
            print("Symbol not bound in memory.")

    def evaluate_formula(self):
        symbol = input("Enter symbol of proposition to evaluate: ")

        if symbol in self.saved_propositions:
            result = self.saved_propositions[symbol].eval({})
            print(f"{symbol} = {result}")
        else:
            print("Symbol not bound in memory.")

    def show_truth_table(self):
        symbol = input("Enter symbol of proposition: ")

        if symbol in self.saved_propositions:
            print(f"{symbol}: {self.saved_propositions[symbol]}")

            # Allow use to enter bindings
            bindings = {}
            while True:
                binding_symbol = input("Enter symbol to bind, or <Return> to continue: ")
                if len(binding_symbol) == 0:
                    break

                binding_value = input(f"Enter [T/F] value: {binding_symbol}=")
                bindings[binding_symbol] = binding_value.lower() == 't'

            table = TruthTable(self.saved_propositions[symbol])
            table.set_bindings(bindings)
            table.generate()
            table.print()
        else:
            print("Symbol not bound in memory.")

    def simplify_formula(self):
        symbol = input("Enter proposition to fetch from memory: ")

        if symbol not in self.saved_propositions:
            print("Symbol not bound in memory.")
            return

        unsimplified = self.saved_propositions[symbol]
        print(f"Un-simplified: {unsimplified}")

        simplified = unsimplified.simplify()
        print(f"Simplified: {simplified}")

        save = input(f"Overwrite '{symbol}' with its simplification? [y/n] ")
        if save == 'y':
            self.saved_propositions[symbol] = simplified

    def show_formula_rank(self):
        symbol = input("Enter proposition to fetch from memory: ")

        if symbol not in self.saved_propositions:
            print("Symbol not bound in memory.")
            return

        formula = self.saved_propositions[symbol]
        print(f"{symbol}: {formula}")
        print(f"rank({symbol}) = {rank(formula)}")

    def to_normal_form(self):
        form = input("Convert to CNF or DNF? [cnf/dnf/both] ").lower()
        symbol = input("Enter proposition to fetch from memory: ")

        if symbol not in self.saved_propositions:
            print("Symbol not bound in memory.")
            return

        original = self.saved_propositions[symbol]

        if form == "both":
            print(f"Original: {original}")
            print(f"CNF: {NormalForm.conjunctive_normal_form(original)}")
            print(f"DNF: {NormalForm.disjunctive_normal_form(original)}")
            return
        elif form == "cnf":
            converted = NormalForm.conjunctive_normal_form(original)
        elif form == "dnf":
            converted = NormalForm.disjunctive_normal_form(original)
        else:
            print("Unknown form provided.")
            return
        
        print(f"Original: {original}")
        print(f"{form.upper()}: {converted}")

        save = input(f"Overwrite '{symbol}' with the above normal form? [y/n] ")
        if save == 'y':
            self.saved_propositions[symbol] = converted
            print("Ok.")

    def substitute_saved_formulae(self):
        symbol_base = input("Enter symbol of base proposition: ")
        if symbol_base not in self.saved_propositions:
            print("Symbol not bound in memory.")
            return

        print(f"Base: {symbol_base}: {self.saved_propositions[symbol_base]}")

        symbol_sub = input("Enter symbol of proposition to substitute in: ")
        if symbol_sub not in self.saved_propositions:
            print("Symbol not bound in memory.")
            return

        print(f"{symbol_sub}: {self.saved_propositions[symbol_sub]}")

        new_proposition = self.saved_propositions[symbol_base].substitute(symbol_sub,
                                                                          self.saved_propositions[symbol_sub])
        print(f"{symbol_base}': {new_proposition}")

        save = input(f"Overwrite '{symbol_base}' with the above proposition? [y/n] ")
        if save == 'y':
            self.saved_propositions[symbol_base] = new_proposition
            print("Ok.")


if __name__ == "__main__":
    app = CLI()
    # app.write_formula('A', '(a . b) + (!a . !b)')
    app.write_formula('A', 'a + B')
    app.write_formula('B', 'b . c')
    app.main()
