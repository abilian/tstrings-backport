import sys

import pytest

from tstrings import Interpolation, t


def test_simple_string():
    """Tests a string with no interpolations."""
    template = t("Hello, world!")
    assert template.strings == ("Hello, world!",)
    assert template.interpolations == ()
    assert template.values == ()
    assert tuple(template) == ("Hello, world!",)


def test_empty_string():
    """Tests an empty string."""
    template = t("")
    assert template.strings == ("",)
    assert template.interpolations == ()
    assert template.values == ()
    assert tuple(template) == ()


def test_simple_interpolation():
    """Tests a basic variable interpolation."""
    name = "World"
    assert name
    template = t("Hello, {name}!")
    assert template.strings == ("Hello, ", "!")
    assert len(template.interpolations) == 1
    interp = template.interpolations[0]
    assert interp.value == "World"
    assert interp.expression == "name"
    assert interp.conversion is None
    assert interp.format_spec == ""
    assert template.values == ("World",)
    assert tuple(template) == ("Hello, ", interp, "!")


def test_leading_and_trailing_interpolations():
    """Tests interpolations at the start and end of the string."""
    a, b = 1, 2
    assert a and b
    template_leading = t("{a} is first")
    assert template_leading.strings == ("", " is first")
    assert tuple(template_leading) == (template_leading.interpolations[0], " is first")

    template_trailing = t("last is {b}")
    assert template_trailing.strings == ("last is ", "")
    assert tuple(template_trailing) == ("last is ", template_trailing.interpolations[0])


def test_adjacent_interpolations():
    """Tests two interpolations with no text between them."""
    first, second = "one", "two"
    assert first and second
    template = t("{first}{second}")
    assert template.strings == ("", "", "")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == "one"
    assert template.interpolations[1].value == "two"
    assert template.values == ("one", "two")
    assert tuple(template) == template.interpolations


def test_conversion_specifiers():
    """Tests !r, !s, and !a conversions."""
    value = "Test"
    assert value
    template_r = t("{value!r}")
    assert template_r.interpolations[0].conversion == "r"
    template_s = t("{value!s}")
    assert template_s.interpolations[0].conversion == "s"
    template_a = t("{value!a}")
    assert template_a.interpolations[0].conversion == "a"


def test_format_specifier():
    """Tests a format specification."""
    num = 123.456
    assert num
    template = t("{num:.2f}")
    interp = template.interpolations[0]
    assert interp.value == 123.456
    assert interp.format_spec == ".2f"
    assert interp.conversion is None


def test_format_then_conversion():
    temp, unit = 22.43, "C"
    assert temp and unit
    template = t("Temperature: {temp:.1f} degrees {unit!s}")
    assert template.strings == ("Temperature: ", " degrees ", "")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == 22.43
    assert template.interpolations[0].expression == "temp"
    assert template.interpolations[0].conversion is None
    assert template.interpolations[0].format_spec == ".1f"
    assert template.interpolations[1].value == "C"
    assert template.interpolations[1].expression == "unit"
    assert template.interpolations[1].conversion == "s"
    assert template.interpolations[1].format_spec == ""


def test_conversion_then_format():
    summary, temp = "hot", 22.43
    assert temp and summary
    template = t("Temperature is {summary!s}, around {temp:.1f} degrees")
    assert template.strings == ("Temperature is ", ", around ", " degrees")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == "hot"
    assert template.interpolations[0].expression == "summary"
    assert template.interpolations[0].conversion == "s"
    assert template.interpolations[0].format_spec == ""
    assert template.interpolations[1].value == 22.43
    assert template.interpolations[1].expression == "temp"
    assert template.interpolations[1].conversion is None
    assert template.interpolations[1].format_spec == ".1f"


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
    assert data
    template = t("""{
        sum(data)
    }""")
    assert template.interpolations[0].value == 6


def test_raw_string():
    trade = "shrubberies"
    assert trade
    template = t(r'Did you say "{trade}"?\n')
    assert template.strings[0] == r'Did you say "'
    assert template.strings[1] == r'"?\n'


def test_debug_specifier_simple():
    """Tests the debug specifier: {var=}."""
    var = 42
    assert var
    template = t("{var=}")
    assert template.strings == ("var=", "")
    assert len(template.interpolations) == 1
    interp = template.interpolations[0]
    assert interp.value == 42
    assert interp.expression == "var"
    assert interp.conversion == "r"  # Should default to !r
    assert interp.format_spec == ""


