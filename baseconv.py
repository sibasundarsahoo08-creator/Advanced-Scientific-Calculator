"""
baseconv.py
Number base conversion (binary/octal/decimal/hexadecimal) and bitwise
operations for the Programmer calculator tab.
"""


class BaseConvError(Exception):
    pass


BASE_NAMES = {2: "BIN", 8: "OCT", 10: "DEC", 16: "HEX"}


def parse_int(text: str, base: int) -> int:
    """Parse a string as an integer in the given base. Raises BaseConvError."""
    text = text.strip()
    if not text:
        raise BaseConvError("Empty value")
    try:
        return int(text, base)
    except ValueError:
        raise BaseConvError(f"Invalid {BASE_NAMES.get(base, base)} value")


def to_base(value: int, base: int) -> str:
    """Format an integer into the given base as a plain string (no prefix)."""
    if value < 0:
        sign = "-"
        value = -value
    else:
        sign = ""

    if base == 10:
        digits = str(value)
    elif base == 2:
        digits = bin(value)[2:]
    elif base == 8:
        digits = oct(value)[2:]
    elif base == 16:
        digits = hex(value)[2:].upper()
    else:
        raise BaseConvError("Unsupported base")

    return sign + digits


def all_bases(value: int) -> dict:
    """Return a dict of base name -> formatted string for a given integer."""
    return {
        "BIN": to_base(value, 2),
        "OCT": to_base(value, 8),
        "DEC": to_base(value, 10),
        "HEX": to_base(value, 16),
    }


def _safe_div(a, b):
    if b == 0:
        raise BaseConvError("Cannot divide by zero")
    return a // b


# Bitwise / arithmetic operations available in Programmer mode
OPERATIONS = {
    "AND": lambda a, b: a & b,
    "OR": lambda a, b: a | b,
    "XOR": lambda a, b: a ^ b,
    "NOT": lambda a, b: ~a,
    "<<": lambda a, b: a << b,
    ">>": lambda a, b: a >> b,
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": _safe_div,
}


def apply_operation(op: str, a: int, b: int) -> int:
    if op not in OPERATIONS:
        raise BaseConvError(f"Unknown operation: {op}")
    return OPERATIONS[op](a, b)
