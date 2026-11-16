
from tools_hw4 import calculate
import pytest

def test_multiplication():
    r = calculate("48317 * 1.0947")
    assert r["result"] == pytest.approx(52892.6199)

def test_division():
    r = calculate("44675 / 921.4")
    assert r["result"] == pytest.approx(48.485, abs=0.001)

def test_addition():
    assert calculate("25 + 15")["result"] == 40

def test_subtraction():
    assert calculate("100 - 35")["result"] == 65

def test_zero_division():
    assert "error" in calculate("10 / 0")

def test_dangerous_import():
    r = calculate("__import__('os').system('echo hi')")
    assert "error" in r

def test_dangerous_attribute():
    r = calculate("(1).__class__")
    assert "error" in r

def test_large_exponent():
    r = calculate("9**9**9")
    assert "error" in r

def test_empty_expression():
    assert "error" in calculate("")

def test_large_number():
    assert "error" in calculate("999999999999 * 999")
