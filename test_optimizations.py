#!/usr/bin/env python3
"""Test the new optimizations"""

from src.whitvm import WhitVMMinifier

# Test 1: Expression simplification
code1 = """
set *x* ((*a*))
set *y* (((5)))
set *z* ((*a*) + (*b*))
"""

print("=== Expression Simplification ===")
print("Original:")
print(code1)
minified1 = WhitVMMinifier.minify(code1, shrink_vars=False, shrink_labels=False)
print("\nMinified:")
print(minified1)

# Test 2: Unused jump elimination
code2 = """
:loop:
set *count* 0

:check:
say *count* 1 1
set *count* ((*count*) + 1)
jmp :check: ((*count*) < 3)

:next:
say #Done# 1 1
halt
"""

print("\n=== Unused Jump Elimination ===")
print("Original:")
print(code2)
minified2 = WhitVMMinifier.minify(code2, shrink_vars=False, shrink_labels=False)
print("\nMinified:")
print(minified2)

# Test 3: Combined optimizations
code3 = """
set *health* (((100)))
set *damage* (10 + 5)
say #Starting game# 1 0
say #Health: # 0 1
say *health* 1 1
"""

print("\n=== Combined Optimizations ===")
print("Original:")
print(code3)
minified3 = WhitVMMinifier.minify(code3, shrink_vars=False, shrink_labels=False)
print("\nMinified:")
print(minified3)
