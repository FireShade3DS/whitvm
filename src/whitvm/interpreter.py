#!/usr/bin/env python3
"""
WhitVM Interpreter - Execute scripts as defined in isa.md
"""

import re
import random
from typing import Dict, Any, List, Tuple, Optional


class Parser:
    def __init__(self, code: str):
        self.lines = code.strip().split('\n')
        self.labels: Dict[str, int] = {}  # label_name -> instruction index
        self.instructions: List[List[str]] = []
        self.parse()
    
    def parse(self):
        """Parse labels and instructions"""
        instr_idx = 0
        
        for line in self.lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Check for label declaration (standalone line starting with :)
            if line.startswith(':') and line.endswith(':'):
                label_name = line[1:-1]
                self.labels[label_name] = instr_idx
                continue
            
            # Parse instruction
            tokens = self._tokenize(line)
            if tokens:
                self.instructions.append(tokens)
                instr_idx += 1
    
    def _tokenize(self, line: str) -> List[str]:
        """Tokenize a line into instruction tokens"""
        tokens = []
        i = 0
        while i < len(line):
            if line[i].isspace():
                i += 1
                continue
            
            # String literal
            if line[i] == '#':
                end = line.find('#', i + 1)
                if end != -1:
                    tokens.append(line[i:end+1])
                    i = end + 1
                else:
                    raise ValueError(f"Unclosed string literal: {line}")
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
            # Label reference (e.g., :label_name:)
            elif line[i] == ':':
                j = i + 1
                while j < len(line) and line[j] != ':':
                    j += 1
                if j < len(line) and line[j] == ':':
                    tokens.append(line[i:j+1])
                    i = j + 1
                else:
                    raise ValueError(f"Unclosed label reference: {line}")
            # Variable
            elif line[i] == '*':
                end = line.find('*', i + 1)
                if end != -1:
                    tokens.append(line[i:end+1])
                    i = end + 1
                else:
                    raise ValueError(f"Unclosed variable: {line}")
            # Number or opcode
            else:
                j = i
                while j < len(line) and not line[j].isspace() and line[j] not in '()#*:':
                    j += 1
                tokens.append(line[i:j])
                i = j
        
        return tokens


