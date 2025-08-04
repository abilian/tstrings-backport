import unittest
from pep750_backport import t, Template, Interpolation


class TestTStringEmulator(unittest.TestCase):

    def test_simple_string(self):
        """Tests a string with no interpolations."""
        template = t("Hello, world!")
        self.assertEqual(template.strings, ("Hello, world!",))
        self.assertEqual(template.interpolations, ())

    def test_empty_string(self):
        """Tests an empty string."""
        template = t("")
        self.assertEqual(template.strings, ("",))
        self.assertEqual(template.interpolations, ())

    def test_simple_interpolation(self):
        """Tests a basic variable interpolation."""
        name = "World"
        template = t(f"Hello, {name}!")
        self.assertEqual(template.strings, ("Hello, ", "!"))
        self.assertEqual(len(template.interpolations), 1)
        interp = template.interpolations[0]
        self.assertEqual(interp.value, "World")
        self.assertEqual(interp.expression, "name")
        self.assertIsNone(interp.conversion)
        self.assertEqual(interp.format_spec, "")

    def test_leading_and_trailing_interpolations(self):
        """Tests interpolations at the start and end of the string."""
        a, b = 1, 2
        template_leading = t(f"{a} is first")
        self.assertEqual(template_leading.strings, ("", " is first"))

        template_trailing = t(f"last is {b}")
        self.assertEqual(template_trailing.strings, ("last is ", ""))

    def test_adjacent_interpolations(self):
        """Tests two interpolations with no text between them."""
        first, second = "one", "two"
        template = t(f"{first}{second}")
        self.assertEqual(template.strings, ("", "", ""))
        self.assertEqual(len(template.interpolations), 2)
        self.assertEqual(template.interpolations[0].value, "one")
        self.assertEqual(template.interpolations[1].value, "two")

    def test_conversion_specifiers(self):
        """Tests !r, !s, and !a conversions."""
        value = "Test"

        # !r for repr()
        template_r = t(f"{value!r}")
        self.assertEqual(template_r.interpolations[0].conversion, 'r')

        # !s for str()
        template_s = t(f"{value!s}")
        self.assertEqual(template_s.interpolations[0].conversion, 's')

        # !a for ascii()
        template_a = t(f"{value!a}")
        self.assertEqual(template_a.interpolations[0].conversion, 'a')

    def test_format_specifier(self):
        """Tests a format specification."""
        num = 123.456
        template = t(f"{num:.2f}")
        interp = template.interpolations[0]
        self.assertEqual(interp.value, 123.456)
        self.assertEqual(interp.format_spec, ".2f")
        self.assertIsNone(interp.conversion)

    def test_conversion_and_format_spec(self):
        """Tests a combined conversion and format spec."""
        num = 123.456
        template = t(f"{num!r:.2f}")
        interp = template.interpolations[0]
        self.assertEqual(interp.conversion, 'r')
        self.assertEqual(interp.format_spec, ".2f")

    def test_complex_expression(self):
        """Tests an interpolation with a function call."""

        def get_val():
            return "complex"

        template = t(f"Value is {get_val().upper()}")
        self.assertEqual(template.interpolations[0].value, "COMPLEX")
        self.assertEqual(template.interpolations[0].expression, "get_val().upper()")

    def test_debug_specifier_simple(self):
        """Tests the debug specifier: {var=}."""
        var = 42
        template = t(f"{var=}")
        self.assertEqual(template.strings, ("var=",))
        self.assertEqual(len(template.interpolations), 1)
        interp = template.interpolations[0]
        self.assertEqual(interp.value, 42)
        self.assertEqual(interp.expression, "var")
        self.assertEqual(interp.conversion, 'r')  # Should default to !r
        self.assertEqual(interp.format_spec, "")

    def test_debug_specifier_with_text_and_whitespace(self):
        """Tests the debug specifier with surrounding text and whitespace."""
        val = "test"
        template = t(f"The value is { val= }.")
        # The whitespace inside the braces is preserved in the expression part
        self.assertEqual(template.strings, ("The value is  val= .",))
        interp = template.interpolations[0]
        self.assertEqual(interp.expression, " val")  # Note the leading space
        self.assertEqual(interp.conversion, 'r')

    def test_debug_specifier_with_format(self):
        """Tests the debug specifier with a format spec: {var=:.2f}."""
        num = 3.14159
        template = t(f"{num=:.2f}")
        self.assertEqual(template.strings, ("num=",))
        interp = template.interpolations[0]
        self.assertEqual(interp.value, 3.14159)
        self.assertEqual(interp.expression, "num")
        self.assertEqual(interp.conversion, 's')  # Should switch to !s
        self.assertEqual(interp.format_spec, ".2f")

    # def test_debug_with_conversion_is_error(self):
    #     """Verifies that {var!r=} raises a SyntaxError."""
    #     var = 1
    #     with self.assertRaises(SyntaxError):
    #         t(f"{var!r =}")

    if __name__ == '__main__':
        unittest.main()
