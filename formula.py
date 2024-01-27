class Formula:
    def __init__(self):
        pass

    def eval_const(self) -> bool | None:
        """ Evaluate the given node without symbols """
        raise NotImplementedError

    def eval(self, symbols) -> bool:
        """ Evaluate the given node with the given symbols """
        # Please override
        raise NotImplementedError

    def get_variables(self):
        """ Return set of all variables occurring in this formula """
        # Please override
        raise NotImplementedError

    def equals(self, other: 'Formula') -> bool:
        """ Return whether this formula is the same (syntactically) as the given formula """
        # Please override
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, Formula) and self.equals(other)
