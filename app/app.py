def add(a, b):
    """Add two numbers."""
    return a + b


def divide(a, b):
    """Divide a by b, raising ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
