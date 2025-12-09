# WhitVM AGENTS.md

## Overview
WhitVM is a Harvard-architecture interpreter for interactive fiction and text adventures. It parses and executes `.whitvm` script files with support for variables, labels, expressions, and control flow.

## Build & Test Commands

```bash
# Install in development mode
python -m pip install -e .

# Run all tests
python -m pytest tests/

# Run single test file
python -m pytest tests/test_interpreter.py

# Run single test function
python -m pytest tests/test_interpreter.py::TestInterpreter::test_simple_say

# Run with verbose output
python -m pytest tests/ -v
```

## Architecture & Structure

**Core Module** (`src/whitvm/`)
- `interpreter.py`: Parser and Interpreter classes (61 tests)
- `loader.py`: File I/O and `.whitvm` validator (11 tests)
- `minifier.py`: Code minification utilities

**Tests** (`tests/`)
- `test_interpreter.py`: Core functionality (variables, expressions, control flow)
- `test_loader.py`: File loading and validation
- `test_*aweosme.py`: Aweosme-complete specification compliance
- `test_truth_machine.py`, `test_madlibs.py`: Example programs

**Examples** (`examples/`)
- `.whitvm` and `.min.whitvm` (minified) files demonstrating language features

**Games** (`games/dungeon_crawler/`)
- Interactive text adventure using WhitVM

## Code Style & Conventions

**Python Style**: Follow Black (100 char line limit) and isort for imports.

**WhitVM Syntax** (`.whitvm` files):
- Labels: `:label_name:` (standalone lines)
- Variables: `*var_name*` (alphanumeric + underscore)
- Strings: `#text content#`
- Expressions: `(expression)` with operators: `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- Operator precedence: `*/%` > `+-` > comparisons
- Comments: `say #text# 1 0` (condition = 0)

**Instructions** (format: `opcode arg1 arg2 ...`):
- `set *var* value`: Assign value (number/string/variable/expression)
- `say value [nl_qty] [condition]`: Print with optional newlines and condition
- `ask n [condition]`: Read input 1-n, jumps forward by (input - 1) instructions
- `jmp :label: [condition]`: Jump to label if condition != 0
- `halt [condition]`: Exit if condition != 0
- All instructions default to condition=1 (execute)

**Error Handling**: 
- Undefined variables/labels raise errors at runtime
- Invalid syntax caught by loader
- Division by zero raises error
- Out-of-range `ask` input defaults to option 1

**Variables**: Must be explicitly initialized with `set` before use.