def test_debug_specifier_with_text_and_whitespace():
    """Tests the debug specifier with surrounding text and whitespace."""
    val = "test"
    assert val
    template = t("The value is {val=}.")
    assert template.strings == ("The value is val=", ".")
    interp = template.interpolations[0]
    assert interp.expression == "val"
    assert interp.conversion == "r"


def test_debug_specifier_with_format():
    """Tests the debug specifier with a format spec: {var=:.2f}."""
    num = 3.14159
    assert num
    template = t("{num=:.2f}")
    assert template.strings == ("num=", "")
    interp = template.interpolations[0]
    assert interp.value == 3.14159
    assert interp.expression == "num"
    assert interp.conversion == "s"  # Should switch to !s
    assert interp.format_spec == ".2f"


def test_debug_with_conversion_is_error():
    """Verifies that {var!r=} raises a SyntaxError."""
    var = 1
    assert var
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


def test_interpolation_repr():
    """Ensures that the repr of an Interpolation instance is as expected."""
    interp = Interpolation("value", "expr", "r", ".2f")
    assert (
        repr(interp)
        == "Interpolation(value='value', expression='expr', conversion='r', format_spec='.2f')"  # noqa: E501
    )


def test_template_repr():
    """Ensures that the repr of a Template instance is as expected."""
    name = "world"
    assert name
    template = t("Hello, {name}!")
    assert (
        repr(template)
        == "Template(strings=('Hello, ', '!'), interpolations=(Interpolation(value='world', expression='name', conversion=None, format_spec=''),))"  # noqa: E501
    )


def test_err_on_str():
    """Ensures that converting a Template instance to a string raises TypeError."""
    template = t("Hello!")
    with pytest.raises(TypeError):
        str(template)


def test_interpolation_equality():
    i1 = Interpolation("value", "expr")
    i2 = Interpolation("value", "expr")
    assert i1 == i1
    assert i1 != i2
    assert i1 != 5


def test_template_equality():
    name = "world"
    assert name
    t1 = t("Hello, {name}!")
    t2 = t("Hello, {name}!")
    assert t1 == t1
    assert t1 != t2
    assert t1 != 5


def test_interpolation_ordering_errors():
    i1 = Interpolation("value", "expr")
    i2 = Interpolation("value", "expr")
    with pytest.raises(TypeError):
        i1 < i2
    with pytest.raises(TypeError):
        i1 <= i2
    with pytest.raises(TypeError):
        i1 > i2
    with pytest.raises(TypeError):
        i1 >= i2
    with pytest.raises(TypeError):
        i1 < 5


def test_template_ordering_errors():
    t1 = t("value")
    t2 = t("value")
    with pytest.raises(TypeError):
        t1 < t2
    with pytest.raises(TypeError):
        t1 <= t2
    with pytest.raises(TypeError):
        t1 > t2
    with pytest.raises(TypeError):
        t1 >= t2
    with pytest.raises(TypeError):
        t1 < 5


def test_add():
    a, b = "A", "B"
    assert a and b
    t1 = t("leading {a} trailing")
    t2 = t(" and more {b} end")
    t3 = t1 + t2
    assert t3.strings == ("leading ", " trailing and more ", " end")
    assert t3.interpolations == (t1.interpolations[0], t2.interpolations[0])


def test_add_empty():
    t1 = t("")
    t2 = t("")
    t3 = t1 + t2
    assert t3.strings == ("",)
    assert len(t3.interpolations) == 0


def test_add_not_supported():
    template = t("content")
    with pytest.raises(TypeError):
        template + "not a template"
    with pytest.raises(TypeError):
        template + Interpolation(5, "expr")


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="match statement requires Python 3.10+"
)
def test_interpolation_match():
    name = "world"
    template = t("Hello, {name}")
    assert name and template
    match_code = """
for part in template:
    match part:
        case Interpolation(value, expression, conversion, format_spec):
            assert value == "world"
            assert expression == "name"
            assert conversion is None
            assert format_spec == ""
        case str(s):
            assert s == "Hello, "
        case _:
            assert False
"""
    exec(match_code, globals(), locals())
