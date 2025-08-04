import pytest
from pep750_backport import t, Template, Interpolation

def test_simple_string():
    template = t("Hello, world!")
    assert template.strings == ("Hello, world!",)
    assert template.interpolations == ()

def test_empty_string():
    template = t("")
    assert template.strings == ("",)
    assert template.interpolations == ()

def test_simple_interpolation():
    name = "World"
    template = t(f"Hello, {name}!")
    assert template.strings == ("Hello, ", "!")
    assert len(template.interpolations) == 1
    interp = template.interpolations[0]
    assert interp.value == "World"
    assert interp.expression == "name"
    assert interp.conversion is None
    assert interp.format_spec == ""

def test_leading_and_trailing_interpolations():
    a, b = 1, 2
    template_leading = t(f"{a} is first")
    assert template_leading.strings == ("", " is first")

    template_trailing = t(f"last is {b}")
    assert template_trailing.strings == ("last is ", "")

def test_adjacent_interpolations():
    first, second = "one", "two"
    template = t(f"{first}{second}")
    assert template.strings == ("", "", "")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == "one"
    assert template.interpolations[1].value == "two"

def test_conversion_specifiers():
    value = "Test"

    template_r = t(f"{value!r}")
    assert template_r.interpolations[0].conversion == 'r'

    template_s = t(f"{value!s}")
    assert template_s.interpolations[0].conversion == 's'

    template_a = t(f"{value!a}")
    assert template_a.interpolations[0].conversion == 'a'

def test_format_specifier():
    num = 123.456
    template = t(f"{num:.2f}")
    interp = template.interpolations[0]
    assert interp.value == 123.456
    assert interp.format_spec == ".2f"
    assert interp.conversion is None

def test_conversion_and_format_spec():
    num = 123.456
    template = t(f"{num!r:.2f}")
    interp = template.interpolations[0]
    assert interp.conversion == 'r'
    assert interp.format_spec == ".2f"

def test_complex_expression():
    def get_val():
        return "complex"
    template = t(f"Value is {get_val().upper()}")
    assert template.interpolations[0].value == "COMPLEX"
    assert template.interpolations[0].expression == "get_val().upper()"

def test_debug_specifier_simple():
    var = 42
    template = t(f"{var=}")
    assert template.strings == ("var=",)
    assert len(template.interpolations) == 1
    interp = template.interpolations[0]
    assert interp.value == 42
    assert interp.expression == "var"
    assert interp.conversion == 'r'
    assert interp.format_spec == ""

def test_debug_specifier_with_text_and_whitespace():
    val = "test"
    template = t(f"The value is { val= }.")
    assert template.strings == ("The value is  val= .",)
    interp = template.interpolations[0]
    assert interp.expression == " val"
    assert interp.conversion == 'r'

def test_debug_specifier_with_format():
    num = 3.14159
    template = t(f"{num=:.2f}")
    assert template.strings == ("num=",)
    interp = template.interpolations[0]
    assert interp.value == 3.14159
    assert interp.expression == "num"
    assert interp.conversion == 's'
    assert interp.format_spec == ".2f"

# def test_debug_with_conversion_is_error():
#     var = 1
#     with pytest.raises(SyntaxError):
#         t(f"{var!r =}")
