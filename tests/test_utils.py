import sys
from io import StringIO
from typing import Iterator, List, Tuple

import pytest

from serial_stamp.utils import cartesian_product, replace_vars


class TestIterCartesianProduct:
    """Test suite for iter_cartesian_product function."""

    def test_empty_input(self):
        """Test with no input iterables."""
        result = list(cartesian_product())
        assert result == []

    def test_single_iterable(self):
        """Test with a single iterable."""
        result = list(cartesian_product([1, 2, 3]))
        expected = [(1,), (2,), (3,)]
        assert result == expected

    def test_single_empty_iterable(self):
        """Test with a single empty iterable."""
        result = list(cartesian_product([]))
        assert result == []

    def test_two_iterables(self):
        """Test cartesian product of two iterables."""
        result = list(cartesian_product([1, 2], ["a", "b"]))
        expected = [(1, "a"), (1, "b"), (2, "a"), (2, "b")]
        assert result == expected

    def test_three_iterables(self):
        """Test cartesian product of three iterables."""
        result = list(cartesian_product([1, 2], ["a"], [True, False]))
        expected = [(1, "a", True), (1, "a", False), (2, "a", True), (2, "a", False)]
        assert result == expected

    def test_mixed_types(self):
        """Test with iterables containing different types."""
        result = list(cartesian_product([1, 2], ["x", "y"], [True]))
        expected = [(1, "x", True), (1, "y", True), (2, "x", True), (2, "y", True)]
        assert result == expected

    def test_one_empty_iterable_in_multiple(self):
        """Test when one of multiple iterables is empty."""
        result = list(cartesian_product([1, 2], [], ["a", "b"]))
        assert result == []

    def test_strings_as_iterables(self):
        """Test using strings as iterables."""
        result = list(cartesian_product("ab", "12"))
        expected = [("a", "1"), ("a", "2"), ("b", "1"), ("b", "2")]
        assert result == expected

    def test_ranges(self):
        """Test using range objects."""
        result = list(cartesian_product(range(2), range(1, 3)))
        expected = [(0, 1), (0, 2), (1, 1), (1, 2)]
        assert result == expected

    def test_generators(self):
        """Test with generator expressions using materialize=True."""
        gen1 = (x for x in [1, 2])
        gen2 = (y for y in ["a", "b"])
        result = list(cartesian_product(gen1, gen2, materialize=True))
        expected = [(1, "a"), (1, "b"), (2, "a"), (2, "b")]
        assert result == expected

    def test_generators_without_materialize(self):
        """Test that generators don't work correctly without materialize=True."""
        gen1 = (x for x in [1, 2])
        gen2 = (y for y in ["a", "b"])
        result = list(cartesian_product(gen1, gen2))
        # Without materialize=True, generators get exhausted after first iteration
        # So we only get combinations for the first element of gen1
        expected = [(1, "a"), (1, "b")]
        assert result == expected

    def test_large_product(self):
        """Test with larger iterables."""
        result = list(cartesian_product(range(3), range(3), range(2)))
        expected = [
            (0, 0, 0),
            (0, 0, 1),
            (0, 1, 0),
            (0, 1, 1),
            (0, 2, 0),
            (0, 2, 1),
            (1, 0, 0),
            (1, 0, 1),
            (1, 1, 0),
            (1, 1, 1),
            (1, 2, 0),
            (1, 2, 1),
            (2, 0, 0),
            (2, 0, 1),
            (2, 1, 0),
            (2, 1, 1),
            (2, 2, 0),
            (2, 2, 1),
        ]
        assert result == expected

    def test_ten_iterables(self):
        """Test with maximum overloaded parameters (10 iterables)."""
        iterables = [[i] for i in range(10)]
        result = list(cartesian_product(*iterables))
        expected = [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)]
        assert result == expected

    def test_more_than_ten_iterables(self):
        """Test with more than 10 iterables (falls back to general implementation)."""
        iterables = [[i] for i in range(12)]
        result = list(cartesian_product(*iterables))
        expected = [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)]
        assert result == expected

    def test_is_generator(self):
        """Test that the function returns a generator."""
        result = cartesian_product([1, 2], ["a", "b"])
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_lazy_evaluation(self):
        """Test that the function is lazy (doesn't compute all results immediately)."""

        def counting_generator():
            count = 0
            while count < 3:
                yield count
                count += 1

        result = cartesian_product(counting_generator(), [1, 2])
        # Getting the first item shouldn't consume the entire generator
        first = next(result)
        assert first == (0, 1)

        # We should be able to get more items
        second = next(result)
        assert second == (0, 2)

        third = next(result)
        assert third == (1, 1)

    def test_nested_lists(self):
        """Test with nested data structures."""
        result = list(cartesian_product([[1, 2], [3, 4]], ["a", "b"]))
        expected = [([1, 2], "a"), ([1, 2], "b"), ([3, 4], "a"), ([3, 4], "b")]
        assert result == expected

    def test_tuple_elements(self):
        """Test with tuples as elements."""
        result = list(cartesian_product([(1, 2), (3, 4)], ["x", "y"]))
        expected = [((1, 2), "x"), ((1, 2), "y"), ((3, 4), "x"), ((3, 4), "y")]
        assert result == expected

    def test_single_element_iterables(self):
        """Test with single-element iterables."""
        result = list(cartesian_product([1], [2], [3], [4], [5]))
        expected = [(1, 2, 3, 4, 5)]
        assert result == expected

    def test_comparison_with_itertools(self):
        """Test that results match itertools.product."""
        import itertools

        test_cases = [
            ([1, 2], ["a", "b"]),
            ([1, 2, 3], ["x"], [True, False]),
            (range(2), range(3)),
            ("ab", "12", "!@"),
        ]

        for case in test_cases:
            our_result = list(cartesian_product(*case))
            itertools_result = list(itertools.product(*case))
            assert our_result == itertools_result, f"Mismatch for case {case}"

    def test_memory_efficiency(self):
        """Test that large products don't consume excessive memory immediately."""
        # This test ensures the function is truly lazy
        large_iter = cartesian_product(range(1000), range(1000))

        # Should be able to create without memory issues
        first_few = []
        for i, item in enumerate(large_iter):
            first_few.append(item)
            if i >= 4:  # Just get first 5 items
                break

        expected_start = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
        assert first_few == expected_start

    def test_type_preservation(self):
        """Test that element types are preserved in output."""
        ints = [1, 2]
        strs = ["a", "b"]
        bools = [True, False]

        result = list(cartesian_product(ints, strs, bools))

        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3
            assert isinstance(item[0], int)
            assert isinstance(item[1], str)
            assert isinstance(item[2], bool)

    def test_edge_case_very_small_inputs(self):
        """Test edge cases with very small inputs."""
        # Single element in each iterable
        result = list(cartesian_product([42]))
        assert result == [(42,)]

        # Two single elements
        result = list(cartesian_product([1], [2]))
        assert result == [(1, 2)]

    def test_reproducibility(self):
        """Test that calling the function multiple times gives the same results."""
        args = ([1, 2, 3], ["a", "b"], [True, False])

        result1 = list(cartesian_product(*args))
        result2 = list(cartesian_product(*args))

        assert result1 == result2
        assert len(result1) == 3 * 2 * 2  # 12 combinations


