from typing import List, Union, Tuple
import math


class Expression:
    start_char = ""
    end_char = " "

    def __init__(self):
        self.value: Union[List[Expression], str] = ""
        self.length: Union[List[Expression], int] = 1
        self.cycle_idx: int = 0

    def get_total_length(self) -> float:
        """Calculate the total length/duration of this expression"""
        if isinstance(self.length, List):
            # If length is an expression, evaluate it
            return sum(expr.get_total_length() for expr in self.length)
        return float(self.length)

    def get_cycle_length(self) -> int:
        """Get the number of cycles needed for this expression to return to start"""
        if isinstance(self.value, List):
            if not self.value:
                return 1
            # LCM of all sub-expression cycle lengths
            cycles = [expr.get_cycle_length() for expr in self.value]
            result = cycles[0]
            for c in cycles[1:]:
                result = (result * c) // math.gcd(result, c)
            return result
        return 1

    def evaluate_at_position(self, cursor: 'ExpressionCursor') -> List[Tuple[str, float]]:
        """Evaluate expression at current cursor position, return list of (value, duration) pairs"""
        if isinstance(self.value, str):
            return [(self.value, self.get_total_length())]
        return []

    def unwrap(self):
        """Unwrap into the most unfolded version"""
        cursor = ExpressionCursor()
        results = []

        # Calculate how many cycles we need to complete
        total_cycles = self.get_cycle_length()

        # Evaluate for each cycle
        for cycle in range(total_cycles):
            cursor.cycle = cycle
            cycle_results = self.evaluate_at_position(cursor)
            results.extend(cycle_results)

        # Create the unwrapped angle expression
        unwrapped = AngleExpression()
        unwrapped.value = []

        for val, dur in results:
            elem = Expression()
            elem.value = val
            elem.length = dur
            unwrapped.value.append(elem)

        return unwrapped

    def _inner_value_repr(self, inner_value):
        return inner_value

    def __str__(self):
        inner_value = ""
        if isinstance(self.value, List):
            for i, inner in enumerate(self.value):
                if i > 0:
                    inner_value += " "
                inner_value += inner.__str__()
        else:
            inner_value = self.value
            if isinstance(self.length, List):
                inner_value += "@" + self.length.__str__()
            else:
                if self.length != 1:
                    inner_value += "@" + str(self.length)

        return self.__class__.start_char + self._inner_value_repr(inner_value) + self.__class__.end_char


class AngleExpression(Expression):
    start_char = "<"
    end_char = ">"

    def get_cycle_length(self) -> int:
        """Angle expression cycles through all its elements"""
        if isinstance(self.value, List):
            # The angle expression itself takes len(self.value) cycles to complete
            # But we also need to consider nested expressions
            base_cycles = len(self.value) if self.value else 1

            # If any element is also a cycling expression, we need LCM
            nested_cycles = []
            for expr in self.value:
                nested_cycles.append(expr.get_cycle_length())

            # LCM of base_cycles with all nested cycles
            result = base_cycles
            for c in nested_cycles:
                result = (result * c) // math.gcd(result, c)

            return result
        return 1

    def evaluate_at_position(self, cursor: 'ExpressionCursor') -> List[Tuple[str, float]]:
        """Angle brackets alternate between elements on each cycle"""
        if isinstance(self.value, str):
            return [(self.value, self.get_total_length())]

        if isinstance(self.value, List) and self.value:
            # Select which element to play based on the cycle number
            idx = cursor.cycle % len(self.value)
            selected = self.value[idx]

            if isinstance(selected.value, str):
                # Simple value
                return [(selected.value, selected.get_total_length())]
            else:
                # Nested expression - recursively evaluate
                return selected.evaluate_at_position(cursor)

        return []

    def unwrap(self):
        """Unwrap angle expression by showing all values across cycles"""
        if isinstance(self.value, str):
            # Simple string value
            unwrapped = AngleExpression()
            unwrapped.value = self.value
            unwrapped.length = self.length
            return unwrapped

        cursor = ExpressionCursor()
        results = []

        # Calculate how many cycles we need to complete
        total_cycles = self.get_cycle_length()

        # Evaluate for each cycle
        for cycle in range(total_cycles):
            cursor.cycle = cycle
            cycle_results = self.evaluate_at_position(cursor)
            results.extend(cycle_results)

        # Create the unwrapped angle expression
        unwrapped = AngleExpression()
        unwrapped.value = []

        for val, dur in results:
            elem = Expression()
            elem.value = val
            elem.length = dur
            unwrapped.value.append(elem)

        return unwrapped


