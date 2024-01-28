from __future__ import annotations


class Formula:
    def eval_const(self) -> bool | None:
        """ Evaluate the given node without symbols """
        raise NotImplementedError

    def eval(self, symbols: dict[str, bool]) -> bool:
        """ Evaluate the given node with the given symbols """
        # Please override
        raise NotImplementedError

    def get_variables(self) -> set[str]:
        """ Return set of all variables occurring in this formula """
        # Please override
        raise NotImplementedError

    def equals(self, other: Formula) -> bool:
        """ Return whether this formula is the same (syntactically) as the given formula """
        # Please override
        raise NotImplementedError

    def simplify(self) -> Formula:
        """ Simplify the given formula (i.e., resolve 'a + a') """
        # Please override
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, Formula) and self.equals(other)
