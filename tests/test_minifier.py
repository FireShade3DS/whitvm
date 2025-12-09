#!/usr/bin/env python3
"""
Unit tests for WhitVM Minifier
"""

import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from whitvm import WhitVMMinifier


class TestMinifier(unittest.TestCase):
    """Test minifier functionality"""
    
    def test_remove_comments(self):
        """Test removal of comment lines"""
        code = """
say #This is a comment# 1 0
set *x* 42
say #Another comment# 1 0
say *x* 1 1
"""
        minified = WhitVMMinifier.minify(code, shrink_vars=False, remove_defaults=False)
        self.assertNotIn("This is a comment", minified)
        self.assertNotIn("Another comment", minified)
        self.assertIn("set *x* 42", minified)
        self.assertIn("say *x*", minified)
    
    def test_remove_blank_lines(self):
        """Test removal of blank lines"""
        code = """
set *x* 42

set *y* 10

say *x* 1 1
"""
        minified = WhitVMMinifier.minify(code)
        lines = minified.split('\n')
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertTrue(line.strip())  # All lines have content
    
    def test_remove_leading_whitespace(self):
        """Test removal of leading whitespace"""
        code = """
    set *x* 42
        say *x* 1 1
set *y* 10
"""
        minified = WhitVMMinifier.minify(code)
        lines = minified.split('\n')
        for line in lines:
            self.assertFalse(line.startswith(' '))
    
    def test_preserve_content(self):
        """Test that non-comment content is preserved"""
        code = """
:loop:
set *count* 0
:count_loop:
say *count* 1 1
set *count* ((*count*) + 1)
jmp :count_loop: ((*count*) < 5)
"""
        minified = WhitVMMinifier.minify(code, shrink_vars=False, shrink_labels=False)
        self.assertIn(":loop:", minified)
        self.assertIn("set *count* 0", minified)
        # Check for the jmp instruction with the loop label (variable might be renamed)
        self.assertIn("jmp :count_loop:", minified)
        self.assertIn("((*count*) < 5)", minified)
    
    def test_distinguish_comment_from_output(self):
        """Test that say with condition 1 is preserved"""
        code = """
say #This is output# 1 1
say #This is a comment# 1 0
say #This too# 1 1
"""
        minified = WhitVMMinifier.minify(code, remove_defaults=False)
        self.assertIn("say #This is output#", minified)
        self.assertIn("say #This too#", minified)
        self.assertNotIn("say #This is a comment#", minified)
    
    def test_handle_expressions(self):
        """Test that comments with expressions are handled correctly"""
        code = """
say #Check# 1 0
set *result* ((*a*) + (*b*))
say #Result: # 1 0
say *result* 1 1
"""
        minified = WhitVMMinifier.minify(code, shrink_vars=False)
        self.assertNotIn("say #Check#", minified)
        self.assertNotIn("say #Result: #", minified)
        self.assertIn("set *result* ((*a*) + (*b*))", minified)
        self.assertIn("say *result*", minified)
    
    def test_empty_input(self):
        """Test with empty input"""
        code = ""
        minified = WhitVMMinifier.minify(code)
        self.assertEqual(minified, "")
    
    def test_only_comments(self):
        """Test with only comment lines"""
        code = """
say #Comment 1# 1 0
say #Comment 2# 1 0
say #Comment 3# 1 0
"""
        minified = WhitVMMinifier.minify(code)
        self.assertEqual(minified, "")
    
    def test_nested_comments_in_expressions(self):
        """Test that say with complex expressions keeps condition tokens"""
        code = """
set *x* ((*a*) + (*b*))
say #Debug: (value is ((*x*)))# 1 0
say *x* 1 1
"""
        minified = WhitVMMinifier.minify(code, shrink_vars=False)
        self.assertNotIn("#Debug: (value is ((*x*)))#", minified)
        self.assertIn("set *x* ((*a*) + (*b*))", minified)
        self.assertIn("say *x*", minified)


if __name__ == '__main__':
    unittest.main()
