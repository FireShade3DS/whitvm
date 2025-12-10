#!/usr/bin/env python3
"""
Test minifier optimizations
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from whitvm import WhitVMMinifier


class TestMinifierOptimizations(unittest.TestCase):
    """Test advanced minifier optimizations"""
    
    def test_expression_simplification(self):
        """Test expression simplification removes nested parens"""
        code = """
set *x* ((*a*))
set *y* (((5)))
set *z* ((*a*) + (*b*))
"""
        minified = WhitVMMinifier.minify(code, simplify_expr=True)
        
        # ((*a*)) should become (*a*)
        self.assertIn("set *x* (*a*)", minified)
        # (((5))) should become (5) after simplification
        self.assertIn("set *y* (5)", minified)
        # ((*a*) + (*b*)) should stay (has operator)
        self.assertIn("set *z* ((*a*) + (*b*))", minified)
    
    def test_constant_evaluation(self):
        """Test constant expression evaluation"""
        code = """
set *a* (5 + 3)
set *b* (10 / 2)
set *c* (2 * 3)
"""
        minified = WhitVMMinifier.minify(code, eval_const=True)
        
        self.assertIn("set *a* 8", minified)
        self.assertIn("set *b* 5", minified)
        self.assertIn("set *c* 6", minified)
    
    def test_string_pooling(self):
        """Test repeated strings are pooled into variables"""
        code = """
say #Hello# 1 1
say #World# 1 1
say #Hello# 1 1
say #Hello# 1 1
"""
        minified = WhitVMMinifier.minify(code, pool_strings=True)
        
        # #Hello# appears 3 times, should be pooled
        # Should have set statement for pooled string
        self.assertIn("set *", minified)
        # Original strings should be replaced with var refs
        hello_count = minified.count("#Hello#")
        self.assertLessEqual(hello_count, 1)  # At most 1 in set statement
    
    def test_dead_code_removal(self):
        """Test unused variable removal"""
        code = """
set *unused* 42
set *used* 10
say *used* 1 1
"""
        minified = WhitVMMinifier.minify(code, dead_code=True)
        
        # *unused* is never read, should be removed
        self.assertNotIn("set *unused*", minified)
        # *used* is read, should stay
        self.assertIn("set *used*", minified)
    
    def test_name_shrinking(self):
        """Test variable and label name shrinking"""
        code = """
set *player_health* 100
set *enemy_damage* 10
:main_loop:
say *player_health* 1 1
jmp :main_loop: (1)
"""
        minified = WhitVMMinifier.minify(code, shrink_names=True)
        
        # Long names should be replaced with short ones
        self.assertNotIn("player_health", minified)
        self.assertNotIn("enemy_damage", minified)
        self.assertNotIn("main_loop", minified)
        
        # Should have short variable/label names
        self.assertRegex(minified, r'\*[a-z]\*')
        self.assertRegex(minified, r':[a-z]:')
    
    def test_unreachable_code_removal(self):
        """Test unreachable code after halt is removed"""
        code = """
say #Start# 1 1
halt
say #Never reached# 1 1
:label:
say #But label stays# 1 1
"""
        minified = WhitVMMinifier.minify(code, remove_unreachable=True)
        
        # Code between halt and label should be removed
        self.assertNotIn("Never reached", minified)
        # Label and code after it should stay
        self.assertIn(":label:", minified)
        self.assertIn("But label stays", minified)
    
    def test_ask_dispatch_preservation(self):
        """Test that ask dispatch patterns are preserved"""
        code = """
ask 3
jmp :opt1:
jmp :opt2:
jmp :opt3:
:opt1:
say #Option 1# 1 1
halt
:opt2:
say #Option 2# 1 1
halt
:opt3:
say #Option 3# 1 1
halt
"""
        minified = WhitVMMinifier.minify(code, remove_unreachable=True)
        
        # All three jumps should be preserved (ask dispatch)
        self.assertEqual(minified.count("jmp"), 3)
    
    def test_combined_optimizations(self):
        """Test all optimizations together"""
        code = """
set *player_health* (((100)))
set *unused_var* 999
say #Game Start# 1 0
:main_loop:
say #Your health: # 0 1
say *player_health* 1 1
set *player_health* ((*player_health*) - 1)
jmp :main_loop: ((*player_health*) > 0)
say #Game Over# 1 1
halt
say #Unreachable# 1 1
"""
        minified = WhitVMMinifier.minify(code,
            shrink_names=True,
            eval_const=True,
            simplify_expr=True,
            pool_strings=True,
            dead_code=True,
            remove_unreachable=True)
        
        # Should be significantly smaller
        self.assertLess(len(minified), len(code) * 0.7)
        
        # Should not have original long names
        self.assertNotIn("player_health", minified)
        self.assertNotIn("unused_var", minified)
        
        # Should not have unreachable code
        self.assertNotIn("Unreachable", minified)
        
        # Should still be valid (parseable)
        from whitvm import Interpreter
        interp = Interpreter()
        interp.load(minified)  # Should not raise


if __name__ == '__main__':
    unittest.main()
