import re
import sys
from dataclasses import dataclass
from typing import Literal, Optional, Tuple

# Regex to find and parse an f-string-like interpolation.
# It captures:
# 1. The main expression.
# 2. An optional debug specifier (=).
# 3. An optional conversion specifier (!r, !s, or !a).
# 4. An optional format specifier (:...).
INTERPOLATION_RE = re.compile(
    r"""
    \{
        # The core expression, non-greedy
        (?P<expression>.+?)
        # Optional debug specifier
        (?P<debug>=)?
        # Optional conversion, one of !r, !s, or !a
        (?P<conversion>![rsa])?
        # Optional format spec, starting with a colon
        (?P<format_spec>:.+)?
    }
    """,
    re.VERBOSE | re.DOTALL,
)


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


def t(template_string: str) -> Template:
    """
    Emulates a PEP 750 t-string literal for Python < 3.14.

    This function parses a string with f-string-like syntax and returns
    a `Template` object, correctly evaluating expressions in the caller's
    scope.

    Args:
        template_string: The string to parse, e.g., "Hello {name!r}".

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
    last_end = 0

    for match in INTERPOLATION_RE.finditer(template_string):
        # Add the static string part before this interpolation
        strings.append(template_string[last_end : match.start()])
        last_end = match.end()

        groups = match.groupdict()
        expression = groups["expression"]

        # The debug specifier is syntactic sugar. It modifies both the
        # preceding string part and the interpolation itself.
        if groups["debug"]:
            # t'{value=}' becomes t'value={value!r}'
            # t'{value=:fmt}' becomes t'value={value!s:fmt}'

            # Find the position of the '=' in the original match string
            # so we can split the expression and the '=' (with whitespace)
            expr_with_possible_ws = groups["expression"]
            # Find the '=' at the end (possibly with whitespace before/after)
            eq_index = expr_with_possible_ws.rfind("=")
            if eq_index != -1:
                expr_for_static = expr_with_possible_ws[: eq_index + 1]
                # Remove trailing whitespace and the '=' for evaluation
                expr_for_eval = expr_with_possible_ws[:eq_index]
                # Strip all whitespace from both ends for evaluation
                expr_for_eval = expr_for_eval.strip()
                # Remove any trailing '=' if present (shouldn't be, but for safety)
                if expr_for_eval.endswith("="):
                    expr_for_eval = expr_for_eval[:-1].rstrip()
            else:
                expr_for_static = expr_with_possible_ws + "="
                expr_for_eval = expr_with_possible_ws.strip()

            # Prepend 'expression=' (with whitespace) to the *current* static string.
            strings[-1] += expr_for_static

            # For debug specifier, strip trailing '=' and whitespace for evaluation
            # (already done above)

            if groups["conversion"]:
                raise SyntaxError(f"f-string: cannot specify both conversion and '='")

            # If a format spec is present, conversion becomes 's'. Otherwise, 'r'.
            conv_char = "s" if groups["format_spec"] else "r"
            expression_to_eval = expr_for_eval
        else:
            conv_char = groups["conversion"][1] if groups["conversion"] else None
            expression_to_eval = groups["expression"]

        fmt_spec = groups["format_spec"][1:] if groups["format_spec"] else ""

        # Dedent multiline expressions for evaluation
        import textwrap

        expr_eval_str = textwrap.dedent(expression_to_eval)

        # Evaluate the expression to get its value using the caller's context
        try:
            value = eval(expr_eval_str, caller_globals, caller_locals)
        except Exception as e:
            # Re-raise with more context
            msg = f"Failed to evaluate expression '{expression_to_eval}': {e}"
            raise type(e)(msg) from e

        interpolations.append(
            Interpolation(
                value=value,
                expression=expression_to_eval,
                conversion=conv_char,
                format_spec=fmt_spec,
            )
        )

    # Add the final static string part after the last interpolation
    strings.append(template_string[last_end:])

    return Template(strings=tuple(strings), interpolations=tuple(interpolations))
