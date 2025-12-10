#!/usr/bin/env python3
"""
WhitVM Minifier Core - Essential minification passes
Removes comments, blank lines, default arguments, and excess whitespace
"""

from typing import List


class MinifierCore:
    """Core minification operations"""
    
    @staticmethod
    def minify_essential(code: str) -> str:
        """Apply essential minification only
        
        Removes:
        - Comment lines (say ... 1 0)
        - Blank lines
        - Default arguments (say ... 1 1 → say ...)
        - Excess whitespace
        
        Safe and non-lossy optimizations
        """
        lines = code.strip().split('\n')
        
        # Pass 1: Remove comments and blank lines
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line or MinifierCore._is_comment_line(line):
                continue
            cleaned.append(line)
        
        # Pass 2: Remove default arguments
        cleaned = [MinifierCore._remove_defaults(line) for line in cleaned]
        
        # Pass 3: Compact spacing
        cleaned = [MinifierCore._compact_spacing(line) for line in cleaned]
        
        return '\n'.join(cleaned)
    
    @staticmethod
    def _is_comment_line(line: str) -> bool:
        """Check if a line is a comment (say ... 1 0)"""
        if not line.startswith('say'):
            return False
        
        tokens = MinifierCore._extract_tokens(line)
        if len(tokens) < 3:
            return False
        
        return tokens[-2] == '1' and tokens[-1] == '0'
    
    @staticmethod
    def _remove_defaults(line: str) -> str:
        """Remove default arguments (1 1 from say, 1 from jmp/ask)"""
        tokens = MinifierCore._extract_tokens(line)
        
        if not tokens:
            return line
        
        opcode = tokens[0]
        
        # say value nl_qty condition
        if opcode == 'say' and len(tokens) >= 3:
            if len(tokens) == 4 and tokens[-2] == '1' and tokens[-1] == '1':
                return ' '.join(tokens[:-2])
            elif len(tokens) == 3 and tokens[-1] == '1':
                return ' '.join(tokens[:-1])
        
        # jmp/ask with default condition
        elif opcode in ('jmp', 'ask') and len(tokens) >= 2:
            if tokens[-1] == '1':
                return ' '.join(tokens[:-1])
        
        return line
    
    @staticmethod
    def _compact_spacing(line: str) -> str:
        """Remove extra spaces while preserving token boundaries"""
        tokens = MinifierCore._extract_tokens(line)
        return ' '.join(tokens)
    
    @staticmethod
    def _extract_tokens(line: str) -> list:
        """Extract tokens from a line, respecting string/expression boundaries"""
        tokens = []
        i = 0
        
        while i < len(line):
            # Skip whitespace
            while i < len(line) and line[i].isspace():
                i += 1
            if i >= len(line):
                break
            
            # String literal
            if line[i] == '#':
                end = line.find('#', i + 1)
                if end != -1:
                    tokens.append(line[i:end+1])
                    i = end + 1
                else:
                    break
            # Expression
            elif line[i] == '(':
                depth = 1
                j = i + 1
                while j < len(line) and depth > 0:
                    if line[j] == '(':
                        depth += 1
                    elif line[j] == ')':
                        depth -= 1
                    j += 1
                tokens.append(line[i:j])
                i = j
            # Label reference
            elif line[i] == ':':
                j = i + 1
                while j < len(line) and line[j] != ':':
                    j += 1
                if j < len(line) and line[j] == ':':
                    tokens.append(line[i:j+1])
                    i = j + 1
                else:
                    break
            # Variable
            elif line[i] == '*':
                end = line.find('*', i + 1)
                if end != -1:
                    tokens.append(line[i:end+1])
                    i = end + 1
                else:
                    break
            # Regular token
            else:
                j = i
                while j < len(line) and not line[j].isspace() and line[j] not in '()#*:':
                    j += 1
                if j > i:
                    tokens.append(line[i:j])
                i = j
        
        return tokens
