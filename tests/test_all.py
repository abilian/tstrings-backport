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
        template = t("Hello, {name}!")
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
        template_leading = t("{a} is first")
        self.assertEqual(template_leading.strings, ("", " is first"))

        template_trailing = t("last is {b}")
        self.assertEqual(template_trailing.strings, ("last is ", ""))

    def test_adjacent_interpolations(self):
        """Tests two interpolations with no text between them."""
        first, second = "one", "two"
        template = t("{first}{second}")
        self.assertEqual(template.strings, ("", "", ""))
        self.assertEqual(len(template.interpolations), 2)
        self.assertEqual(template.interpolations[0].value, "one")
        self.assertEqual(template.interpolations[1].value, "two")

    def test_conversion_specifiers(self):
        """Tests !r, !s, and !a conversions."""
        value = "Test"
        template_r = t("{value!r}")
        self.assertEqual(template_r.interpolations[0].conversion, 'r')
        template_s = t("{value!s}")
        self.assertEqual(template_s.interpolations[0].conversion, 's')
        template_a = t("{value!a}")
        self.assertEqual(template_a.interpolations[0].conversion, 'a')

    def test_format_specifier(self):
        """Tests a format specification."""
        num = 123.456
        template = t("{num:.2f}")
        interp = template.interpolations[0]
        self.assertEqual(interp.value, 123.456)
        self.assertEqual(interp.format_spec, ".2f")
        self.assertIsNone(interp.conversion)

    def test_complex_expression(self):
        """Tests an interpolation with a function call."""

        def get_val():
            return "complex"

        template = t("Value is {get_val().upper()}")
        self.assertEqual(template.interpolations[0].value, "COMPLEX")
        self.assertEqual(template.interpolations[0].expression, "get_val().upper()")

    def test_multiline_expression(self):
        """Tests an expression spanning multiple lines."""
        data = [1, 2, 3]
        template = t("""{
            sum(data)
        }""")
        self.assertEqual(template.interpolations[0].value, 6)

    def test_debug_specifier_simple(self):
        """Tests the debug specifier: {var=}."""
        var = 42
        template = t("{var=}")
        self.assertEqual(template.strings, ("var=", ""))
        self.assertEqual(len(template.interpolations), 1)
        interp = template.interpolations[0]
        self.assertEqual(interp.value, 42)
        self.assertEqual(interp.expression, "var")
        self.assertEqual(interp.conversion, 'r')  # Should default to !r
        self.assertEqual(interp.format_spec, "")

    def test_debug_specifier_with_text_and_whitespace(self):
        """Tests the debug specifier with surrounding text and whitespace."""
        val = "test"
        template = t("The value is { val= }.")
        self.assertEqual(template.strings, ("The value is  val= ", "."))
        interp = template.interpolations[0]
        self.assertEqual(interp.expression, " val")
        self.assertEqual(interp.conversion, 'r')

    def test_debug_specifier_with_format(self):
        """Tests the debug specifier with a format spec: {var=:.2f}."""
        num = 3.14159
        template = t("{num=:.2f}")
        self.assertEqual(template.strings, ("num=", ""))
        interp = template.interpolations[0]
        self.assertEqual(interp.value, 3.14159)
        self.assertEqual(interp.expression, "num")
        self.assertEqual(interp.conversion, 's')  # Should switch to !s
        self.assertEqual(interp.format_spec, ".2f")

    def test_debug_with_conversion_is_error(self):
        """Verifies that {var!r=} raises a SyntaxError."""
        var = 1
        with self.assertRaises(SyntaxError):
            t("{var!r=}")

    def test_undefined_variable_raises_error(self):
        """Ensures that an undefined variable in an expression raises NameError."""
        with self.assertRaises(NameError):
            t("This will fail: {undefined_var}")

    def test_syntax_error_in_expression_raises_error(self):
        """Ensures an invalid expression raises SyntaxError."""
        with self.assertRaises(SyntaxError):
            t("This is invalid: {1 +}")


if __name__ == '__main__':
    unittest.main()
