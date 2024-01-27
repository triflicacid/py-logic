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
        # Please override
        raise NotImplementedError