class Interpreter:
    def __init__(self):
        self.dmem: Dict[str, Any] = {}  # Data memory
        self.pc = 0  # Program counter
        self.instructions: List[List[str]] = []
        self.labels: Dict[str, int] = {}
    
    def load(self, code: str):
        """Load and parse assembly code"""
        parser = Parser(code)
        self.instructions = parser.instructions
        self.labels = parser.labels
        self.pc = 0
    
    def load_file(self, filepath: str):
        """Load and parse a .whitvm file"""
        from .loader import WhitVMLoader
        code = WhitVMLoader.load_file(filepath)
        self.load(code)
    
    def run(self):
        """Execute the loaded program"""
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            opcode = instr[0]
            
            if opcode == 'say':
                self._exec_say(instr[1:])
            elif opcode == 'ask':
                self._exec_ask(instr[1:])
            elif opcode == 'jmp':
                self._exec_jmp(instr[1:])
            elif opcode == 'set':
                self._exec_set(instr[1:])
            elif opcode == 'halt':
                if self._exec_halt(instr[1:]):
                    break
            else:
                raise ValueError(f"Unknown opcode: {opcode}")
            
            self.pc += 1
    
    def _get_value(self, arg: str) -> Any:
        """Resolve a value: variable, string, number, or expression"""
        arg = arg.strip()
        
        # String literal
        if arg.startswith('#') and arg.endswith('#'):
            return arg[1:-1]
        
        # Variable
        if arg.startswith('*') and arg.endswith('*'):
            var_name = arg[1:-1]
            if var_name not in self.dmem:
                raise ValueError(f"Undefined variable: {var_name}")
            return self.dmem[var_name]
        
        # Expression
        if arg.startswith('(') and arg.endswith(')'):
            return self._eval_expr(arg)
        
        # Number
        try:
            return int(arg)
        except ValueError:
            raise ValueError(f"Invalid value: {arg}")
    
    def _eval_expr(self, expr: str) -> Any:
        """Evaluate an expression with full operator support.
        
        Operators (by precedence, highest to lowest):
        - Multiplication/Division/Modulo: *, /, %
        - Addition/Subtraction: +, -
        - Comparison: ==, !=, <, >, <=, >=
        
        Returns numeric result for arithmetic, 1/0 for comparisons.
        """
        expr = expr[1:-1].strip()  # Remove outer parentheses
        
        # Tokenize expression
        tokens = self._tokenize_expr(expr)
        
        # Evaluate using tokens
        return self._eval_tokens(tokens)
    
    def _tokenize_expr(self, expr: str) -> List[Any]:
        """Tokenize an expression into values and operators"""
        tokens = []
        i = 0
        
        while i < len(expr):
            # Skip whitespace
            while i < len(expr) and expr[i].isspace():
                i += 1
            if i >= len(expr):
                break
            
            # String literal
            if expr[i] == '#':
                end = expr.find('#', i + 1)
                if end != -1:
                    tokens.append(expr[i:end+1])
                    i = end + 1
                else:
                    raise ValueError(f"Unclosed string literal at {i}")
            # Variable (look for matching *) - only if followed by alphanumeric
            elif expr[i] == '*' and i + 1 < len(expr) and (expr[i+1].isalnum() or expr[i+1] == '_'):
                end = expr.find('*', i + 1)
                if end != -1:
                    tokens.append(expr[i:end+1])
                    i = end + 1
                else:
                    raise ValueError(f"Unclosed variable at {i}")
            # Otherwise it's an operator
            elif expr[i] == '*':
                tokens.append('*')
                i += 1
            # Expression
            elif expr[i] == '(':
                depth = 1
                j = i + 1
                while j < len(expr) and depth > 0:
                    if expr[j] == '(':
                        depth += 1
                    elif expr[j] == ')':
                        depth -= 1
                    j += 1
                tokens.append(expr[i:j])
                i = j
            # Closing paren (shouldn't happen in well-formed expressions)
            elif expr[i] == ')':
                i += 1  # Skip it
            # Operators
            elif expr[i:i+2] in ['==', '!=', '<=', '>=']:
                tokens.append(expr[i:i+2])
                i += 2
            elif expr[i] in '+-*/%<>':
                tokens.append(expr[i])
                i += 1
            # Function call (rng) or number/identifier
            else:
                j = i
                while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                    j += 1
                if j > i:
                    func_name = expr[i:j]
                    # Check if it's a function call
                    if func_name == 'rng':
                        # Look for rng min max pattern
                        k = j
                        while k < len(expr) and expr[k].isspace():
                            k += 1
                        # Collect min and max arguments
                        min_start = k
                        while k < len(expr) and not expr[k].isspace() and expr[k] not in '()':
                            k += 1
                        min_val = expr[min_start:k]
                        
                        while k < len(expr) and expr[k].isspace():
                            k += 1
                        
                        max_start = k
                        while k < len(expr) and not expr[k].isspace() and expr[k] not in '()':
                            k += 1
                        max_val = expr[max_start:k]
                        
                        tokens.append(('rng', min_val, max_val))
                        i = k
                    else:
                        tokens.append(func_name)
                        i = j
                else:
                    raise ValueError(f"Unexpected character at {i}: {expr[i]}")
        
        return tokens
    
    def _eval_tokens(self, tokens: List[Any]) -> Any:
        """Evaluate tokenized expression"""
        # Handle comparison operators first
        for i, tok in enumerate(tokens):
            if tok in ['==', '!=', '<=', '>=', '<', '>']:
                left_tokens = tokens[:i]
                right_tokens = tokens[i+1:]
                left_val = self._eval_tokens(left_tokens)
                right_val = self._eval_tokens(right_tokens)
                
                if tok == '==':
                    return 1 if left_val == right_val else 0
                elif tok == '!=':
                    return 1 if left_val != right_val else 0
                elif tok == '<':
                    return 1 if left_val < right_val else 0
                elif tok == '>':
                    return 1 if left_val > right_val else 0
                elif tok == '<=':
                    return 1 if left_val <= right_val else 0
                elif tok == '>=':
                    return 1 if left_val >= right_val else 0
        
        # Handle + and - (lower precedence)
        for i in range(len(tokens) - 1, -1, -1):  # Right to left
            tok = tokens[i]
            if tok in ['+', '-']:
                left_tokens = tokens[:i]
                right_tokens = tokens[i+1:]
                left_val = self._eval_tokens(left_tokens)
                right_val = self._eval_tokens(right_tokens)
                
                if tok == '+':
                    return left_val + right_val
                else:
                    return left_val - right_val
        
        # Handle * / and % (higher precedence)
        for i in range(len(tokens) - 1, -1, -1):  # Right to left
            tok = tokens[i]
            if tok in ['*', '/', '%']:
                left_tokens = tokens[:i]
                right_tokens = tokens[i+1:]
                left_val = self._eval_tokens(left_tokens)
                right_val = self._eval_tokens(right_tokens)
                
                if tok == '*':
                    return left_val * right_val
                elif tok == '/':
                    return int(left_val / right_val)
                else:
                    return left_val % right_val
        
        # Single token - evaluate it
        if len(tokens) == 1:
            tok = tokens[0]
            # Handle rng function
            if isinstance(tok, tuple) and tok[0] == 'rng':
                min_val = self._get_value(tok[1])
                max_val = self._get_value(tok[2])
                return random.randint(int(min_val), int(max_val))
            elif tok.startswith('(') and tok.endswith(')'):
                return self._eval_expr(tok)
            else:
                return self._get_value(tok)
        
        raise ValueError(f"Unable to evaluate tokens: {tokens}")
    
    def _exec_say(self, args: List[str]):
        """say value [nl_qty] [condition]
        
        Prints value to stdout. nl_qty specifies number of newlines (default: 1).
        Executes if condition is non-zero (default: 1).
        """
        if not args:
            raise ValueError("say requires at least 1 argument")
        
        out = self._get_value(args[0])
        nl_qty = 1
        cond = 1
        
        if len(args) > 1:
            nl_qty = self._get_value(args[1])
        if len(args) > 2:
            cond = self._get_value(args[2])
        
        if cond != 0:
            print(str(out), end='\n' * nl_qty)
    
    def _exec_ask(self, args: List[str]):
        """ask n [condition]
        
        Prompts for user input (integer 1 to n). Jumps PC forward by (input - 1)
        instructions if condition is non-zero (default: 1).
        Out-of-range input defaults to option 1 (no jump).
        If condition is zero (disabled), skips all n option jumps.
        """
        if not args:
            raise ValueError("ask requires at least 1 argument")
        
        n = self._get_value(args[0])
        cond = 1
        
        if len(args) > 1:
            cond = self._get_value(args[1])
        
        if cond != 0:
            user_input = int(input())
            if 1 <= user_input <= n:
                # PC jumps such that the user's chosen option is executed
                # Option 1: execute next instruction (add 0)
                # Option 2: skip 1, execute 2nd instruction after ask (add 1)
                # etc.
                self.pc += user_input - 1
        else:
            # Condition is 0 (disabled), skip all n option jumps
            self.pc += n
    
    def _exec_jmp(self, args: List[str]):
        """jmp :label: [condition]
        
        Jumps PC to :label: if condition is non-zero (default: 1).
        Raises error if label is undefined.
        """
        if not args:
            raise ValueError("jmp requires at least 1 argument")
        
        label_arg = args[0]
        cond = 1
        
        # Extract label name (remove colons)
        if label_arg.startswith(':') and label_arg.endswith(':'):
            label = label_arg[1:-1]
        else:
            label = label_arg
        
        if len(args) > 1:
            cond = self._get_value(args[1])
        
        if cond != 0:
            if label not in self.labels:
                raise ValueError(f"Undefined label: {label}")
            self.pc = self.labels[label] - 1  # -1 because pc will be incremented
    
    def _exec_set(self, args: List[str]):
        """set *var* value
        
        Assigns value to variable *var* in data memory.
        Value can be number, string, variable reference, or expression.
        """
        if len(args) < 2:
            raise ValueError("set requires 2 arguments")
        
        var_name = args[0]
        if not (var_name.startswith('*') and var_name.endswith('*')):
            raise ValueError(f"First argument to set must be a variable")
        
        var_name = var_name[1:-1]
        value = self._get_value(args[1])
        self.dmem[var_name] = value
    
    def _exec_halt(self, args: List[str]):
        """halt [condition]
        
        Halts program execution if condition is non-zero (default: 1).
        The break in run() will stop execution.
        """
        cond = 1
        
        if len(args) > 0:
            cond = self._get_value(args[0])
        
        # Only return True to halt if condition is non-zero
        return cond != 0


def main():
    # Example program
    program = """
:start_screen:
    set *player_gender* #Undef#
    set *nl_single* 1
    set *msg_prompt* #Please select your character's gender (1-Male, 2-Female):#
    set *msg_male_intro* #You are a strong male hero.#
    set *msg_female_intro* #You are a graceful female heroine.#
    
    say *msg_prompt* *nl_single* 1
    ask 2

    jmp :male_selection:
    jmp :female_selection:

:male_selection:
    set *player_gender* #Male#
    jmp :intro_scene:

:female_selection:
    set *player_gender* #Female#
    jmp :intro_scene:

:intro_scene:
    say #You selected: # *nl_single* 1
    say *player_gender* *nl_single* 1

    jmp :male_story_branch: (*player_gender* == #Male#)
    jmp :female_story_branch: (*player_gender* == #Female#)

:male_story_branch:
    say *msg_male_intro* *nl_single* 1
    jmp :program_end:

:female_story_branch:
    say *msg_female_intro* *nl_single* 1
    jmp :program_end:

:program_end:
    say #The adventure begins!# 1 1
"""
    
    interp = Interpreter()
    interp.load(program)
    interp.run()


if __name__ == '__main__':
    main()
