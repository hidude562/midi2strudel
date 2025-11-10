from typing import List, Union

class Expression:
    start_char = ""
    end_char = " "

    def __init__(self):
        self.value: Union[List['Expression'], str] = ""
        self.length: Union[List['Expression'], int] = 1
        self.duration_modifier = 1.0  # Default duration multiplier

    def unwrap(self):
        """
        Unwrap into the most unfolded version.
        Returns a new Expression with all special constructs expanded.
        """
        if isinstance(self.value, str):
            # Leaf node - return a copy
            result = self.__class__()
            result.value = self.value
            result.duration_modifier = self.duration_modifier
            return result
        else:
            # Recursively unwrap all children first
            unwrapped_children = []
            for child in self.value:
                unwrapped_child = child.unwrap()
                unwrapped_children.append(unwrapped_child)

            # Create new expression with unwrapped children
            result = self.__class__()
            result.value = unwrapped_children
            result.duration_modifier = self.duration_modifier
            return result

    def __eq__(self, other):
        # First unwrap the expressions
        unwrapped_self = self.unwrap()
        unwrapped_other = other.unwrap()

        # Check if the toString is equal
        return str(unwrapped_self) == str(unwrapped_other)

    def __str__(self):
        inner_value = ""
        if isinstance(self.value, list):
            for inner in self.value:
                inner_value += str(inner)
        else:
            inner_value = self.value

        # Add duration modifier for leaf nodes if not default
        if isinstance(self.value, str) and self.duration_modifier != 1.0:
            return self.value + f"@{self.duration_modifier}"

        return self.__class__.start_char + inner_value + self.__class__.end_char

    def flatten_to_elements(self):
        """Helper to flatten to leaf elements with calculated durations."""
        if isinstance(self.value, str):
            return [(self.value, self.duration_modifier)]

        result = []
        for child in self.value:
            child_elements = child.flatten_to_elements()
            # Multiply each child's duration by this node's duration modifier
            # This makes durations hierarchical/multiplicative
            scaled_elements = [(val, dur * self.duration_modifier) for val, dur in child_elements]
            result.extend(scaled_elements)
        return result

    def calculate_normalized_durations(self):
        """Calculate normalized durations for all leaf elements."""
        elements = self.flatten_to_elements()
        total_duration = sum(duration for _, duration in elements)

        if total_duration == 0:
            return elements

        return [(value, duration / total_duration) for value, duration in elements]


class AngleExpression(Expression):
    """
    Angle brackets create alternating/polymeter patterns.
    <a b c> means alternate through a, b, c on successive cycles.
    """
    start_char = "<"
    end_char = ">"

    def get_nested_cycle_count(self):
        """
        Calculate how many cycles are needed to fully expand this angle and any nested angles.
        """
        if isinstance(self.value, str):
            return 1

        # Get the maximum cycle count from children
        max_child_cycles = 1
        for child in self.value:
            if isinstance(child, BracketExpression):
                # Check if bracket contains angles
                child_cycles = child.get_nested_cycle_count()
                max_child_cycles = max(max_child_cycles, child_cycles)
            elif isinstance(child, AngleExpression):
                child_cycles = child.get_nested_cycle_count()
                max_child_cycles = max(max_child_cycles, child_cycles)

        # Total cycles = our length * max child cycles
        return len(self.value) * max_child_cycles

    def unwrap(self):
        """
        Unwrap angle brackets by expanding into all cycles.
        """
        if isinstance(self.value, str):
            result = Expression()
            result.value = self.value
            result.duration_modifier = self.duration_modifier
            return result

        # First, recursively unwrap all children
        unwrapped_children = []
        for child in self.value:
            unwrapped_children.append(child.unwrap())

        # Calculate how many total cycles we need
        total_cycles = self.get_nested_cycle_count()

        # Expand into a bracket showing all cycles
        expanded = []
        for cycle in range(total_cycles):
            # Pick which element from this angle bracket
            element_index = cycle % len(unwrapped_children)
            child = unwrapped_children[element_index]

            # If the child is a bracket with multiple elements (from nested angle expansion),
            # we need to pick the right subset for this cycle
            if isinstance(child, BracketExpression) and isinstance(child.value, list):
                # Calculate which "sub-cycle" we're in for this child
                cycles_per_element = total_cycles // len(unwrapped_children)
                sub_cycle = (cycle // len(unwrapped_children)) % cycles_per_element

                # If the child was expanded from angles, it has cycles_per_element sets of elements
                elements_per_cycle = len(child.value) // cycles_per_element if cycles_per_element > 0 else len(
                    child.value)
                start_idx = sub_cycle * elements_per_cycle
                end_idx = start_idx + elements_per_cycle

                # Add this subset of elements
                for elem in child.value[start_idx:end_idx]:
                    elem_copy = elem.__class__()
                    elem_copy.value = elem.value
                    elem_copy.duration_modifier = elem.duration_modifier
                    expanded.append(elem_copy)
            else:
                # Simple element, just copy it
                child_copy = child.__class__()
                child_copy.value = child.value
                child_copy.duration_modifier = child.duration_modifier if hasattr(child, 'duration_modifier') else 1.0
                expanded.append(child_copy)

        # Return as a bracket
        result = BracketExpression()
        result.value = expanded
        result.duration_modifier = self.duration_modifier
        return result


