# type def pertaining to base_case; see READEME.md in /src/base_/case/ for details
import json
import operator
import typing

from typing import Callable, TypeVar

# Number Systems
# (No implementation needed)

# Arithmetic Operations
T = TypeVar('T')

def addition(a: T, b: T) -> T:
    return operator.add(a, b)

def subtraction(a: T, b: T) -> T:
    return operator.sub(a, b)

def multiplication(a: T, b: T) -> T:
    return operator.mul(a, b)

def division(a: T, b: T) -> T:
    return operator.truediv(a, b)

def exponentiation(a: T, b: T) -> T:
    return operator.pow(a, b)

# Arithmetic Properties
def commutativity(op: Callable[[T, T], T], a: T, b: T) -> bool:
    return op(a, b) == op(b, a)

def associativity(op: Callable[[T, T, T], T], a: T, b: T, c: T) -> bool:
    return op(op(a, b), c) == op(a, op(b, c))

def distributivity(a: T, b: T, c: T) -> bool:
    return multiplication(a, addition(b, c)) == addition(multiplication(a, b), multiplication(a, c))

# Ordering and Inequalities
def equality(a: T, b: T) -> bool:
    return operator.eq(a, b)

def inequality(a: T, b: T) -> bool:
    return operator.ne(a, b)

def less_than(a: T, b: T) -> bool:
    return operator.lt(a, b)

def greater_than(a: T, b: T) -> bool:
    return operator.gt(a, b)

def less_than_or_equal_to(a: T, b: T) -> bool:
    return operator.le(a, b)

def greater_than_or_equal_to(a: T, b: T) -> bool:
    return operator.ge(a, b)

def trichotomy(a: T, b: T) -> bool:
    return less_than(a, b) or equality(a, b) or greater_than(a, b)

# Limits and Infinities
# (No implementation needed)

# Logical Foundations
def and_operator(a: bool, b: bool) -> bool:
    return operator.and_(a, b)

def or_operator(a: bool, b: bool) -> bool:
    return operator.or_(a, b)

def not_operator(a: bool) -> bool:
    return operator.not_(a)

def implication(a: bool, b: bool) -> bool:
    return not_operator(a) or b

def biconditional(a: bool, b: bool) -> bool:
    return and_operator(implication(a, b), implication(b, a))

# Sets and Set Operations
set_operations = {
    'union': operator.or_,
    'intersection': operator.and_,
    'difference': operator.sub,
    'complement': operator.xor
}

# Functions and Relations
def function_application(f: Callable[[T], T], x: T) -> T:
    return f(x)

def composition(f: Callable[[T], T], g: Callable[[T], T]) -> Callable[[T], T]:
    return lambda x: f(g(x))

def run_tests():
    print("Testing arithmetic operations:")
    print("2 + 3 =", addition(2, 3))
    print("5 - 3 =", subtraction(5, 3))
    print("2 * 4 =", multiplication(2, 4))
    print("6 / 3 =", division(6, 3))
    print("2 ** 3 =", exponentiation(2, 3))

    print("\nTesting arithmetic properties:")
    print("2 + 3 = 3 + 2 =", commutativity(addition, 2, 3))
    print("2 + 3 + 4 = 3 + 2 + 4 =", associativity(addition, 2, 3, 4))
    print("2 * 3 = 3 * 2 =", commutativity(multiplication, 2, 3))
    print("2 * 3 * 4 = 3 * 2 * 4 =", associativity(multiplication, 2, 3, 4))
    print("2 * (3 + 4) = (2 * 3) + (2 * 4) =", distributivity(2, 3, 4))

    print("\nTesting ordering and inequalities:")
    print("2 < 3 =", less_than(2, 3))
    print("2 <= 3 =", less_than_or_equal_to(2, 3))
    print("2 > 3 =", greater_than(2, 3))
    print("2 >= 3 =", greater_than_or_equal_to(2, 3))
    print("2 < 3 < 4 =", trichotomy(2, 3))

    print("\nTesting limits and infinities:")
    print("2 < 3 < 4 < 5 =", trichotomy(2, 5))

    print("\nTesting logical foundations:")
    print("True and True =", and_operator(True, True))
    print("True and False =", and_operator(True, False))
    print("True or True =", or_operator(True, True))

    print("\nTesting sets and set operations:")
    print("set([1, 2, 3]) =", set([1, 2, 3]))
    print("set([1, 2, 3]) | set([2, 3, 4]) =", set_operations['union'](set([1, 2, 3]), set([2, 3, 4])))
    print("set([1, 2, 3]) & set([2, 3, 4]) =", set_operations['intersection'](set([1, 2, 3]), set([2, 3, 4])))
    print("set([1, 2, 3]) - set([2, 3, 4]) =", set_operations['difference'](set([1, 2, 3]), set([2, 3, 4])))
    print("set([1, 2, 3]) ^ set([2, 3, 4]) =", set_operations['complement'](set([1, 2, 3]), set([2, 3, 4])))

    print("\nTesting functions and relations:")
    print("function_application(lambda x: x + 1, 2) =", function_application(lambda x: x + 1, 2))
    print("composition(lambda x: x + 1, lambda x: x * 2) =", composition(lambda x: x + 1, lambda x: x * 2))

    print("\nDone!")

if __name__ == "__main__":
    run_tests()