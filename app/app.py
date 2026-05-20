def add(a, b):
    """Add two numbers and return the result."""
    return a + b


def divide(a, b):
    """Divide a by b and return the result.
    
    Raises ValueError if b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
