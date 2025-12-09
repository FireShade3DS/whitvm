#!/usr/bin/env python3
"""
Unit tests for the HLL ISA Interpreter
"""

import unittest
from io import StringIO
import sys
import os

# Add src to path so we can import whitvm
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from whitvm.interpreter import Interpreter, Parser


class TestParser(unittest.TestCase):
    """Test the parser"""
    
    def test_parse_simple_label(self):
        """Test parsing a simple label"""
        code = ":start:"
        parser = Parser(code)
        self.assertIn("start", parser.labels)
        self.assertEqual(parser.labels["start"], 0)
    
    def test_parse_multiple_labels(self):
        """Test parsing multiple labels"""
        code = """
:label1:
    set *x* 1
:label2:
    set *y* 2
"""
        parser = Parser(code)
        self.assertIn("label1", parser.labels)
        self.assertIn("label2", parser.labels)
        self.assertEqual(parser.labels["label1"], 0)
        self.assertEqual(parser.labels["label2"], 1)
    
    def test_parse_instruction_set(self):
        """Test parsing set instruction"""
        code = "set *x* 42"
        parser = Parser(code)
        self.assertEqual(len(parser.instructions), 1)
        self.assertEqual(parser.instructions[0][0], "set")
        self.assertEqual(parser.instructions[0][1], "*x*")
        self.assertEqual(parser.instructions[0][2], "42")
    
    def test_parse_string_literal(self):
        """Test parsing string literals"""
        code = "say #Hello World# 1 1"
        parser = Parser(code)
        self.assertEqual(parser.instructions[0][1], "#Hello World#")
    
    def test_parse_expression(self):
        """Test parsing expressions"""
        code = "set *result* ((*a*) + (*b*))"
        parser = Parser(code)
        self.assertEqual(parser.instructions[0][2], "((*a*) + (*b*))")


class TestInterpreterBasic(unittest.TestCase):
    """Test basic interpreter functionality"""
    
    def setUp(self):
        self.interp = Interpreter()
    
    def test_set_variable(self):
        """Test setting a variable"""
        code = "set *x* 42"
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["x"], 42)
    
    def test_set_string_variable(self):
        """Test setting a variable to a string"""
        code = "set *name* #Alice#"
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["name"], "Alice")
    
    def test_sequential_execution(self):
        """Test sequential execution of instructions"""
        code = """
set *a* 10
set *b* 20
set *c* 30
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["a"], 10)
        self.assertEqual(self.interp.dmem["b"], 20)
        self.assertEqual(self.interp.dmem["c"], 30)


class TestInterpreterExpressions(unittest.TestCase):
    """Test expression evaluation
    
    Validates operator precedence, function calls, and type handling.
    """
    
    def setUp(self):
        self.interp = Interpreter()
    
    def test_addition(self):
        """Test addition in expressions"""
        code = """
