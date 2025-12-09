#!/usr/bin/env python3
"""
Test WhitVM with a Mad Libs style interactive story
"""

import unittest
from io import StringIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from whitvm import Interpreter


class TestMadLibs(unittest.TestCase):
    """Test Mad Libs style program with user input and concatenation"""
    
    def setUp(self):
        self.interp = Interpreter()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
    
    def tearDown(self):
        sys.stdout = sys.__stdout__
    
    def test_simple_madlibs(self):
        """Test a simple Mad Libs story with user input"""
        code = """
say #Welcome to Mad Libs!# 2 1
say #Pick an adjective (1=scary, 2=silly, 3=angry):# 1 1
ask 3
jmp :scary:
jmp :silly:
jmp :angry:

:scary:
    set *adj* #scary#
    jmp :noun:

:silly:
    set *adj* #silly#
    jmp :noun:

:angry:
    set *adj* #angry#
    jmp :noun:

:noun:
    say #Pick a noun (1=dragon, 2=unicorn, 3=robot):# 1 1
    ask 3
    jmp :dragon:
    jmp :unicorn:
    jmp :robot:

:dragon:
    set *noun* #dragon#
    jmp :verb:

:unicorn:
    set *noun* #unicorn#
    jmp :verb:

:robot:
    set *noun* #robot#
    jmp :verb:

:verb:
    say #Pick a verb (1=danced, 2=sang, 3=flew):# 1 1
    ask 3
    jmp :danced:
    jmp :sang:
    jmp :flew:

:danced:
    set *verb* #danced#
    jmp :story:

:sang:
    set *verb* #sang#
    jmp :story:

:flew:
    set *verb* #flew#
    jmp :story:

:story:
    say #Your story:# 2 1
    say #Once upon a time, a # 0 1
    say *adj* 0 1
    say # # 0 1
    say *noun* 0 1
    say # # 0 1
    say *verb* 0 1
    say # in the moonlight.# 2 1
    say #The End!# 1 1
"""
        
        import builtins
        original_input = builtins.input
        inputs = iter(["1", "2", "3"])  # scary, unicorn, flew
        builtins.input = lambda: next(inputs)
        
        try:
            self.interp.load(code)
            self.interp.run()
            output = self.captured_output.getvalue()
            
            # Check story parts are in output
            self.assertIn("Your story:", output)
            self.assertIn("Once upon a time, a scary unicorn flew in the moonlight.", output)
            self.assertIn("The End!", output)
        finally:
            builtins.input = original_input
    
    def test_madlibs_variable_storage(self):
        """Test that variables are properly stored during Mad Libs"""
        code = """
say #Adjective (1=green, 2=blue):# 0 1
ask 2
jmp :green:
jmp :blue:

:green:
    set *color* #green#
    jmp :show:

:blue:
    set *color* #blue#
    jmp :show:

:show:
    say #You chose: # 0 1
    say *color* 1 1
"""
        
        import builtins
        original_input = builtins.input
        builtins.input = lambda: "2"
        
        try:
            self.interp.load(code)
            self.interp.run()
            
            # Check the variable was set correctly
            self.assertEqual(self.interp.dmem["color"], "blue")
            output = self.captured_output.getvalue()
            self.assertIn("You chose: blue", output)
        finally:
            builtins.input = original_input
    
    def test_madlibs_string_concatenation(self):
        """Test string concatenation with nl_qty 0"""
        code = """
set *name* #Alice#
set *food* #pizza#
say #Once there was someone named # 0 1
say *name* 0 1
say # who loved # 0 1
say *food* 1 1
"""
        
        self.interp.load(code)
        self.interp.run()
        output = self.captured_output.getvalue()
        
        self.assertEqual(output, "Once there was someone named Alice who loved pizza\n")


if __name__ == '__main__':
    unittest.main()
