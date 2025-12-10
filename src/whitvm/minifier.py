#!/usr/bin/env python3
"""
WhitVM Minifier - Refactored with optional advanced optimizations
"""

import re
import random
from pathlib import Path
from typing import Union, Dict, Any, List
from .minifier_core import MinifierCore


class WhitVMMinifier:
    """Minify WhitVM code with optional advanced optimizations"""
    
    @staticmethod
    def minify(code: str, 
               shrink_names: bool = False,
               eval_const: bool = False,
               simplify_expr: bool = False,
               pool_strings: bool = False,
               dead_code: bool = False,
               remove_unreachable: bool = False) -> str:
        """Minify WhitVM code
        
        Always applied (essential):
        - Remove comments (say ... 1 0)
        - Remove blank lines
        - Remove default arguments (say ... 1 1 → say ...)
        - Compact whitespace
        
        Optional (advanced):
        - shrink_names: Rename variables/labels to single chars (*var* → *a*)
        - eval_const: Evaluate constant expressions ((5 + 3) → 8)
        - simplify_expr: Remove unnecessary nested parens (((*x*)) → (*x*))
        - pool_strings: Extract repeated strings into variables
        - dead_code: Remove unused variables
        - remove_unreachable: Remove code after halt/jmp
        
        Args:
            code: WhitVM source code
            shrink_names: Shrink variable and label names
            eval_const: Evaluate constant expressions
            simplify_expr: Simplify expressions
            pool_strings: Pool repeated strings
            dead_code: Remove unused variables
            remove_unreachable: Remove unreachable code
            
        Returns:
            Minified code
        """
        # Essential minification
        lines = MinifierCore.minify_essential(code).split('\n')
        
        # Optional optimizations
        if shrink_names:
            lines = WhitVMMinifier._shrink_names(lines)
        
        if eval_const:
            lines = [WhitVMMinifier._eval_constants(line) for line in lines]
        
        if simplify_expr:
            lines = [WhitVMMinifier._simplify_expression(line) for line in lines]
        
        if pool_strings:
            string_map = WhitVMMinifier._build_string_map(lines)
            lines = [WhitVMMinifier._apply_string_map(line, string_map) for line in lines]
            setup_lines = WhitVMMinifier._create_string_setup(string_map)
            lines = setup_lines + lines
        
        if dead_code:
            lines = WhitVMMinifier._remove_dead_code(lines)
        
        if remove_unreachable:
            lines = WhitVMMinifier._remove_unreachable_code(lines)
        
        return '\n'.join(lines)
    
    @staticmethod
    def _shrink_names(lines: list) -> list:
        """Shrink variable and label names"""
        # Build maps
        var_map = WhitVMMinifier._build_var_map(lines)
        label_map = WhitVMMinifier._build_label_map(lines)
        
        # Apply maps
        lines = [WhitVMMinifier._apply_var_map(line, var_map) for line in lines]
        lines = [WhitVMMinifier._apply_label_map(line, label_map) for line in lines]
        
        return lines
    
    @staticmethod
    def _build_var_map(lines: list) -> Dict[str, str]:
        """Build variable name mapping"""
        variables = set()
        
        for line in lines:
            i = 0
            while i < len(line):
                if line[i] == '*' and i + 1 < len(line) and (line[i+1].isalnum() or line[i+1] == '_'):
                    end = line.find('*', i + 1)
                    if end != -1:
                        var_name = line[i+1:end]
                        variables.add(var_name)
                        i = end + 1
                    else:
                        break
                else:
                    i += 1
        
        var_map = {}
        short_names = [chr(ord('a') + i) for i in range(26)]
        if len(variables) > 26:
            for i in range(len(variables) - 26):
                short_names.append(f'a{chr(ord("a") + i)}')
        
        for i, var_name in enumerate(sorted(variables)):
            if i < len(short_names):
                var_map[var_name] = short_names[i]
        
        return var_map
    
    @staticmethod
    def _apply_var_map(line: str, var_map: Dict[str, str]) -> str:
        """Apply variable name mapping"""
        if not var_map:
            return line
        
        result = []
        i = 0
        
        while i < len(line):
            if line[i] == '*' and i + 1 < len(line) and (line[i+1].isalnum() or line[i+1] == '_'):
                end = line.find('*', i + 1)
                if end != -1:
                    var_name = line[i+1:end]
                    if var_name in var_map:
                        result.append(f'*{var_map[var_name]}*')
                    else:
                        result.append(line[i:end+1])
                    i = end + 1
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _build_label_map(lines: list) -> Dict[str, str]:
        """Build label name mapping"""
        labels = set()
        
        for line in lines:
            if line.startswith(':') and ':' in line[1:]:
                end = line.find(':', 1)
                if end != -1:
                    label_name = line[1:end]
                    labels.add(label_name)
            
            if 'jmp' in line or 'ask' in line:
                i = 0
                while i < len(line):
                    if line[i] == ':':
                        j = i + 1
                        while j < len(line) and line[j] != ':':
                            j += 1
                        if j < len(line) and line[j] == ':':
                            label_name = line[i+1:j]
                            labels.add(label_name)
                            i = j + 1
                        else:
                            i += 1
                    else:
                        i += 1
        
        label_map = {}
        short_names = [chr(ord('a') + i) for i in range(26)]
        if len(labels) > 26:
            for i in range(len(labels) - 26):
                short_names.append(f'a{chr(ord("a") + i)}')
        
        for i, label_name in enumerate(sorted(labels)):
            if i < len(short_names):
                label_map[label_name] = short_names[i]
        
        return label_map
    
    @staticmethod
    def _apply_label_map(line: str, label_map: Dict[str, str]) -> str:
        """Apply label name mapping"""
        if not label_map:
            return line
        
        result = []
        i = 0
        
        while i < len(line):
            if line[i] == ':':
                j = i + 1
                while j < len(line) and line[j] != ':':
                    j += 1
                if j < len(line) and line[j] == ':':
                    label_name = line[i+1:j]
                    if label_name in label_map:
                        result.append(f':{label_map[label_name]}:')
                    else:
                        result.append(line[i:j+1])
                    i = j + 1
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _eval_constants(line: str) -> str:
        """Evaluate constant expressions"""
        i = 0
        result = []
        
        while i < len(line):
            if line[i] == '(':
                end = WhitVMMinifier._find_matching_paren(line, i)
                if end != -1:
                    expr = line[i:end+1]
                    evaluated = WhitVMMinifier._try_eval_expr(expr)
                    if evaluated is not None:
                        result.append(str(evaluated))
                    else:
                        result.append(expr)
                    i = end + 1
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _find_matching_paren(line: str, start: int) -> int:
        """Find matching closing paren"""
        depth = 1
        i = start + 1
        while i < len(line) and depth > 0:
            if line[i] == '(':
                depth += 1
            elif line[i] == ')':
                depth -= 1
            i += 1
        return i - 1 if depth == 0 else -1
    
    @staticmethod
    def _try_eval_expr(expr: str) -> Any:
        """Try to evaluate expression with only literals"""
        expr = expr[1:-1].strip()
        
        if '*' in expr or 'rng' in expr:
            return None
        
        try:
            result = eval(expr)
            if isinstance(result, bool):
                return 1 if result else 0
            if isinstance(result, float):
                return int(result)
            return result
        except:
            return None
    
    @staticmethod
    def _simplify_expression(line: str) -> str:
        """Simplify nested expressions"""
        result = []
        i = 0
        
        while i < len(line):
            if line[i] == '(':
                end = WhitVMMinifier._find_matching_paren(line, i)
                if end != -1:
                    expr = line[i:end+1]
                    simplified = WhitVMMinifier._simplify_single_expr(expr)
                    result.append(simplified)
                    i = end + 1
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _simplify_single_expr(expr: str) -> str:
        """Simplify single expression by removing unnecessary parens"""
        if not expr.startswith('(') or not expr.endswith(')'):
            return expr
        
        inner = expr[1:-1].strip()
        depth = 0
        has_operators = False
        
        for char in inner:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char in '+-*/%<>=!' and depth == 0:
                has_operators = True
                break
        
        if depth == 0 and not has_operators and inner.startswith('(') and inner.endswith(')'):
            return WhitVMMinifier._simplify_single_expr(inner)
        
        return expr
    
    @staticmethod
    def _build_string_map(lines: list) -> Dict[str, str]:
        """Build string pooling map"""
        string_counts = {}
        
        for line in lines:
            i = 0
            while i < len(line):
                if line[i] == '#':
                    end = line.find('#', i + 1)
                    if end != -1:
                        string_val = line[i:end+1]
                        string_counts[string_val] = string_counts.get(string_val, 0) + 1
                        i = end + 1
                    else:
                        break
                else:
                    i += 1
        
        string_map = {}
        short_names = [chr(ord('s') + i) for i in range(26)]
        idx = 0
        
        for string_val in sorted(string_counts.keys()):
            if string_counts[string_val] >= 2 and idx < len(short_names):
                string_map[string_val] = short_names[idx]
                idx += 1
        
        return string_map
    
    @staticmethod
    def _apply_string_map(line: str, string_map: Dict[str, str]) -> str:
        """Apply string pooling"""
        if not string_map:
            return line
        
        result = []
        i = 0
        
        while i < len(line):
            if line[i] == '#':
                end = line.find('#', i + 1)
                if end != -1:
                    string_val = line[i:end+1]
                    if string_val in string_map:
                        result.append(f'*{string_map[string_val]}*')
                    else:
                        result.append(string_val)
                    i = end + 1
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _create_string_setup(string_map: Dict[str, str]) -> list:
        """Create set instructions for pooled strings"""
        setup = []
        for string_val in sorted(string_map.keys()):
            var_name = string_map[string_val]
            setup.append(f'set *{var_name}* {string_val}')
        return setup
    
    @staticmethod
    def _remove_dead_code(lines: list) -> list:
        """Remove unused variables"""
        set_vars = {}
        for i, line in enumerate(lines):
            tokens = MinifierCore._extract_tokens(line)
            if tokens and tokens[0] == 'set' and len(tokens) >= 3:
                var_name = tokens[1]
                if var_name.startswith('*') and var_name.endswith('*'):
                    var_name = var_name[1:-1]
                    set_vars[var_name] = i
        
        used_vars = set()
        for i, line in enumerate(lines):
            tokens = MinifierCore._extract_tokens(line)
            skip_first_var = (tokens and tokens[0] == 'set' and len(tokens) >= 2)
            
            j = 0
            var_count = 0
            while j < len(line):
                if line[j] == '*' and j + 1 < len(line) and (line[j+1].isalnum() or line[j+1] == '_'):
                    end = line.find('*', j + 1)
                    if end != -1:
                        var_name = line[j+1:end]
                        if not (skip_first_var and var_count == 0):
                            used_vars.add(var_name)
                        var_count += 1
                        j = end + 1
                    else:
                        break
                else:
                    j += 1
        
        result = []
        for i, line in enumerate(lines):
            tokens = MinifierCore._extract_tokens(line)
            if tokens and tokens[0] == 'set' and len(tokens) >= 3:
                var_name = tokens[1]
                if var_name.startswith('*') and var_name.endswith('*'):
                    var_name = var_name[1:-1]
                    if var_name in used_vars:
                        result.append(line)
                else:
                    result.append(line)
            else:
                result.append(line)
        
        return result
    
    @staticmethod
    def _remove_unreachable_code(lines: list) -> list:
        """Remove unreachable code after halt/jmp, respecting ask dispatch"""
        ask_dispatch_ranges = set()
        for i in range(len(lines)):
            tokens = MinifierCore._extract_tokens(lines[i])
            if tokens and tokens[0] == 'ask' and len(tokens) >= 2:
                try:
                    n = int(tokens[1])
                    for j in range(i + 1, min(i + 1 + n, len(lines))):
                        ask_dispatch_ranges.add(j)
                except (ValueError, IndexError):
                    pass
        
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            is_label = line.startswith(':') and ':' in line[1:]
            
            if is_label:
                result.append(line)
                i += 1
                continue
            
            result.append(line)
            
            if i not in ask_dispatch_ranges:
                tokens = MinifierCore._extract_tokens(line)
                
                if tokens and tokens[0] == 'halt' and (len(tokens) < 2 or tokens[-1] == '1'):
                    i += 1
                    while i < len(lines):
                        if lines[i].startswith(':') and ':' in lines[i][1:]:
                            break
                        i += 1
                    continue
                
                elif tokens and tokens[0] == 'jmp' and (len(tokens) < 3 or tokens[-1] == '1'):
                    i += 1
                    while i < len(lines):
                        if lines[i].startswith(':') and ':' in lines[i][1:]:
                            break
                        if i in ask_dispatch_ranges:
                            break
                        i += 1
                    continue
            
            i += 1
        
        return result
    
    @staticmethod
    def minify_file(filepath: Union[str, Path], **kwargs) -> str:
        """Minify a .whitvm file"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if filepath.suffix != '.whitvm':
            raise ValueError(f"Expected .whitvm file, got {filepath.suffix}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        return WhitVMMinifier.minify(code, **kwargs)
    
    @staticmethod
    def minify_to_file(input_file: Union[str, Path], output_file: Union[str, Path], **kwargs) -> None:
        """Minify a file and write to output"""
        minified = WhitVMMinifier.minify_file(input_file, **kwargs)
        
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(minified)


def main():
    """CLI"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m whitvm.minifier <input.whitvm> [output.whitvm]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        minified = WhitVMMinifier.minify_file(input_file)
        
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
            WhitVMMinifier.minify_to_file(input_file, output_file)
            print(f"Minified: {input_file} -> {output_file}")
        else:
            print(minified)
    
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
