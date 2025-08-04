# tstrings: PEP 750-style Template Strings for Python < 3.14

This package provides a backport of the new [PEP 750](https://peps.python.org/pep-0750/) "t-string" template string syntax, for use with Python versions **before 3.14**.

## Usage

Instead of the new syntax `t"..."` (which is only available in Python 3.14+), use the function call form:

```python
from tstrings import t

name = "World"
tpl = t("Hello, {name}!")
print(tpl.strings)         # ("Hello, ", "!")
print(tpl.interpolations)  # (Interpolation(value="World", expression="name", ...),)
```

The returned object is a `Template` with `.strings` and `.interpolations` attributes, closely matching the PEP 750 API.

## Features

- **String interpolation**: Supports `{expr}` expressions, including complex expressions.
- **Debug specifier**: `{var=}` and `{var=:.2f}` forms, as in f-strings.
- **Conversion specifiers**: `{val!r}`, `{val!s}`, `{val!a}`.
- **Format specifiers**: `{num:.2f}`.
- **Multiline expressions**: Supported.
- **Error handling**: Raises `NameError` or `SyntaxError` for invalid expressions, as in f-strings.
- **PEP 750 API**: Returns `Template` and `Interpolation` dataclasses matching the PEP.

## Limitations

- **No t-string literal syntax**: You must use `t("...")`, not `t"..."`.
- **No support for all edge cases**: Some advanced f-string/t-string edge cases may not be fully supported.

## Examples

```python
from tstrings import t

name = ""
value = 1
num = 3.1415
obj = {}
data = [1, 2, 3]

# Simple
tpl = t("Hello, {name}!")
# Debug
tpl = t("{value=}")
# Format
tpl = t("{num:.2f}")
# Conversion
tpl = t("{obj!r}")
# Multiline
tpl = t("""
    {sum(data)}
""")
```

## Development & Testing

Run the test suite with:

```sh
nox
```

See `tests/test_all.py` for coverage of all supported features.

## How to help

This was hacked together in less than 1 hour. If you find it useful, please consider contributing fixes, improvements, or documentation!

Pull requests and issues are welcome.
