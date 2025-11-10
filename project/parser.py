from expression import MultiplierExpression, AngleExpression, Expression, BracketExpression

# Shitty parser that can only parse basic things
# TODO:
class BasicParser:
    """Parse Strudel pattern strings into Expression objects."""

    def __init__(self, text):
        self.text = text
        self.pos = 0

    def peek(self):
        """Look at current character without consuming it."""
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def consume(self):
        """Consume and return current character."""
        if self.pos >= len(self.text):
            return None
        char = self.text[self.pos]
        self.pos += 1
        return char

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.peek() and self.peek() in ' \t\n':
            self.consume()

    def parse_number(self):
        """Parse a number (integer or float)."""
        num_str = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            num_str += self.consume()

        if '.' in num_str:
            return float(num_str)
        return int(num_str)

    def parse_value(self):
        """Parse a simple value (number, letter, word)."""
        value_str = ""
        while self.peek() and self.peek() not in ' \t\n[]<>*@':
            value_str += self.consume()

        expr = Expression()
        expr.value = value_str
        return expr

    def parse_duration_modifier(self, expr):
        """Parse @n duration modifier and apply it to expression."""
        if self.peek() == '@':
            self.consume()  # consume '@'
            self.skip_whitespace()
            duration = self.parse_number()
            expr.length = duration
        return expr

    def parse_element(self):
        """Parse a single element (value, bracket, or angle)."""
        self.skip_whitespace()

        if self.peek() == '[':
            return self.parse_bracket()
        elif self.peek() == '<':
            return self.parse_angle()
        else:
            expr = self.parse_value()
            return self.parse_duration_modifier(expr)

    def parse_elements(self, end_char):
        """Parse multiple elements until we hit end_char."""
        elements = []
        self.skip_whitespace()

        while self.peek() and self.peek() != end_char:
            elements.append(self.parse_element())
            self.skip_whitespace()

        return elements

    def parse_bracket(self):
        """Parse [...]."""
        self.consume()  # consume '['
        elements = self.parse_elements(']')
        self.consume()  # consume ']'

        bracket = BracketExpression()
        bracket.value = elements if elements else ""

        # Check for duration modifier
        self.parse_duration_modifier(bracket)

        # Check for multiplier
        self.skip_whitespace()
        if self.peek() == '*':
            return self.parse_multiplier(bracket)

        return bracket

    def parse_angle(self):
        """Parse <...>."""
        self.consume()  # consume '<'
        elements = self.parse_elements('>')
        self.consume()  # consume '>'

        angle = AngleExpression()
        angle.value = elements if elements else ""

        # Check for duration modifier
        self.parse_duration_modifier(angle)

        return angle

    def parse_multiplier(self, pattern):
        """Parse *n multiplier."""
        self.consume()  # consume '*'
        multiplier_value = self.parse_number()
        #print('mult', pattern)

        mult = MultiplierExpression()
        mult.value = [pattern]
        mult.multiplier = multiplier_value

        return mult

    def parse(self):
        """Parse the entire expression."""
        self.skip_whitespace()
        return self.parse_element()


def parse_pattern(text):
    """Parse a Strudel pattern string into Expression objects."""
    parser = BasicParser(text)
    return parser.parse()
