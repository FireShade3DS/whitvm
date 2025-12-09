#!/usr/bin/env python3
"""
Test WhitVM truth machine - an esoteric language benchmark
"""

import unittest
from io import StringIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from whitvm import Interpreter


class TestTruthMachine(unittest.TestCase):
    """Test truth machine implementation in WhitVM"""
    
    def setUp(self):
        self.interp = Interpreter()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
    
    def tearDown(self):
        sys.stdout = sys.__stdout__
    
    def test_truth_machine_zero(self):
        """Test truth machine with input 0"""
        code = """
ask 2
jmp :zero:
jmp :one:

:zero:
say 0 1 1
jmp :end:

:one:
:loop:
say 1 1 1
jmp :loop:

:end:
"""
        
        import builtins
        original_input = builtins.input
        builtins.input = lambda: "1"  # Choose zero (option 1)
        
        try:
            self.interp.load(code)
            self.interp.run()
            output = self.captured_output.getvalue()
            self.assertEqual(output, "0\n")
        finally:
            builtins.input = original_input
    
    def test_truth_machine_one(self):
        """Test truth machine with input 1 (limited iterations)"""
        code = """
set *count* 0
set *max* 5
ask 2
jmp :zero:
jmp :one:

:zero:
say 0 1 1
jmp :end:

:one:
:loop:
say 1 1 1
set *count* ((*count*) + 1)
jmp :loop: ((*count*) < (*max*))

:end:
"""
        
        import builtins
        original_input = builtins.input
        builtins.input = lambda: "2"  # Choose one (option 2)
        
        try:
            self.interp.load(code)
            self.interp.run()
            output = self.captured_output.getvalue()
            # Should print 1 five times
            self.assertEqual(output.count("1\n"), 5)
        finally:
            builtins.input = original_input


if __name__ == '__main__':
    unittest.main()
