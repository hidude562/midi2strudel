from typing import List


class Expression:
    start_char = ""
    end_char = " "

    def __init__(self):
        self.value: List[Expression] | str = ""
        self.length: List[Expression] | int = 1

        # Used in interpreting. Once all expressions have self.cycle_idx equal to 0 after the cursor goes back to the first idx return the unwrapped
        self.cycle_idx: int = 0

    # Unwrap into the most unfolded version
    # Evaluate until all of the cycles become 1 and the original state
    # TODO:
    def unwrap(self):
        pass

    # Get if two expressions are equivilent / rewrites
    def __eq__(self, other):
        # First unwrap the expressions
        unwrapped_self = self.unwrap()
        unwrapped_other = other.unwrap()

        # Check if the toString is equal
        return unwrapped_self.__str__() == unwrapped_other.__str__()

    def _inner_value_repr(self, inner_value):
        return inner_value

    def __str__(self):
        inner_value = ""
        if isinstance(self.value, List):
            for inner in self.value:
                inner_value += inner.__str__()
        else:
            inner_value = self.value
            if isinstance(self.length, List):
                inner_value += "@"+self.length.__str__()
            else:
                if self.length != 1:
                    inner_value += "@"+str(self.length)

        return self.__class__.start_char + self._inner_value_repr(inner_value) + self.__class__.end_char

class AngleExpression(Expression):
    start_char = "<"
    end_char = ">"

    def unwrap(self):
        pass

class BracketExpression(Expression):
    start_char = "["
    end_char = "]"

    def unwrap(self):
        pass

class MultiplierExpression(Expression):
    start_char = ""
    
    # End char in inner_value_repr
    end_char = ""

    def __init__(self):
        super().__init__()
        self.multiplier = 1

    def _inner_value_repr(self, inner_value):
        return f"{inner_value}*{self.multiplier}"

    def unwrap(self):
        pass

# Track position for expressions
class ExpressionCursor:
    def __init__(self):
        self.call_stack: List[Expression] = []

        # Length, modified when multiplying, etc.
        self.length: float = 1

    # List of recorded value stream output, with the value and length.
    def record(self, expr: Expression):
        self.recorded: list = []
