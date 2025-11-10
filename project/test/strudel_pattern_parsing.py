from expression import BracketExpression, Expression, AngleExpression, MultiplierExpression
from parser import parse_pattern


def test_pattern(pattern_str):
    """Test a pattern by parsing and unwrapping it."""
    print(f"Pattern: {pattern_str}")
    parsed = parse_pattern(pattern_str)
    print(f"Parsed: {parsed}")

    unwrapped = parsed.unwrap()
    print(f"Unwrapped: {unwrapped}")

    elements = unwrapped.flatten_to_elements()
    print(f"Elements: {' '.join([f'{v}@{d}' for v, d in elements])}")
    print()


# Example usage and testing
if __name__ == "__main__":
    print("=== Automated Tests ===\n")

    # Test 1: [0 1]*2
    test_pattern("[0 1]*2")

    # Test 2: [0 <2 3>@2]*2
    test_pattern("[0 <2 3>@2]*2")

    # Test 3: Simple bracket
    test_pattern("[a b c]")

    # Test 4: Angle bracket
    test_pattern("<x y z>")

    # Test 5: Complex nested pattern
    test_pattern("[0 [1 2]*2 3]")

    print("\n=== Interactive Mode ===")
    print("Enter Strudel patterns to unwrap them (or 'quit' to exit)")
    print("Examples: [0 1]*2, [0 <2 3>@2]*2, <a b c>@3\n")

    while True:
        try:
            user_input = input("Pattern: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            test_pattern(user_input)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.\n")
    # Example 1: [0 1]*2
    print("Example 1: [0 1]*2")
    bracket = BracketExpression()
    elem0 = Expression()
    elem0.value = "0"
    elem1 = Expression()
    elem1.value = "1"
    bracket.value = [elem0, elem1]

    mult = MultiplierExpression()
    mult.pattern = bracket
    mult.multiplier = 2

    unwrapped = mult.unwrap()
    print(f"Unwrapped: {unwrapped}")

    # Show durations
    elements = unwrapped.flatten_to_elements()
    print(f"Elements: {' '.join([f'{v}@{d:.1f}' for v, d in elements])}")
    print()

    # Example 2: [0 <2 3>@2]*2
    print("Example 2: [0 <2 3>@2]*2")
    bracket2 = BracketExpression()
    elem0_2 = Expression()
    elem0_2.value = "0"

    angle = AngleExpression()
    elem2 = Expression()
    elem2.value = "2"
    elem3 = Expression()
    elem3.value = "3"
    angle.value = [elem2, elem3]
    angle.duration_modifier = 2.0

    bracket2.value = [elem0_2, angle]

    # First unwrap the bracket (expands angle)
    unwrapped_bracket = bracket2.unwrap()
    print(f"After expanding angles: {unwrapped_bracket}")

    mult2 = MultiplierExpression()
    mult2.pattern = unwrapped_bracket
    mult2.multiplier = 2

    final = mult2.unwrap()
    print(f"Final unwrapped: {final}")

    # Calculate normalized durations
    print(f"With durations: {' '.join([f'{v}@{d:.5f}' for v, d in final.flatten_to_elements()])}")