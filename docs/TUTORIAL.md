# WhitVM Game Development Tutorial

Welcome to WhitVM! This guide will teach you how to create interactive text adventure games.

## Table of Contents

1. [Installation](#installation)
2. [Your First Game](#your-first-game)
3. [Basic Syntax](#basic-syntax)
4. [Building Choices](#building-choices)
5. [Game Variables](#game-variables)
6. [Advanced Features](#advanced-features)
7. [Tips & Tricks](#tips--tricks)

## Installation

```bash
pip install -e .
# or
pipx install .
```

## Your First Game

Create a new game:

```bash
whitvm new HelloWorld --template blank
cd HelloWorld
```

Edit HelloWorld.whitvm:

```whitvm
:start:
    say #Hello, adventurer!# 1 1
    say #Welcome to WhitVM.# 1 1
```

Run it:

```bash
whitvm run HelloWorld.whitvm
```

You should see:
```
Hello, adventurer!
Welcome to WhitVM.
```

## Basic Syntax

### Labels (Story Checkpoints)

Labels mark locations in your game that you can jump to:

```whitvm
:start:
    say #You're at the start!# 1 1

:ending:
    say #Game over!# 1 1
    halt
```

### Say (Print Text)

Output text to the player:

```whitvm
say #Hello World# 1 1
```

Format: `say value [newlines] [condition]`

- `value`: Text (#...#), variable (*...*), number, or expression
- `newlines`: How many line breaks after (default: 1)
- `condition`: Execute only if true (default: 1, always execute)

Examples:

```whitvm
say #Text# 1 1              # Print with 1 newline
say #Text# 2 1              # Print with 2 newlines
say #Text# 0 1              # Print with 0 newlines (no break)
say #Debug# 1 0             # Hidden comment (condition=0, never prints)
```

### Halt (End Game)

Stop execution:

```whitvm
:ending:
    say #Thanks for playing!# 1 1
    halt
```

## Building Choices

### Ask (Get Player Input)

Prompt the player for a choice:

```whitvm
:start:
    say #What do you do?# 1 1
    say #1) Go left  2) Go right# 1 1
    ask 2
    
    jmp :left_path:
    jmp :right_path:

:left_path:
    say #You went left!# 1 1
    halt

:right_path:
    say #You went right!# 1 1
    halt
```

Format: `ask n [condition]`

- `n`: Number of options (1 to n)
- Each `jmp` after `ask` is a possible choice
- If player chooses option 1, execute the 1st jmp
- If player chooses option 2, execute the 2nd jmp

### Jump (Go to Label)

Jump to a label:

```whitvm
jmp :label_name:
```

Can be conditional:

```whitvm
jmp :end: (*health* <= 0)  # Jump only if health is 0 or less
```

## Game Variables

Store information:

```whitvm
set *health* 100
set *name* #Hero#
set *gold* 0
```

Format: `set *variable_name* value`

Use variables:

```whitvm
set *health* 100
say *health* 1 1            # Prints: 100
set *health* ((*health*) - 10)
say *health* 1 1            # Prints: 90
```

### Example: Health System

```whitvm
:start:
    set *health* 100
    set *gold* 0
    jmp :main_menu:

:main_menu:
    say #=== ADVENTURE ===#  2 1
    say #Health: # 0 1
    say *health* 1 1
    say #Gold: # 0 1
    say *gold* 1 1
    say #What do you do?# 1 1
    say #1) Fight  2) Rest  3) Quit# 1 1
    ask 3
    
    jmp :fight:
    jmp :rest:
    jmp :quit:

:fight:
    say #You fought a monster!# 1 1
    set *health* ((*health*) - 20)
    set *gold* ((*gold*) + 50)
    jmp :main_menu:

:rest:
    say #You rest and recover.# 1 1
    set *health* 100
    jmp :main_menu:

:quit:
    say #You return home with # 0 1
    say *gold* 1 1
    say # gold.# 1 1
    halt
```

## Advanced Features

### Expressions

Perform calculations:

```whitvm
set *result* ((5 + 3))       # 8
set *result* ((10 - 2))      # 8
set *result* ((4 * 3))       # 12
set *result* ((20 / 4))      # 5
set *result* ((10 % 3))      # 1 (modulo)
```

Operator precedence (highest to lowest):
1. `*`, `/`, `%` (multiplication, division, modulo)
2. `+`, `-` (addition, subtraction)
3. `==`, `!=`, `<`, `>`, `<=`, `>=` (comparisons)

### Comparisons

Compare values:

```whitvm
set *health* 50

say #You're alive!# 1 1 ((*health*) > 0)      # Execute if true
say #You're dead!# 1 1 ((*health*) <= 0)      # Execute if true
say #You're healthy!# 1 1 ((*health*) >= 100) # Execute if true
```

Comparison result is 1 (true) or 0 (false):

```whitvm
set *is_alive* ((*health*) > 0)
say *is_alive* 1 1  # Prints: 1 or 0
```

### Random Numbers

Generate random values:

```whitvm
set *roll* (rng 1 6)        # Random number 1-6 (like a die roll)
say #You rolled: # 0 1
say *roll* 1 1
```

### Loops

Repeat sections:

```whitvm
set *count* 0

:loop:
    say *count* 1 1
    set *count* ((*count*) + 1)
    jmp :loop: ((*count*) < 10)  # Loop while count < 10

say #Done!# 1 1
```

### String Concatenation

Combine strings (print multiple times):

```whitvm
set *name* #Hero#
say #Welcome, # 0 1    # Print without newline
say *name* 0 1         # Continue same line
say #!# 1 1            # End with newline

# Output: Welcome, Hero!
```

## Tips & Tricks

### Tip 1: Hide Comments

Comments in WhitVM use the condition=0 pattern:

```whitvm
say #This is a hidden comment# 1 0
say #Another note for developers# 1 0
```

### Tip 2: Validate Before Running

Check your game for syntax errors:

```bash
whitvm check game.whitvm
```

### Tip 3: Minify for Release

Reduce file size:

```bash
whitvm minify game.whitvm -o game.min.whitvm
```

This shrinks variable names, removes comments, and optimizes code.

### Tip 4: Multi-Choice Chains

For more than 2-3 choices, use nested choices:

```whitvm
ask 3

jmp :path_1:
jmp :path_2_3:
jmp :path_other:

:path_2_3:
    say #Choose again!# 1 1
    say #2a or 2b?# 1 1
    ask 2
    
    jmp :path_2a:
    jmp :path_2b:
```

### Tip 5: Test as You Build

Keep test games small and run them frequently:

```bash
# Quick test
whitvm run test.whitvm
```

### Tip 6: Use Meaningful Variable Names

In development, use clear names:

```whitvm
set *player_health* 100
set *monster_health* 50
set *current_room* #forest#
```

Then minify for release:

```bash
whitvm minify game.whitvm
```

### Tip 7: Structure with Labels

Organize your game:

```whitvm
:start:
    # Initialization
    set *health* 100
    jmp :main:

:main:
    # Main game loop
    jmp :end:

:end:
    # Cleanup/ending
    halt
```

## Example: Complete Dungeon Game

See examples/ directory for more complete games:

```bash
whitvm run examples/dungeon_crawler/game.whitvm
```

## Need Help?

- Check syntax: `whitvm check game.whitvm`
- View help: `whitvm --help`
- Read full ISA: `docs/isa.md`
- See examples: `examples/` directory

Happy game making!
