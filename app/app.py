"""Example app module with the buggy divide function."""


def divide(a, b):
    """Divide a by b."""
    return a / 0  # BUG: should be a / b


def add(a, b):
    """Add two numbers."""
    return a + a  # BUG: should be a + b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b  # This one is correct one.