from logic.formula import Formula


class TruthTable:
    def __init__(self, formula: Formula = None):
        """ Create a wrapper for a truth table. """
        self.formula = formula
        self.bindings = {}  # Existing bindings
        self.variables: list[str] = []  # List of variables
        self.results: list[tuple[list[bool], bool]] = []  # List of results: boolean assignments, result

    def set_formula(self, formula: Formula):
        """ Set the formula to generate a truth table for. Return `self` for chaining. """
        self.formula = formula
        return self

    def set_bindings(self, bindings: dict[str, bool]):
        """ Set truth table bindings (variables whose values are already known). """
        self.bindings = bindings

    def clear_bindings(self):
        self.bindings.clear()

    def get_formula(self) -> Formula:
        """ Get the formula the truth table represents. """
        return self.formula

    def generate(self):
        """ Generate the truth table for the provided formula. Return `self` for chaining. """
        self.variables = sorted([variable for variable in self.formula.get_variables()
                                 if variable not in self.bindings])
        self.results.clear()

        # Stores the current assignment
        state = [False] * len(self.variables)

        while True:
            # Bind variables and calculate result
            assignment = {**{self.variables[i]: state[i] for i in range(len(state))}, **self.bindings}
            result = self.formula.eval(assignment)
            self.results.append((state[:], result))

            # Next Boolean iteration (boolean addition)
            for i in range(len(state) - 1, -1, -1):
                if state[i]:
                    state[i] = False
                else:
                    state[i] = True
                    break

            if not any(state):
                break

        return self

    def print(self, true_symbol='T', false_symbol='F', result_symbol='φ'):
        """ Print the generated truth table. """

        if len(self.results) == 0:
            return

        # Max length of true/false symbols
        max_tf_len = max(len(true_symbol), len(false_symbol))

        # Print symbol headers
        for symbol in [*self.bindings.keys(), *self.variables]:
            print('| ' + symbol.center(max_tf_len, ' ') + ' ', end='')

        print('|| ' + result_symbol.center(max_tf_len) + ' |')

        # Print seperator line
        for symbol in [*self.bindings.keys(), *self.variables]:
            print('|-' + '-' * max(len(symbol), max_tf_len) + '-', end='')

        print('||-' + '-' * max_tf_len + '-|')

        for assignment, result in self.results:
            assignment_info = [(self.variables[i], assignment[i]) for i in range(len(assignment))]
            for i, (symbol, boolean) in enumerate([*self.bindings.items(), *assignment_info]):
                print('| ' + str(true_symbol if boolean else false_symbol).center(max(max_tf_len, len(
                  symbol)), ' ') + ' ', end='')

            print('|| ' + str(true_symbol if result else false_symbol).center(max(max_tf_len, len(
                result_symbol))) + ' |')