set *a* 10
set *b* 20
set *c* ((*a*) + (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["c"], 30)
    
    def test_subtraction(self):
        """Test subtraction"""
        code = """
set *a* 50
set *b* 20
set *result* ((*a*) - (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 30)
    
    def test_multiplication(self):
        """Test multiplication"""
        code = """
set *a* 6
set *b* 7
set *result* ((*a*) * (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 42)
    
    def test_modulo(self):
        """Test modulo operation"""
        code = """
set *a* 17
set *b* 5
set *result* ((*a*) % (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 2)
    
    def test_division(self):
        """Test division"""
        code = """
set *a* 20
set *b* 4
set *result* ((*a*) / (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 5)
    
    def test_division_integer(self):
        """Test integer division (floor)"""
        code = """
set *a* 17
set *b* 5
set *result* ((*a*) / (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 3)
    
    def test_nested_expression(self):
        """Test nested expressions"""
        code = """
set *a* 2
set *b* 3
set *c* 4
set *result* (((*a*) + (*b*)) * (*c*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 20)
    
    def test_equality_true(self):
        """Test equality comparison (true)"""
        code = """
set *a* 5
set *b* 5
set *result* ((*a*) == (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 1)
    
    def test_equality_false(self):
        """Test equality comparison (false)"""
        code = """
set *a* 5
set *b* 6
set *result* ((*a*) == (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 0)
    
    def test_string_equality(self):
        """Test string equality"""
        code = """
set *name* #Alice#
set *result* ((*name*) == #Alice#)
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 1)
    
    def test_less_than(self):
        """Test less than comparison"""
        code = """
set *a* 3
set *b* 5
set *result* ((*a*) < (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 1)
    
    def test_greater_than(self):
        """Test greater than comparison"""
        code = """
set *a* 10
set *b* 5
set *result* ((*a*) > (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 1)
    
    def test_less_equal(self):
        """Test less than or equal"""
        code = """
set *a* 5
set *b* 5
set *result* ((*a*) <= (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 1)
    
    def test_greater_equal(self):
        """Test greater than or equal"""
        code = """
set *a* 10
set *b* 5
set *result* ((*a*) >= (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 1)
    
    def test_not_equal(self):
        """Test not equal comparison"""
        code = """
set *a* 5
set *b* 6
set *result* ((*a*) != (*b*))
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], 1)
    
    def test_rng_basic(self):
        """Test rng function"""
        code = """
set *result* (rng 1 3)
"""
        self.interp.load(code)
        self.interp.run()
        self.assertIn(self.interp.dmem["result"], [1, 2, 3])
    
    def test_rng_range(self):
        """Test rng function with larger range"""
        code = """
set *result* (rng 1 10)
"""
        self.interp.load(code)
        self.interp.run()
        self.assertGreaterEqual(self.interp.dmem["result"], 1)
        self.assertLessEqual(self.interp.dmem["result"], 10)
    
    def test_rng_with_variables(self):
        """Test rng function with variables"""
        code = """
set *min* 5
set *max* 15
set *result* (rng *min* *max*)
"""
        self.interp.load(code)
        self.interp.run()
        self.assertGreaterEqual(self.interp.dmem["result"], 5)
        self.assertLessEqual(self.interp.dmem["result"], 15)


class TestInterpreterControl(unittest.TestCase):
    """Test control flow
    
    Validates jumps, conditionals, and loops with PC manipulation.
    """
    
    def setUp(self):
        self.interp = Interpreter()
    
    def test_unconditional_jump(self):
        """Test unconditional jump"""
        code = """
set *x* 0
jmp :skip:
set *x* 1

:skip:
set *x* 2
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["x"], 2)
    
    def test_conditional_jump_true(self):
        """Test conditional jump when condition is true"""
        code = """
set *x* 0
jmp :branch: 1
set *x* 1

:branch:
set *x* 2
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["x"], 2)
    
    def test_conditional_jump_false(self):
        """Test conditional jump when condition is false"""
        code = """
set *x* 0
jmp :branch: 0
set *x* 1
jmp :end:

:branch:
set *x* 2

:end:
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["x"], 1)
    
    def test_conditional_jump_with_expression(self):
        """Test conditional jump with expression"""
        code = """
set *score* 85
set *result* #fail#
jmp :pass: ((*score*) >= 70)
set *result* #fail#
jmp :end:

:pass:
set *result* #pass#

:end:
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["result"], "pass")
    
    def test_loop_with_counter(self):
        """Test a simple loop"""
        code = """
set *count* 0
set *sum* 0

:loop:
jmp :end: ((*count*) >= 5)
set *sum* ((*sum*) + (*count*))
set *count* ((*count*) + 1)
jmp :loop:

:end:
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["sum"], 10)  # 0+1+2+3+4


class TestInterpreterSay(unittest.TestCase):
    """Test say instruction
    
    Validates output printing with variable newlines and conditional execution.
    """
    
    def setUp(self):
        self.interp = Interpreter()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
    
    def tearDown(self):
        sys.stdout = sys.__stdout__
    
    def test_say_string(self):
        """Test printing a string"""
        code = "say #Hello# 1 1"
        self.interp.load(code)
        self.interp.run()
        self.assertIn("Hello", self.captured_output.getvalue())
    
    def test_say_variable(self):
        """Test printing a variable"""
        code = """
set *value* 42
say *value* 1 1
"""
        self.interp.load(code)
        self.interp.run()
        self.assertIn("42", self.captured_output.getvalue())
    
    def test_say_multiple_lines(self):
        """Test printing with multiple newlines"""
        code = "say #Text# 3 1"
        self.interp.load(code)
        self.interp.run()
        output = self.captured_output.getvalue()
        self.assertEqual(output.count('\n'), 3)
    
    def test_say_conditional_true(self):
        """Test conditional say (true)"""
        code = "say #Shown# 1 1"
        self.interp.load(code)
        self.interp.run()
        self.assertIn("Shown", self.captured_output.getvalue())
    
    def test_say_conditional_false(self):
        """Test conditional say (false)"""
        code = "say #Hidden# 1 0"
        self.interp.load(code)
        self.interp.run()
        self.assertNotIn("Hidden", self.captured_output.getvalue())
    
    def test_say_no_newline(self):
        """Test say with zero newlines (concatenation)"""
        code = """
say #Hello# 0 1
say # # 0 1
say #World# 1 1
"""
        self.interp.load(code)
        self.interp.run()
        output = self.captured_output.getvalue()
        self.assertEqual(output, "Hello World\n")


class TestInterpreterAsk(unittest.TestCase):
    """Test ask instruction
    
    Validates user input handling and PC jumps based on user selection.
    """
    
    def setUp(self):
        self.interp = Interpreter()
    
    def test_ask_jumps_correctly(self):
        """Test that ask jumps to correct instruction based on input"""
        code = """
ask 2
jmp :option1:
jmp :option2:

:option1:
set *result* 1
jmp :end:

:option2:
set *result* 2

:end:
"""
        # Simulate input of 1
        self.interp.load(code)
        # Mock the input
        import builtins
        original_input = builtins.input
        builtins.input = lambda: "1"
        
        try:
            self.interp.run()
            self.assertEqual(self.interp.dmem["result"], 1)
        finally:
            builtins.input = original_input
    
    def test_ask_with_input_2(self):
        """Test ask with input 2"""
        code = """
ask 2
jmp :option1:
jmp :option2:

:option1:
set *result* 1
jmp :end:

:option2:
set *result* 2

:end:
"""
        import builtins
        original_input = builtins.input
        builtins.input = lambda: "2"
        
        try:
            self.interp.load(code)
            self.interp.run()
            self.assertEqual(self.interp.dmem["result"], 2)
        finally:
            builtins.input = original_input

    def test_ask_invalid_input_defaults_to_option_1(self):
        """Test that invalid input (out of range) defaults to option 1"""
        code = """
ask 2
jmp :option1:
jmp :option2:

:option1:
set *result* 1
jmp :end:

:option2:
set *result* 2

:end:
"""
        import builtins
        original_input = builtins.input
        builtins.input = lambda: "999"  # Invalid input
        
        try:
            self.interp.load(code)
            self.interp.run()
            self.assertEqual(self.interp.dmem["result"], 1)  # Should default to option 1
        finally:
            builtins.input = original_input

    def test_ask_disabled_skips_all_options(self):
        """Test that ask with condition=0 skips all option jumps"""
        code = """
ask 3 0
jmp :option1:
jmp :option2:
jmp :option3:
set *result* 99
halt

:option1:
set *result* 1
halt

:option2:
set *result* 2
halt

:option3:
set *result* 3
halt
"""
        self.interp.load(code)
        self.interp.run()
        # Should skip all 3 jumps and execute the next instruction (set *result* 99)
        self.assertEqual(self.interp.dmem["result"], 99)

    def test_ask_with_three_options(self):
        """Test ask with 3 options"""
        code = """
ask 3
jmp :option1:
jmp :option2:
jmp :option3:

:option1:
set *result* 1
jmp :end:

:option2:
set *result* 2
jmp :end:

:option3:
set *result* 3

:end:
"""
        import builtins
        original_input = builtins.input
        
        # Test option 3
        builtins.input = lambda: "3"
        
        try:
            self.interp.load(code)
            self.interp.run()
            self.assertEqual(self.interp.dmem["result"], 3)
        finally:
            builtins.input = original_input


class TestInterpreterHalt(unittest.TestCase):
    """Test halt instruction
    
    Validates program termination with conditional execution.
    """
    
    def setUp(self):
        self.interp = Interpreter()
    
    def test_halt_instruction(self):
        """Test halt instruction"""
        code = """
set *x* 1
halt
set *x* 2
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["x"], 1)
    
    def test_halt_conditional_true(self):
        """Test conditional halt (true)"""
        code = """
set *x* 1
halt 1
set *x* 2
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["x"], 1)
    
    def test_halt_conditional_false(self):
        """Test conditional halt (false) - continues execution"""
        code = """
set *x* 1
halt 0
set *x* 2
"""
        self.interp.load(code)
        self.interp.run()
        self.assertEqual(self.interp.dmem["x"], 2)


class TestInterpreterErrors(unittest.TestCase):
    """Test error handling
    
    Validates error detection for undefined variables, labels, and invalid operations.
    """
    
    def setUp(self):
        self.interp = Interpreter()
    
    def test_undefined_variable(self):
        """Test error on undefined variable"""
        code = "say *undefined* 1 1"
        self.interp.load(code)
        with self.assertRaises(ValueError):
            self.interp.run()
    
    def test_undefined_label(self):
        """Test error on undefined label"""
        code = "jmp :undefined:"
        self.interp.load(code)
        with self.assertRaises(ValueError):
            self.interp.run()
    
    def test_invalid_set_argument(self):
        """Test error when set gets non-variable as first arg"""
        code = "set 42 10"
        self.interp.load(code)
        with self.assertRaises(ValueError):
            self.interp.run()


if __name__ == '__main__':
    unittest.main()
