"""Luhn algorithm implementation for credit card validation."""


def luhn_validate(number: str) -> bool:
    """Validate a number using Luhn algorithm.

    Args:
        number: String representation of the number to validate.

    Returns:
        True if the number passes Luhn validation, False otherwise.
    """
    if not number.isdigit():
        return False

    if len(number) < 13 or len(number) > 19:
        return False

    digits = [int(d) for d in number]
    checksum = 0

    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        checksum += doubled if doubled < 10 else doubled - 9

    for i in range(len(digits) - 1, -1, -2):
        checksum += digits[i]

    return checksum % 10 == 0
