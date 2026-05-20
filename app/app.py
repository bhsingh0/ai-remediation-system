"""Example app module with the buggy divide function."""
 
 
def divide(a, b):
    """Divide a by b."""
    return a / 0  # BUG: should be a / b
 
 
def add(a, b):
    """Add two numbers."""
    return a + b
 