class BracketExpression(Expression):
    start_char = "["
    end_char = "]"

    def evaluate_at_position(self, cursor: 'ExpressionCursor') -> List[Tuple[str, float]]:
        """Bracket expressions play elements sequentially within a single cycle"""
        if isinstance(self.value, str):
            return [(self.value, self.get_total_length())]

        if isinstance(self.value, List) and self.value:
            results = []
            total_len = self.get_total_length()

            # Calculate total weight (considering lengths)
            total_weight = sum(expr.get_total_length() for expr in self.value)

            for expr in self.value:
                expr_weight = expr.get_total_length()
                expr_duration = (expr_weight / total_weight) * total_len

                if isinstance(expr.value, str):
                    # Simple value
                    results.append((expr.value, expr_duration))
                elif isinstance(expr, AngleExpression):
                    # Angle expression within brackets - evaluate at current cycle
                    nested_results = expr.evaluate_at_position(cursor)
                    # Scale nested results to fit in this slot
                    nested_total = sum(d for _, d in nested_results)
                    if nested_total > 0:
                        scale_factor = expr_duration / nested_total
                        for val, dur in nested_results:
                            results.append((val, dur * scale_factor))
                else:
                    # Other nested expression
                    nested_results = expr.evaluate_at_position(cursor)
                    # Scale nested results to fit in this slot
                    nested_total = sum(d for _, d in nested_results)
                    if nested_total > 0:
                        scale_factor = expr_duration / nested_total
                        for val, dur in nested_results:
                            results.append((val, dur * scale_factor))

            return results

        return []

    def unwrap(self):
        """Unwrap bracket expression into angle expression format"""
        cursor = ExpressionCursor()
        results = []

        # Calculate how many cycles we need to complete
        total_cycles = self.get_cycle_length()

        # Evaluate for each cycle
        for cycle in range(total_cycles):
            cursor.cycle = cycle
            cycle_results = self.evaluate_at_position(cursor)
            results.extend(cycle_results)

        # Create the unwrapped angle expression
        unwrapped = AngleExpression()
        unwrapped.value = []

        for val, dur in results:
            elem = Expression()
            elem.value = val
            elem.length = dur
            unwrapped.value.append(elem)

        return unwrapped


class MultiplierExpression(Expression):
    start_char = ""
    end_char = ""

    def __init__(self):
        super().__init__()
        self.multiplier = 1

    def _inner_value_repr(self, inner_value):
        return f"{inner_value}*{self.multiplier}"

    def get_cycle_length(self) -> int:
        """Multiplier doesn't affect cycle length of the pattern"""
        if isinstance(self.value, List) and len(self.value) == 1:
            return self.value[0].get_cycle_length()
        return 1

    def evaluate_at_position(self, cursor: 'ExpressionCursor') -> List[Tuple[str, float]]:
        """Multiplier repeats the pattern n times within the same duration"""
        if isinstance(self.value, List) and len(self.value) == 1:
            base_expr = self.value[0]

            # For multiplier, we need to evaluate at different "sub-cycles"
            all_results = []
            for rep in range(self.multiplier):
                # Create a modified cursor for this repetition
                sub_cursor = ExpressionCursor()
                # The sub-pattern cycles faster
                sub_cursor.cycle = cursor.cycle * self.multiplier + rep

                base_results = base_expr.evaluate_at_position(sub_cursor)

                for val, dur in base_results:
                    # Each repetition is 1/multiplier of the original duration
                    all_results.append((val, dur / self.multiplier))

            return all_results

        return []

    def unwrap(self):
        """Unwrap multiplier expression by repeating the pattern"""
        if isinstance(self.value, List) and len(self.value) == 1:
            base_expr = self.value[0]
            cursor = ExpressionCursor()
            results = []

            # Calculate total cycles needed
            base_cycles = base_expr.get_cycle_length()

            # We need to go through all cycles to get the complete pattern
            for cycle in range(base_cycles):
                cursor.cycle = cycle
                cycle_results = self.evaluate_at_position(cursor)
                results.extend(cycle_results)

            # Create the unwrapped angle expression
            unwrapped = AngleExpression()
            unwrapped.value = []

            for val, dur in results:
                elem = Expression()
                elem.value = val
                elem.length = dur
                unwrapped.value.append(elem)

            return unwrapped

        return Expression()


class ExpressionCursor:
    def __init__(self):
        self.call_stack: List[Expression] = []
        self.length: float = 1
        self.position: float = 0
        self.cycle: int = 0

    def advance_cycle(self):
        """Move to next cycle"""
        self.cycle += 1
        self.position = 0

    def record(self, expr: Expression):
        self.recorded: list = []