class BracketExpression(Expression):
    """
    Square brackets create sequential patterns.
    [a b c] means play a, then b, then c in sequence.
    """
    start_char = "["
    end_char = "]"

    def get_nested_cycle_count(self):
        """
        Calculate how many cycles are needed due to nested angles.
        """
        if isinstance(self.value, str):
            return 1

        max_cycles = 1
        for child in self.value:
            if isinstance(child, AngleExpression):
                child_cycles = child.get_nested_cycle_count()
                max_cycles = max(max_cycles, child_cycles)
            elif isinstance(child, BracketExpression):
                child_cycles = child.get_nested_cycle_count()
                max_cycles = max(max_cycles, child_cycles)

        return max_cycles

    def unwrap(self):
        """
        Brackets preserve structure but expand their children.
        Special handling for angle bracket children - they expand the sequence.
        """
        if isinstance(self.value, str):
            result = BracketExpression()
            result.value = self.value
            result.duration_modifier = self.duration_modifier
            return result

        # Check if any children are AngleExpressions
        has_angle = any(isinstance(child, AngleExpression) for child in self.value)

        if has_angle:
            # Need to expand for each alternation cycle
            # Find the maximum number of alternations
            max_alternations = 1
            for child in self.value:
                if isinstance(child, AngleExpression) and isinstance(child.value, list):
                    max_alternations = max(max_alternations, len(child.value))

            # Calculate durations within the original bracket (WITHOUT dividing by cycles)
            total_duration = sum(child.duration_modifier for child in self.value)

            # Expand the bracket pattern for each cycle
            expanded = []
            for cycle in range(max_alternations):
                for child in self.value:
                    if isinstance(child, AngleExpression) and isinstance(child.value, list):
                        # Pick the element from this cycle
                        alternation_child = child.value[cycle % len(child.value)]
                        expanded_child = alternation_child.unwrap()
                        # Keep the original proportion (DON'T divide by max_alternations)
                        proportion = child.duration_modifier / total_duration
                        expanded_child.duration_modifier = proportion
                        expanded.append(expanded_child)
                    else:
                        expanded_child = child.unwrap()
                        # Keep the original proportion (DON'T divide by max_alternations)
                        proportion = child.duration_modifier / total_duration
                        expanded_child.duration_modifier = proportion
                        expanded.append(expanded_child)

            result = BracketExpression()
            result.value = expanded
            result.duration_modifier = self.duration_modifier
            return result
        else:
            # No angle brackets, just unwrap children and calculate proportions
            unwrapped_children = []
            total_duration = sum(child.duration_modifier for child in self.value)

            for child in self.value:
                unwrapped_child = child.unwrap()
                # Set duration as proportion of the bracket
                unwrapped_child.duration_modifier = child.duration_modifier / total_duration
                unwrapped_children.append(unwrapped_child)

            result = BracketExpression()
            result.value = unwrapped_children
            result.duration_modifier = self.duration_modifier
            return result


class MultiplierExpression(Expression):
    """
    Multiplier repeats/speeds up a pattern.
    [a b]*2 means repeat [a b] twice, fitting both repetitions in one cycle.
    """
    start_char = "*"
    end_char = ""

    def __init__(self):
        super().__init__()
        self.multiplier = 1
        self.pattern = None  # The pattern to multiply

    def unwrap(self):
        """
        Unwrap by repeating the pattern n times.
        """
        if self.pattern is None:
            return self

        # Unwrap the pattern first
        unwrapped_pattern = self.pattern.unwrap()

        # If pattern is a bracket, expand it by repetition
        if isinstance(unwrapped_pattern, BracketExpression):
            repeated_children = []
            for _ in range(self.multiplier):
                if isinstance(unwrapped_pattern.value, list):
                    # Create copies of each child to avoid reference issues
                    for child in unwrapped_pattern.value:
                        child_copy = child.__class__()
                        child_copy.value = child.value
                        child_copy.duration_modifier = child.duration_modifier
                        repeated_children.append(child_copy)
                else:
                    repeated_children.append(unwrapped_pattern.value)

            # Renormalize durations: the children's durations should sum to 1.0 within the new bracket
            # After repetition, we have multiplier times as many elements
            # Each element's duration should be divided by multiplier to maintain proportions
            total_duration = sum(child.duration_modifier for child in repeated_children)
            for child in repeated_children:
                child.duration_modifier = child.duration_modifier / total_duration

            result = BracketExpression()
            result.value = repeated_children
            result.duration_modifier = self.duration_modifier
            return result

        # For other pattern types, just return the unwrapped pattern
        return unwrapped_pattern

    def __str__(self):
        if self.pattern:
            return f"{self.pattern}*{self.multiplier}"
        return f"*{self.multiplier}"

