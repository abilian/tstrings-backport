import re
import sys
from dataclasses import dataclass
from typing import Literal, Tuple, Sequence, Union, Optional

# Regex to parse an f-string-like interpolation.
# It captures:
# 1. The main expression.
# 2. A debug specifier (=).
# 3. A conversion specifier (!r, !s, or !a).
# 4. A format specifier (:...).
INTERPOLATION_RE = re.compile(r"""
    \{
        (?P<expression>.+?)
        (?P<debug>=)?
        (?P<conversion>![rsa])?
        (?P<format_spec>:.+)?
    \}
""", re.VERBOSE)


@dataclass(frozen=True)
class Interpolation:
    """
    Emulates the string.templatelib.Interpolation class from PEP 750.
    Represents an expression inside a template string.
    """
    value: object
    expression: str
    conversion: Optional[Literal["a", "r", "s"]] = None
    format_spec: str = ""


@dataclass(frozen=True)
class Template:
    """
    Emulates the string.templatelib.Template class from PEP 750.
    Represents a parsed t-string literal.
    """
    strings: Tuple[str, ...]
    interpolations: Tuple[Interpolation, ...]


def t(f_string: str) -> Template:
    """
    Emulates a PEP 750 t-string literal for Python < 3.14.

    This function parses a string with f-string-like syntax and returns
    a `Template` object, correctly evaluating expressions in the caller's
    scope.

    Args:
        f_string: The string to parse, e.g., "Hello {name!r}".

    Returns:
        A `Template` instance containing the parsed static strings and
        evaluated interpolations.
    """
    # Get the execution frame of the caller to evaluate expressions in their scope.
    # sys._getframe(0) is the frame of t()
    # sys._getframe(1) is the frame of the caller of t()
    caller_frame = sys._getframe(1)
    caller_globals = caller_frame.f_globals
    caller_locals = caller_frame.f_locals

    strings = []
    interpolations = []

    # We split the string by our regex. This gives us an alternating list
    # of [static_text, captured_group_1, captured_group_2, ..., static_text, ...].
    # Since our regex matches the *entire* interpolation including braces, the
    # list will be [static, interp, static, interp, ...].
    parts = INTERPOLATION_RE.split(f_string)

    # The first element is always a static string part.
    strings.append(parts[0])

    # The rest of the parts come in groups of 5 from our regex match.
    for i in range(1, len(parts), 5):
        expression = parts[i]
        debug = parts[i + 1]
        conversion_str = parts[i + 2]
        format_spec = parts[i + 3]
        next_static_string = parts[i + 4]

        # Process according to PEP 750 rules
        conv_char = conversion_str[1] if conversion_str else None
        fmt_spec = format_spec[1:] if format_spec else ""

        # The debug specifier is syntactic sugar. It modifies both the
        # preceding string part and the interpolation itself.
        if debug:
            # t'{value=}' becomes t'value={value!r}'
            # t'{value=:fmt}' becomes t'value={value!s:fmt}'

            # Prepend 'expression=' to the *preceding* static string.
            strings[-1] += expression

            if conv_char:
                # PEP 701 specifies this is a syntax error, but we handle it gracefully.
                # A debug specifier cannot be combined with a conversion.
                raise SyntaxError(f"f-string: cannot specify both conversion and '='\n  {f_string}")

            # If a format spec is present, conversion becomes 's'. Otherwise, 'r'.
            conv_char = 's' if fmt_spec else 'r'

        # Evaluate the expression to get its value.
        try:
            value = eval(expression, caller_globals, caller_locals)
        except Exception as e:
            # Re-raise with more context
            raise type(e)(f"Failed to evaluate expression '{expression}': {e}")

        interpolations.append(Interpolation(
            value=value,
            expression=expression,
            conversion=conv_char,
            format_spec=fmt_spec
        ))

        strings.append(next_static_string)

    return Template(
        strings=tuple(strings),
        interpolations=tuple(interpolations)
    )
