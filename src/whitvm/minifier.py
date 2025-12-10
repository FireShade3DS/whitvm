#!/usr/bin/env python3
"""
WhitVM Minifier - Remove comments, whitespace, and optimize .whitvm files
"""

import re
import random
from pathlib import Path
from typing import Union, Dict, Any


class WhitVMMinifier:
    """Minify WhitVM code by removing comments and unnecessary whitespace"""
    
    @staticmethod
    def minify(code: str, shrink_vars: bool = True, shrink_labels: bool = True, 
               eval_const: bool = True, remove_defaults: bool = True, pool_strings: bool = True,
               dead_code: bool = True, simplify_expr: bool = True, remove_unused_jumps: bool = True,
               remove_unreachable: bool = True) -> str:
        """Minify WhitVM code
        
        Removes:
        - Comment lines (say ... 1 0)
        - Blank lines
        - Leading/trailing whitespace on each line
        - Default arguments (say ... 1 1 → say ...)
        - Whitespace between tokens
        - Unused jumps (jumps to next instruction)
        
        Optionally:
        - Shrink variable names (*player_health* → *a*, *count* → *b*, etc.)
        - Shrink label names (:main_loop: → :a:, :check_health: → :b:, etc.)
        - Evaluate constant expressions at compile time
        - Pool repeated strings into variables (#text# → *s* where *s* = #text#)
        - Simplify expressions (remove nested parentheses)
        - Remove unused jumps
        - Remove unreachable code (after halt/unconditional jumps)
        
        Args:
            code: WhitVM source code
            shrink_vars: Rename variables to shorter names
            shrink_labels: Rename labels to shorter names
            eval_const: Evaluate constant expressions
            remove_defaults: Remove default arguments (1 1 from say)
            pool_strings: Extract repeated strings into variables
            dead_code: Remove unused variables (set but never used)
            simplify_expr: Simplify expressions by removing unnecessary parentheses
            remove_unused_jumps: Remove jumps that target the next instruction
            remove_unreachable: Remove unreachable code after halt/unconditional jumps
            
        Returns:
            Minified code
        """
        lines = code.strip().split('\n')
        
        # First pass: remove comments and blank lines
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line or WhitVMMinifier._is_comment_line(line):
                continue
            cleaned_lines.append(line)
        
        # Second pass: label shrinking
        label_map = {}
        if shrink_labels:
            label_map = WhitVMMinifier._build_label_map(cleaned_lines)
            cleaned_lines = [WhitVMMinifier._apply_label_map(line, label_map) for line in cleaned_lines]
        
        # Third pass: variable shrinking
        var_map = {}
        if shrink_vars:
            var_map = WhitVMMinifier._build_var_map(cleaned_lines)
            cleaned_lines = [WhitVMMinifier._apply_var_map(line, var_map) for line in cleaned_lines]
        
        # Fourth pass: constant expression evaluation
        if eval_const:
            cleaned_lines = [WhitVMMinifier._eval_constants(line) for line in cleaned_lines]
        
        # Fifth pass: expression simplification
        if simplify_expr:
            cleaned_lines = [WhitVMMinifier._simplify_expression(line) for line in cleaned_lines]
        
        # Sixth pass: remove default arguments
        if remove_defaults:
            cleaned_lines = [WhitVMMinifier._remove_defaults(line) for line in cleaned_lines]
        
        # Seventh pass: string pooling
        string_map = {}
        if pool_strings:
            string_map = WhitVMMinifier._build_string_map(cleaned_lines)
            cleaned_lines = [WhitVMMinifier._apply_string_map(line, string_map) for line in cleaned_lines]
            # Add set instructions for string variables at the beginning (after labels)
            setup_lines = WhitVMMinifier._create_string_setup(string_map)
            cleaned_lines = setup_lines + cleaned_lines
        
        # Eighth pass: dead code elimination (remove unused variables)
        if dead_code:
            cleaned_lines = WhitVMMinifier._remove_dead_code(cleaned_lines)
        
        # Ninth pass: remove unused jumps
        if remove_unused_jumps:
            cleaned_lines = WhitVMMinifier._remove_unused_jumps(cleaned_lines)
        
        # Tenth pass: remove unreachable code
        if remove_unreachable:
            cleaned_lines = WhitVMMinifier._remove_unreachable_code(cleaned_lines)
        
        # Eleventh pass: compact spacing (remove extra spaces)
        cleaned_lines = [WhitVMMinifier._compact_spacing(line) for line in cleaned_lines]
        
        return '\n'.join(cleaned_lines)
    
    @staticmethod
    def _build_label_map(lines: list) -> Dict[str, str]:
        """Build a mapping of label names to shorter names
        
        Collects all labels and assigns them short names (a, b, c, etc.)
        """
        labels = set()
        
        for line in lines:
            # Find label declarations (lines starting with :)
            if line.startswith(':') and ':' in line[1:]:
                end = line.find(':', 1)
                if end != -1:
                    label_name = line[1:end]
                    labels.add(label_name)
            
            # Find label references in jmp instructions
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
        
        # Create mapping: long names to short names
        label_map = {}
        short_names = [chr(ord('a') + i) for i in range(26)]  # a-z
        
        # Add more names if needed: aa, ab, ac, etc.
        if len(labels) > 26:
            for i in range(len(labels) - 26):
                short_names.append(f'a{chr(ord("a") + i)}')
        
        for i, label_name in enumerate(sorted(labels)):
            if i < len(short_names):
                label_map[label_name] = short_names[i]
        
        return label_map
    
    @staticmethod
    def _apply_label_map(line: str, label_map: Dict[str, str]) -> str:
        """Replace label names with shortened versions"""
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
    def _build_var_map(lines: list) -> Dict[str, str]:
        """Build a mapping of variable names to shorter names
        
        Collects all variables and assigns them short names (a, b, c, etc.)
        """
        variables = set()
        
        for line in lines:
            # Find all variables in the line
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
        
        # Create mapping: long names to short names
        var_map = {}
        short_names = [chr(ord('a') + i) for i in range(26)]  # a-z
        
        # Add more names if needed: aa, ab, ac, etc.
        if len(variables) > 26:
            for i in range(len(variables) - 26):
                short_names.append(f'a{chr(ord("a") + i)}')
        
        for i, var_name in enumerate(sorted(variables)):
            if i < len(short_names):
                var_map[var_name] = short_names[i]
        
        return var_map
    
    @staticmethod
    def _apply_var_map(line: str, var_map: Dict[str, str]) -> str:
        """Replace variable names with shortened versions"""
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
    def _eval_constants(line: str) -> str:
        """Evaluate constant expressions (expressions with only literals)
        
        E.g., (5 + 3) → 8, (10 / 2) → 5
        """
        # Find expressions in parentheses
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
        """Find the closing parenthesis matching the one at start"""
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
        """Try to evaluate an expression with only literal values
        
        Returns the result if successful, None if expression contains variables
        """
        expr = expr[1:-1].strip()  # Remove parens
        
        # Check if expression contains variables
        if '*' in expr:
            return None
        
        # Check if expression contains function calls (rng)
        if 'rng' in expr:
            return None
        
        # Try to evaluate
        try:
            # Replace operators with Python equivalents
            expr_py = expr.replace('%', '%')  # modulo stays same
            expr_py = expr_py.replace('==', '==')  # equals stays same
            expr_py = expr_py.replace('!=', '!=')  # not equals stays same
            expr_py = expr_py.replace('<=', '<=')  # less/equal stays same
            expr_py = expr_py.replace('>=', '>=')  # greater/equal stays same
            expr_py = expr_py.replace('<', '<')  # less than stays same
            expr_py = expr_py.replace('>', '>')  # greater than stays same
            
            # Safely evaluate (only numbers and operators)
            result = eval(expr_py)
            
            # For comparison operators, convert 1/0 to int
            if isinstance(result, bool):
                return 1 if result else 0
            
            # For arithmetic, ensure integer
            if isinstance(result, float):
                return int(result)
            
            return result
        except:
            return None
    
    @staticmethod
    def _build_string_map(lines: list) -> Dict[str, str]:
        """Build a map of repeated strings to variable names
        
        Only pools strings that appear more than once (saves space)
        """
        string_counts = {}
        
        for line in lines:
            # Find all strings in the line
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
        
        # Only pool strings that appear 2+ times
        string_map = {}
        short_names = [chr(ord('s') + i) for i in range(26)]  # s-h
        idx = 0
        
        for string_val in sorted(string_counts.keys()):
            if string_counts[string_val] >= 2 and idx < len(short_names):
                string_map[string_val] = short_names[idx]
                idx += 1
        
        return string_map
    
    @staticmethod
    def _apply_string_map(line: str, string_map: Dict[str, str]) -> str:
        """Replace repeated strings with variable references"""
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
        """Remove set statements for variables that are never used
        
        Note: Only removes variables that are set and never referenced.
        Requires forward scanning to identify all uses before optimization.
        """
        # First, find all variables that are set
        set_vars = {}  # var_name -> line_index
        for i, line in enumerate(lines):
            tokens = WhitVMMinifier._extract_tokens(line)
            if tokens and tokens[0] == 'set' and len(tokens) >= 3:
                var_name = tokens[1]
                if var_name.startswith('*') and var_name.endswith('*'):
                    var_name = var_name[1:-1]
                    set_vars[var_name] = i
        
        # Second, find which variables are actually used (including in expressions)
        used_vars = set()
        for i, line in enumerate(lines):
            # Skip the set statement's target variable
            tokens = WhitVMMinifier._extract_tokens(line)
            skip_first_var = (tokens and tokens[0] == 'set' and len(tokens) >= 2)
            
            # Find all variable references in this line
            j = 0
            var_count = 0
            while j < len(line):
                if line[j] == '*' and j + 1 < len(line) and (line[j+1].isalnum() or line[j+1] == '_'):
                    end = line.find('*', j + 1)
                    if end != -1:
                        var_name = line[j+1:end]
                        # Skip first variable in set statements (it's the target, not a use)
                        if not (skip_first_var and var_count == 0):
                            used_vars.add(var_name)
                        var_count += 1
                        j = end + 1
                    else:
                        break
                else:
                    j += 1
        
        # Third, remove lines that set unused variables
        result = []
        for i, line in enumerate(lines):
            tokens = WhitVMMinifier._extract_tokens(line)
            if tokens and tokens[0] == 'set' and len(tokens) >= 3:
                var_name = tokens[1]
                if var_name.startswith('*') and var_name.endswith('*'):
                    var_name = var_name[1:-1]
                    if var_name in used_vars:
                        result.append(line)
                    # else: skip this line (unused variable)
                else:
                    result.append(line)
            else:
                result.append(line)
        
        return result
    
    @staticmethod
    def _simplify_expression(line: str) -> str:
        """Simplify expressions by removing unnecessary nested parentheses
        
        E.g., ((*a*)) → (*a*), ((5)) → 5, ((*a*) + 3) → (*a* + 3)
        """
        result = []
        i = 0
        
        while i < len(line):
            if line[i] == '(':
                # Found an expression, try to simplify it
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
        """Simplify a single expression by removing unnecessary nested parentheses
        
        ((*a*)) → (*a*), but preserve ((*a*) + 3) as is (needed for expression context)
        Only simplify if the entire inner expression is a single variable or literal
        """
        if not expr.startswith('(') or not expr.endswith(')'):
            return expr
        
        # Remove outer parentheses and check if still valid
        inner = expr[1:-1].strip()
        
        # Check if inner is a simple single token (variable, number, or expression)
        # We only simplify ((var)) or ((5)) patterns, not (a + b)
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
        
        # Only remove outer parens if inner is balanced and contains no top-level operators
        if depth == 0 and not has_operators and inner.startswith('(') and inner.endswith(')'):
            # Inner is like ((*a*)), recursively simplify
            return WhitVMMinifier._simplify_single_expr(inner)
        
        return expr
    
    @staticmethod
    def _remove_unused_jumps(lines: list) -> list:
        """Remove jumps that target the next instruction
        
        E.g., if jmp :label: points to the very next instruction, remove it
        """
        # First, build a map of label positions (including label declarations)
        label_positions = {}
        pos = 0
        
        for line in lines:
            # Check if this line is a label declaration
            if line.startswith(':') and ':' in line[1:]:
                end = line.find(':', 1)
                if end != -1:
                    label_name = line[1:end]
                    label_positions[label_name] = pos
            pos += 1
        
        # Second pass: remove jumps to next instruction
        result = []
        for i, line in enumerate(lines):
            tokens = WhitVMMinifier._extract_tokens(line)
            
            # Check if it's a jump instruction
            if tokens and tokens[0] in ('jmp', 'ask') and len(tokens) >= 2:
                # Extract label from jmp/ask
                label_ref = tokens[1]
                if label_ref.startswith(':') and label_ref.endswith(':'):
                    label_name = label_ref[1:-1]
                    
                    # Check if label points to next instruction
                    if label_name in label_positions:
                        target_pos = label_positions[label_name]
                        next_pos = i + 1
                        
                        # Only remove unconditional jumps to next position
                        if target_pos == next_pos and (len(tokens) < 3 or tokens[-1] == '1'):
                            # This jump is redundant, skip it
                            continue
            
            result.append(line)
        
        return result
    
    @staticmethod
    def _remove_unreachable_code(lines: list) -> list:
        """Remove code that cannot be reached
        
        Removes lines after:
        - halt (unconditional termination)
        - jmp :label: (unconditional jump, unless followed by label)
        - ask (unconditional branch)
        
        But preserves labels that might be jump targets
        """
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            tokens = WhitVMMinifier._extract_tokens(line)
            
            # Check if line is a label
            is_label = line.startswith(':') and ':' in line[1:]
            
            if is_label:
                # Always keep labels
                result.append(line)
                i += 1
                continue
            
            result.append(line)
            
            # Check if this instruction is unconditional termination
            if tokens:
                opcode = tokens[0]
                
                # Unconditional halt
                if opcode == 'halt' and (len(tokens) < 2 or tokens[-1] == '1'):
                    # Everything after halt (until next label) is unreachable
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        # Keep labels but skip other instructions
                        if next_line.startswith(':') and ':' in next_line[1:]:
                            break
                        i += 1
                    continue
                
                # Unconditional jump
                elif opcode == 'jmp' and (len(tokens) < 3 or tokens[-1] == '1'):
                    # Everything after jmp (until next label) is unreachable
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        # Keep labels but skip other instructions
                        if next_line.startswith(':') and ':' in next_line[1:]:
                            break
                        i += 1
                    continue
            
            i += 1
        
        return result
    
    @staticmethod
    def _compact_spacing(line: str) -> str:
        """Remove extra spaces while preserving token boundaries"""
        tokens = WhitVMMinifier._extract_tokens(line)
        return ' '.join(tokens)
    
    @staticmethod
    def _remove_defaults(line: str) -> str:
        """Remove default arguments from instructions
        
        - say ... 1 1 → say ...
        - say ... X 1 → say ... X (only remove condition if it's 1)
        - jmp ... 1 → jmp ...
        - ask ... 1 → ask ...
        """
        tokens = WhitVMMinifier._extract_tokens(line)
        
        if not tokens:
            return line
        
        opcode = tokens[0]
        
        # Handle say instruction: remove trailing "1 1"
        if opcode == 'say' and len(tokens) >= 3:
            # say value nl_qty condition
            if len(tokens) == 4 and tokens[-2] == '1' and tokens[-1] == '1':
                # say ... 1 1 → say ...
                return ' '.join(tokens[:-2])
            elif len(tokens) == 3 and tokens[-1] == '1':
                # Check if this is say ... 1 (where 1 is the nl_qty/condition)
                # We need context - if only 3 tokens total, last is probably nl_qty with default cond
                # If it ends with just "1", remove it if it's the default condition
                return ' '.join(tokens[:-1])
        
        # Handle jmp instruction: remove trailing "1"
        elif opcode == 'jmp' and len(tokens) >= 2:
            if tokens[-1] == '1':
                return ' '.join(tokens[:-1])
        
        # Handle ask instruction: remove trailing "1"
        elif opcode == 'ask' and len(tokens) >= 2:
            if tokens[-1] == '1':
                return ' '.join(tokens[:-1])
        
        return line
    
    @staticmethod
    def _is_comment_line(line: str) -> bool:
        """Check if a line is a comment (say ... 1 0)
        
        A comment line matches: say <anything> 1 0
        where the last two tokens are "1" and "0"
        """
        # Match: say ... 1 0
        # The pattern checks if it's a say instruction ending with "1 0"
        if not line.startswith('say'):
            return False
        
        # Extract tokens from the line
        tokens = WhitVMMinifier._extract_tokens(line)
        
        # Must have at least 3 tokens: say, value, and the two condition args
        if len(tokens) < 3:
            return False
        
        # Check if last two tokens are "1" and "0"
        return tokens[-2] == '1' and tokens[-1] == '0'
    
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
            # Regular token (number, opcode)
            else:
                j = i
                while j < len(line) and not line[j].isspace() and line[j] not in '()#*:':
                    j += 1
                if j > i:
                    tokens.append(line[i:j])
                i = j
        
        return tokens
    
    @staticmethod
    def minify_file(filepath: Union[str, Path]) -> str:
        """Minify a .whitvm file and return minified code
        
        Args:
            filepath: Path to .whitvm file
            
        Returns:
            Minified code
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if filepath.suffix != '.whitvm':
            raise ValueError(f"Expected .whitvm file, got {filepath.suffix}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        return WhitVMMinifier.minify(code)
    
    @staticmethod
    def minify_to_file(input_file: Union[str, Path], output_file: Union[str, Path]) -> None:
        """Minify a .whitvm file and write to output
        
        Args:
            input_file: Path to input .whitvm file
            output_file: Path to output .whitvm file
        """
        minified = WhitVMMinifier.minify_file(input_file)
        
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(minified)


def main():
    """Command-line interface for minifier"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m whitvm.minifier <input.whitvm> [output.whitvm]")
        print()
        print("If output file is not specified, prints to stdout")
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
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
