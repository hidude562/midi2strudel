from typing import List


class Expression:
    start_char = ""
    end_char = " "

    def __init__(self):
        self.value: List[Expression] | str = ""
        self.length: List[Expression] | int = 1

    # Unwrap into the most unfolded version
    # TODO:
    def unwrap(self):
        if self.value is str:
            return self
        else:
            # Unfold the list
            # (There's no function to apply to this)
            for value in self.value:
                value.unwrap()

    # Get if two expressions are equivilent / rewrites
    def __eq__(self, other):
        # First unwrap the expressions
        unwrapped_self = self.unwrap()
        unwrapped_other = other.unwrap()

        # Check if the toString is equal
        return unwrapped_self.__str__() == unwrapped_other.__str__()

    def __str__(self):
        inner_value = ""
        if self.value is List:
            for inner in inner_value:
                inner_value += inner.__str__()
        else:
            inner_value = self.value

        return self.__class__.start_char + inner_value + self.__class__.end_char

# '@' doesnt work on this
class AngleExpression(Expression):
    start_char = "<"
    end_char = ">"

# '@' doesnt work on this
class BracketExpression(Expression):
    start_char = "["
    end_char = "]"

    def unwrap(self):
        pass

class MultiplierExpression(Expression):
    start_char = "*"
    end_char = ""

    def unwrap(self):
        if self.value is str:
            return self
        else:
            # Unfold the list
            # (There's no function to apply to this)
            for value in self.value:
                value.unwrap()