class TestReplaceVars:
    """Test suite for replace_vars function."""

    def test_basic_variable_replacement(self):
        """Test basic variable replacement."""
        template = "Hello $name!"
        vars_dict = {"name": "World"}
        result = replace_vars(template, vars_dict)
        assert result == "Hello World!"

    def test_multiple_variables(self):
        """Test replacing multiple variables."""
        template = "Hello $name, you have $count items and $status."
        vars_dict = {"name": "John", "count": "5", "status": "active"}
        result = replace_vars(template, vars_dict)
        assert result == "Hello John, you have 5 items and active."

    def test_same_variable_multiple_times(self):
        """Test using the same variable multiple times."""
        template = "$name likes $name's job at $company."
        vars_dict = {"name": "Alice", "company": "TechCorp"}
        result = replace_vars(template, vars_dict)
        assert result == "Alice likes Alice's job at TechCorp."

    def test_dollar_escaping(self):
        """Test escaping dollar signs with $$."""
        template = "Price: $$50 for $item"
        vars_dict = {"item": "book"}
        result = replace_vars(template, vars_dict)
        assert result == "Price: $50 for book"

    def test_multiple_dollar_escaping(self):
        """Test multiple dollar sign escapes."""
        template = "$$var costs $$100 and $name paid $$50"
        vars_dict = {"name": "Bob"}
        result = replace_vars(template, vars_dict)
        assert result == "$var costs $100 and Bob paid $50"

    def test_empty_template(self):
        """Test with empty template."""
        template = ""
        vars_dict = {"name": "test"}
        result = replace_vars(template, vars_dict)
        assert result == ""

    def test_empty_vars_dict(self):
        """Test with empty variables dictionary."""
        template = "No variables here"
        vars_dict = {}
        result = replace_vars(template, vars_dict)
        assert result == "No variables here"

    def test_no_variables_in_template(self):
        """Test template with no $ signs."""
        template = "This is just plain text"
        vars_dict = {"name": "test"}
        result = replace_vars(template, vars_dict)
        assert result == "This is just plain text"

    def test_unknown_variable(self):
        """Test handling of unknown variables."""
        template = "Hello $unknown_var!"
        vars_dict = {"name": "World"}

        # Capture stdout to check warning message
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            result = replace_vars(template, vars_dict)
            output = captured_output.getvalue()

            # Should warn about unknown variable
            assert "[warn] Unknown variable at $unknown_var!" in output
            # Should leave the $ in place
            assert result == "Hello $unknown_var!"
        finally:
            sys.stdout = old_stdout

    def test_mixed_known_and_unknown_variables(self):
        """Test mix of known and unknown variables."""
        template = "$name has $unknown items"
        vars_dict = {"name": "Alice"}

        # Capture stdout to check warning
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            result = replace_vars(template, vars_dict)
            output = captured_output.getvalue()

            assert "[warn] Unknown variable at $unknown items" in output
            assert result == "Alice has $unknown items"
        finally:
            sys.stdout = old_stdout

    def test_dollar_at_end(self):
        """Test dollar sign at the end of template."""
        template = "End with $"
        vars_dict = {"name": "test"}

        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            result = replace_vars(template, vars_dict)
            output = captured_output.getvalue()

            assert "[warn] Unknown variable at $" in output
            assert result == "End with $"
        finally:
            sys.stdout = old_stdout

    def test_consecutive_dollars(self):
        """Test consecutive dollar signs."""
        template = "$$$name"
        vars_dict = {"name": "test"}
        result = replace_vars(template, vars_dict)
        assert result == "$test"

    def test_variable_names_with_special_chars(self):
        """Test variable names that might contain special characters."""
        template = "$var1 and $var_2 and $var-3"
        vars_dict = {"var1": "one", "var_2": "two", "var-3": "three"}
        result = replace_vars(template, vars_dict)
        assert result == "one and two and three"

    def test_longest_match_priority(self):
        """Test that longer variable names take priority."""
        template = "$var and $variable"
        vars_dict = {"var": "short", "variable": "long"}
        result = replace_vars(template, vars_dict)
        assert result == "short and long"

        # Test the reverse order to ensure longest match
        template2 = "$variable and $var"
        result2 = replace_vars(template2, vars_dict)
        assert result2 == "long and short"

    def test_overlapping_variable_names(self):
        """Test variables where one name is a prefix of another."""
        template = "$name and $namespace"
        vars_dict = {"name": "John", "namespace": "app"}
        result = replace_vars(template, vars_dict)
        assert result == "John and app"

    def test_empty_variable_value(self):
        """Test variable with empty string value."""
        template = "Before$emptyAfter"
        vars_dict = {"empty": ""}
        result = replace_vars(template, vars_dict)
        assert result == "BeforeAfter"

    def test_variable_with_spaces_in_value(self):
        """Test variable values containing spaces."""
        template = "Message: $message"
        vars_dict = {"message": "Hello World with spaces"}
        result = replace_vars(template, vars_dict)
        assert result == "Message: Hello World with spaces"

    def test_numeric_variable_values(self):
        """Test that numeric values are handled correctly."""
        template = "$count items cost $price each"
        vars_dict = {"count": "42", "price": "19.99"}
        result = replace_vars(template, vars_dict)
        assert result == "42 items cost 19.99 each"

    def test_complex_real_world_example(self):
        """Test a complex real-world-like template."""
        template = "Dear $customer_name,\n\nYour order #$order_id for $$$total_amount has been $status.\n\nThank you,\n$company_name"
        vars_dict = {
            "customer_name": "Jane Doe",
            "order_id": "12345",
            "total_amount": "99.99",
            "status": "shipped",
            "company_name": "ACME Corp",
        }
        expected = "Dear Jane Doe,\n\nYour order #12345 for $99.99 has been shipped.\n\nThank you,\nACME Corp"
        result = replace_vars(template, vars_dict)
        assert result == expected

    def test_preserves_newlines_and_whitespace(self):
        """Test that whitespace and newlines are preserved."""
        template = "  $name  \n  $value  \t"
        vars_dict = {"name": "test", "value": "123"}
        result = replace_vars(template, vars_dict)
        assert result == "  test  \n  123  \t"
