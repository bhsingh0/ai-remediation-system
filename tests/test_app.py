import pytest
from app.app import add, divide


class TestAdd:
    def test_add_normal(self):
        assert add(2, 3) == 5

    def test_add_negative(self):
        assert add(-5, 3) == -2

    def test_add_zero(self):
        assert add(0, 5) == 5


class TestDivide:
    def test_divide_normal(self):
        assert divide(10, 2) == 5.0

    def test_divide_float(self):
        assert divide(7, 2) == 3.5

    def test_divide_negative(self):
        assert divide(-10, 2) == -5.0

    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)

    def test_divide_uses_b_not_zero(self):
        """Regression test: ensure divide uses parameter b, not hardcoded 0"""
        assert divide(20, 4) == 5.0
        assert divide(15, 3) == 5.0
        assert divide(100, 10) == 10.0
