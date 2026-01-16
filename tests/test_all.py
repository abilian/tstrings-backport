import sys

import pytest

from tstrings import Interpolation, Template, t


def assert_interpolations_equal(actual: Interpolation, expected: Interpolation) -> None:
    """Interpolation.__eq__ uses identity, so this compares content."""
    assert actual.value == expected.value
    assert actual.expression == expected.expression
    assert actual.conversion == expected.conversion
    assert actual.format_spec == expected.format_spec


def assert_templates_equal(actual: Template, expected: Template) -> None:
    """Template.__eq__ uses identity, so this compares content."""
    assert actual.strings == expected.strings
    assert len(actual.interpolations) == len(expected.interpolations)
    for a_interp, e_interp in zip(actual.interpolations, expected.interpolations):
        assert_interpolations_equal(a_interp, e_interp)


def test_simple_string():
    """Tests a string with no interpolations."""
    actual = t("Hello, world!")
    expected = Template(strings=("Hello, world!",), interpolations=())
    assert_templates_equal(actual, expected)


def test_empty_string():
    """Tests an empty string."""
    actual = t("")
    expected = Template(strings=("",), interpolations=())
    assert_templates_equal(actual, expected)


def test_simple_interpolation():
    """Tests a basic variable interpolation."""
    name = "World"
    assert name
    actual = t("Hello, {name}!")
    expected = Template(
        strings=("Hello, ", "!"),
        interpolations=(Interpolation(value="World", expression="name"),),
    )
    assert_templates_equal(actual, expected)


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
    actual = t("{first}{second}")
    expected = Template(
        strings=("", "", ""),
        interpolations=(
            Interpolation(value="one", expression="first"),
            Interpolation(value="two", expression="second"),
        ),
    )
    assert_templates_equal(actual, expected)


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


def test_bogus_conversion():
    """Tests !z errors"""
    value = "Test"
    assert value
    with pytest.raises(SyntaxError) as exc_info:
        t("hello {value!z}")
    expected_msg = (
        "Failed to evaluate expression 'value!z': invalid syntax (<string>, line 1)"
    )
    assert str(exc_info.value) == expected_msg


def test_format_specifier():
    """Tests a format specification."""
    num = 123.456
    assert num
    actual = t("{num:.2f}")
    expected = Template(
        strings=("", ""),
        interpolations=(
            Interpolation(value=123.456, expression="num", format_spec=".2f"),
        ),
    )
    assert_templates_equal(actual, expected)


def test_format_then_conversion():
    temp, unit = 22.43, "C"
    assert temp and unit
    actual = t("Temperature: {temp:.1f} degrees {unit!s}")
    expected = Template(
        strings=("Temperature: ", " degrees ", ""),
        interpolations=(
            Interpolation(value=22.43, expression="temp", format_spec=".1f"),
            Interpolation(value="C", expression="unit", conversion="s"),
        ),
    )
    assert_templates_equal(actual, expected)


def test_conversion_then_format():
    summary, temp = "hot", 22.43
    assert temp and summary
    actual = t("Temperature is {summary!s}, around {temp:.1f} degrees")
    expected = Template(
        strings=("Temperature is ", ", around ", " degrees"),
        interpolations=(
            Interpolation(value="hot", expression="summary", conversion="s"),
            Interpolation(value=22.43, expression="temp", format_spec=".1f"),
        ),
    )
    assert_templates_equal(actual, expected)


def test_complex_expression():
    """Tests an interpolation with a function call."""

    def get_val():
        return "complex"

    actual = t("Value is {get_val().upper()}")
    expected = Template(
        strings=("Value is ", ""),
        interpolations=(
            Interpolation(value="COMPLEX", expression="get_val().upper()"),
        ),
    )
    assert_templates_equal(actual, expected)


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
    actual = t(r'Did you say "{trade}"?\n')
    expected = Template(
        strings=(r'Did you say "', r'"?\n'),
        interpolations=(Interpolation(value="shrubberies", expression="trade"),),
    )
    assert_templates_equal(actual, expected)


def test_debug_specifier_simple():
    """Tests the debug specifier: {var=}."""
    var = 42
    assert var
    actual = t("{var=}")
    expected = Template(
        strings=("var=", ""),
        interpolations=(Interpolation(value=42, expression="var", conversion="r"),),
    )
    assert_templates_equal(actual, expected)


def test_debug_specifier_with_text_and_whitespace():
    """Tests the debug specifier with surrounding text and whitespace."""
    val = "test"
    assert val
    actual = t("The value is {val=}.")
    expected = Template(
        strings=("The value is val=", "."),
        interpolations=(Interpolation(value="test", expression="val", conversion="r"),),
    )
    assert_templates_equal(actual, expected)


def test_debug_specifier_with_format():
    """Tests the debug specifier with a format spec: {var=:.2f}."""
    num = 3.14159
    assert num
    actual = t("{num=:.2f}")
    expected = Template(
        strings=("num=", ""),
        interpolations=(
            Interpolation(
                value=num, expression="num", conversion="s", format_spec=".2f"
            ),
        ),
    )
    assert_templates_equal(actual, expected)


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


def test_interpolation_hash():
    i1 = Interpolation("value", "expr")
    i2 = Interpolation("value", "expr")
    assert hash(i1) == hash(i1)
    assert hash(i1) != hash(i2)


def test_template_hash():
    name = "world"
    assert name
    t1 = t("Hello, {name}!")
    t2 = t("Hello, {name}!")
    assert hash(t1) == hash(t1)
    assert hash(t1) != hash(t2)


def test_interpolation_ordering_errors():
    i1 = Interpolation("value", "expr")
    i2 = Interpolation("value", "expr")
    with pytest.raises(TypeError):
        i1 < i2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        i1 <= i2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        i1 > i2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        i1 >= i2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        i1 < 5  # type: ignore[unsupported-operator]


def test_template_ordering_errors():
    t1 = t("value")
    t2 = t("value")
    with pytest.raises(TypeError):
        t1 < t2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        t1 <= t2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        t1 > t2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        t1 >= t2  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        t1 < 5  # type: ignore[unsupported-operator]


def test_add():
    a, b = "A", "B"
    assert a and b
    t1 = t("leading {a} trailing")
    t2 = t(" and more {b} end")
    actual = t1 + t2
    expected = Template(
        strings=("leading ", " trailing and more ", " end"),
        interpolations=(
            Interpolation(value="A", expression="a"),
            Interpolation(value="B", expression="b"),
        ),
    )
    assert_templates_equal(actual, expected)


def test_add_empty():
    t1 = t("")
    t2 = t("")
    actual = t1 + t2
    expected = Template(strings=("",), interpolations=())
    assert_templates_equal(actual, expected)


def test_add_not_supported():
    template = t("content")
    with pytest.raises(TypeError):
        template + "not a template"  # type: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        template + Interpolation(5, "expr")  # type: ignore[unsupported-operator]


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
