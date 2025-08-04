import pytest

from pep750_backport import t


def test_simple_string():
    """Tests a string with no interpolations."""
    template = t("Hello, world!")
    assert template.strings == ("Hello, world!",)
    assert template.interpolations == ()


def test_empty_string():
    """Tests an empty string."""
    template = t("")
    assert template.strings == ("",)
    assert template.interpolations == ()


def test_simple_interpolation():
    """Tests a basic variable interpolation."""
    name = "World"
    template = t("Hello, {name}!")
    assert template.strings == ("Hello, ", "!")
    assert len(template.interpolations) == 1
    interp = template.interpolations[0]
    assert interp.value == "World"
    assert interp.expression == "name"
    assert interp.conversion is None
    assert interp.format_spec == ""


def test_leading_and_trailing_interpolations():
    """Tests interpolations at the start and end of the string."""
    a, b = 1, 2
    template_leading = t("{a} is first")
    assert template_leading.strings == ("", " is first")

    template_trailing = t("last is {b}")
    assert template_trailing.strings == ("last is ", "")


def test_adjacent_interpolations():
    """Tests two interpolations with no text between them."""
    first, second = "one", "two"
    template = t("{first}{second}")
    assert template.strings == ("", "", "")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == "one"
    assert template.interpolations[1].value == "two"


def test_conversion_specifiers():
    """Tests !r, !s, and !a conversions."""
    value = "Test"
    template_r = t("{value!r}")
    assert template_r.interpolations[0].conversion == 'r'
    template_s = t("{value!s}")
    assert template_s.interpolations[0].conversion == 's'
    template_a = t("{value!a}")
    assert template_a.interpolations[0].conversion == 'a'


def test_format_specifier():
    """Tests a format specification."""
    num = 123.456
    template = t("{num:.2f}")
    interp = template.interpolations[0]
    assert interp.value == 123.456
    assert interp.format_spec == ".2f"
    assert interp.conversion is None


def test_complex_expression():
    """Tests an interpolation with a function call."""

    def get_val():
        return "complex"

    template = t("Value is {get_val().upper()}")
    assert template.interpolations[0].value == "COMPLEX"
    assert template.interpolations[0].expression == "get_val().upper()"


def test_multiline_expression():
    """Tests an expression spanning multiple lines."""
    data = [1, 2, 3]
    template = t("""{
        sum(data)
    }""")
    assert template.interpolations[0].value == 6


def test_debug_specifier_simple():
    """Tests the debug specifier: {var=}."""
    var = 42
    template = t("{var=}")
    assert template.strings == ("var=", "")
    assert len(template.interpolations) == 1
    interp = template.interpolations[0]
    assert interp.value == 42
    assert interp.expression == "var"
    assert interp.conversion == 'r'  # Should default to !r
    assert interp.format_spec == ""


def test_debug_specifier_with_text_and_whitespace():
    """Tests the debug specifier with surrounding text and whitespace."""
    val = "test"
    template = t("The value is {val=}.")
    assert template.strings == ("The value is val=", ".")
    interp = template.interpolations[0]
    assert interp.expression == "val"
    assert interp.conversion == 'r'


def test_debug_specifier_with_format():
    """Tests the debug specifier with a format spec: {var=:.2f}."""
    num = 3.14159
    template = t("{num=:.2f}")
    assert template.strings == ("num=", "")
    interp = template.interpolations[0]
    assert interp.value == 3.14159
    assert interp.expression == "num"
    assert interp.conversion == 's'  # Should switch to !s
    assert interp.format_spec == ".2f"


def test_debug_with_conversion_is_error():
    """Verifies that {var!r=} raises a SyntaxError."""
    var = 1
    with pytest.raises(SyntaxError):
        t("{var!r=}")


def test_undefined_variable_raises_error():
    """Ensures that an undefined variable in an expression raises NameError."""
    with pytest.raises(NameError):
        t("This will fail: {undefined_var}")


def test_syntax_error_in_expression_raises_error():
    """Ensures an invalid expression raises SyntaxError."""
    with pytest.raises(SyntaxError):
        t("This is invalid: {1 +}")
