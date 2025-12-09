#!/usr/bin/env python3
"""
Unit tests for the WhitVM loader
"""

import unittest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from whitvm.loader import WhitVMLoader


class TestWhitVMLoader(unittest.TestCase):
    """Test the WhitVM file loader"""
    
    def test_load_file_basic(self):
        """Test loading a basic whitvm file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.whitvm', delete=False) as f:
            f.write("set *x* 42\n")
            f.write("say *x* 1 1\n")
            temp_file = f.name
        
        try:
            code = WhitVMLoader.load_file(temp_file)
            self.assertIn("set *x* 42", code)
            self.assertIn("say *x* 1 1", code)
        finally:
            os.unlink(temp_file)
    
    def test_load_file_not_found(self):
        """Test error when file doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            WhitVMLoader.load_file("nonexistent.whitvm")
    
    def test_load_file_wrong_extension(self):
        """Test error when file has wrong extension"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("set *x* 42\n")
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                WhitVMLoader.load_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_from_string(self):
        """Test loading from string"""
        code = "set *x* 42\nsay *x* 1 1"
        result = WhitVMLoader.load_from_string(code)
        self.assertEqual(result, code)
    
    def test_load_from_empty_string(self):
        """Test error on empty string"""
        with self.assertRaises(ValueError):
            WhitVMLoader.load_from_string("")
    
    def test_validate_syntax_valid(self):
        """Test syntax validation on valid code"""
        code = """
set *x* 42
say #Hello# 1 1
jmp :end: (*x* > 10)
:end:
"""
        self.assertTrue(WhitVMLoader.validate_syntax(code))
    
    def test_validate_syntax_unclosed_string(self):
        """Test syntax validation detects unclosed strings"""
        code = "say #Hello 1 1"
        with self.assertRaises(SyntaxError):
            WhitVMLoader.validate_syntax(code)
    
    def test_validate_syntax_unclosed_paren(self):
        """Test syntax validation detects unclosed parentheses"""
        code = "set *result* ((*a*) + (*b*)"
        with self.assertRaises(SyntaxError):
            WhitVMLoader.validate_syntax(code)
    
    def test_validate_syntax_extra_paren(self):
        """Test syntax validation detects extra parentheses"""
        code = "set *result* ((*a*) + (*b*)))"
        with self.assertRaises(SyntaxError):
            WhitVMLoader.validate_syntax(code)
    
    def test_find_whitvm_files(self):
        """Test finding whitvm files in directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some whitvm files
            Path(os.path.join(tmpdir, "game1.whitvm")).touch()
            Path(os.path.join(tmpdir, "game2.whitvm")).touch()
            Path(os.path.join(tmpdir, "readme.txt")).touch()
            
            files = WhitVMLoader.find_whitvm_files(tmpdir)
            self.assertEqual(len(files), 2)
            names = [f.name for f in files]
            self.assertIn("game1.whitvm", names)
            self.assertIn("game2.whitvm", names)
    
    def test_find_whitvm_files_not_directory(self):
        """Test error when path is not a directory"""
        with tempfile.NamedTemporaryFile() as f:
            with self.assertRaises(NotADirectoryError):
                WhitVMLoader.find_whitvm_files(f.name)


if __name__ == '__main__':
    unittest.main()
