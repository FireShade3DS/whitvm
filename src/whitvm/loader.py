#!/usr/bin/env python3
"""
WhitVM file loader - Parse and load .whitvm files
"""

import os
from pathlib import Path
from typing import Union


class Loader:
    """Alias for backwards compatibility."""
    pass


class WhitVMLoader:
    """Load and validate WhitVM files"""
    
    WHITVM_EXTENSION = '.whitvm'
    
    @staticmethod
    def load_file(filepath: Union[str, Path]) -> str:
        """Load a WhitVM file and return its code"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"WhitVM file not found: {filepath}")
        
        if filepath.suffix != WhitVMLoader.WHITVM_EXTENSION:
            raise ValueError(f"Expected {WhitVMLoader.WHITVM_EXTENSION} file, got {filepath.suffix}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except IOError as e:
            raise IOError(f"Error reading WhitVM file: {e}")
        
        return code
    
    @staticmethod
    def load_from_string(code: str, validate: bool = False) -> str:
        """Load code from string (for testing/embedding)"""
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")
        
        if validate:
            WhitVMLoader.validate_syntax(code)
        
        return code
    
    @staticmethod
    def validate_syntax(code: str) -> bool:
        """Basic syntax validation for WhitVM code"""
        lines = code.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line:
                continue
            
            # Check for unclosed delimiters
            hash_count = line.count('#') - (line.count('##') * 2)
            if hash_count % 2 != 0:
                raise SyntaxError(f"Line {i}: Unclosed string literal (unmatched #)")
            
            paren_depth = 0
            for char in line:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                if paren_depth < 0:
                    raise SyntaxError(f"Line {i}: Unmatched closing parenthesis")
            
            if paren_depth != 0:
                raise SyntaxError(f"Line {i}: Unclosed expression (unmatched parenthesis)")
        
        return True
    
    @staticmethod
    def find_whitvm_files(directory: Union[str, Path]) -> list:
        """Find all .whitvm files in a directory"""
        directory = Path(directory)
        
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")
        
        return sorted(directory.glob(f'*{WhitVMLoader.WHITVM_EXTENSION}'))
