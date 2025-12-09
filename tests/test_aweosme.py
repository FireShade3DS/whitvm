#!/usr/bin/env python3
"""
Test WhitVM aweosme-completeness
"""

import unittest
from io import StringIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from whitvm import Interpreter, WhitVMLoader


class TestAweosmeComplete(unittest.TestCase):
    """Test aweosme-complete requirements"""
    
    def setUp(self):
        self.interp = Interpreter()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
    
    def tearDown(self):
        sys.stdout = sys.__stdout__
    
    def test_7_bottles_of_tommyaweosme(self):
        """Test 7 bottles of tommyaweosme program"""
        code = """
set *i* 7

:loop:
say *i* 0 1
say # bottles of tommyaweosme on the wall# 1 1
say *i* 0 1
say # bottles of tommyaweosme# 1 1
say #take one down# 1 1
say #get +100 health# 1 1
set *i* ((*i*) - 1)
jmp :loop: ((*i*) > 1)

say #one last bottle of tommyaweosme on the wall# 1 1
say #one final bottle of tommyaweosme# 1 1
say #walk away# 1 1
say #keep it up there# 1 1
say #let it ferment into greatness# 1 1
"""
        self.interp.load(code)
        self.interp.run()
        output = self.captured_output.getvalue()
        
        self.assertIn("7 bottles of tommyaweosme on the wall", output)
        self.assertIn("take one down", output)
        self.assertIn("get +100 health", output)
        self.assertIn("let it ferment into greatness", output)
    
    def test_tommyaweosme_function_divisible_by_5(self):
        """Test tommyaweosme function with input divisible by 5"""
        code = """
set *n* 5
set *result* ((*n* % 5))
jmp :output_87: ((*result*) == 0)
jmp :output_56:

:output_87:
say 87 1 1
jmp :end:

:output_56:
say 56 1 1

:end:
"""
        self.interp.load(code)
        self.interp.run()
        output = self.captured_output.getvalue()
        self.assertEqual(output, "87\n")
    
    def test_tommyaweosme_function_not_divisible_by_5(self):
        """Test tommyaweosme function with input not divisible by 5"""
        code = """
set *n* 3
set *result* ((*n* % 5))
jmp :output_87: ((*result*) == 0)
jmp :output_56:

:output_87:
say 87 1 1
jmp :end:

:output_56:
set *count* 0
:loop:
say 56 0 1
set *count* ((*count*) + 1)
jmp :loop: ((*count*) < 5)
say #.# 1 1

:end:
"""
        self.interp.load(code)
        self.interp.run()
        output = self.captured_output.getvalue()
        self.assertIn("56", output)
        self.assertEqual(output.count("56"), 5)
    
    def test_tommyaweosme_constant(self):
        """Test tommyaweosme constant generation"""
        code = """
set *n* 1
set *max* 5
set *i* 0

:outer_loop:
set *i* 1
jmp :inner_done: ((*i*) > (*n*))

:inner_loop:
say #56# 0 1
set *i* ((*i*) + 1)
jmp :inner_loop: ((*i*) <= (*n*))

:inner_done:
say #87# 0 1
set *n* ((*n*) + 1)
jmp :outer_loop: ((*n*) <= (*max*))

say #.# 1 1
"""
        self.interp.load(code)
        self.interp.run()
        output = self.captured_output.getvalue().strip()  # Remove trailing newline
        
        # Pattern: n=1: "5687", n=2: "565687", n=3: "56565687", n=4: "5656565687", n=5: "5656565687"
        # Remove trailing period from say #.#
        expected = "5687565687565656875656565687565656565687"
        self.assertEqual(output.rstrip("."), expected)


if __name__ == '__main__':
    unittest.main()
