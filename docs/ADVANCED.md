# WhitVM Advanced Knowledge

This document covers advanced concepts, internal behavior, and optimization techniques for experienced WhitVM developers.

## Table of Contents

1. [Ask Instruction Deep Dive](#ask-instruction-deep-dive)
2. [Control Flow Patterns](#control-flow-patterns)
3. [Memory and Performance](#memory-and-performance)
4. [Edge Cases and Gotchas](#edge-cases-and-gotchas)
5. [Internal Architecture](#internal-architecture)
6. [Optimization Techniques](#optimization-techniques)

## Ask Instruction Deep Dive

### The Nested If Structure

The `ask` instruction has a **nested conditional structure**:

```
ask n [condition]
├─ if condition == 0 (disabled):
│  └─ skip n instructions (all option jumps)
└─ else (condition != 0, active):
   ├─ read user input
   └─ if 1 <= input <= n (valid):
      └─ jump to that option
      else (invalid input):
         └─ default to option 1 (no jump)
```

### Behavior Breakdown

#### Case 1: Normal Ask (condition=1)
```whitvm
ask 2
jmp :option_a:     # executed if input=1 (no jump)
jmp :option_b:     # executed if input=2 (jump 1)
```

- Input 1 → PC doesn't change → execute `:option_a:`
- Input 2 → PC += 1 → skip `:option_a:`, execute `:option_b:`
- Input 99 → invalid → default to option 1 (execute `:option_a:`)

#### Case 2: Disabled Ask (condition=0)
```whitvm
ask 2 0
jmp :option_a:     # SKIPPED
jmp :option_b:     # SKIPPED
say #Continues here# 1 1
```

When disabled, the instruction **skips forward by `n` positions**, jumping past all option branches entirely. This is useful for conditional questionnaires:

```whitvm
set *is_tutorial* 0

ask 2 (*is_tutorial*)  # Only ask if tutorial mode
jmp :tutorial_1:
jmp :tutorial_2:

say #Tutorial skipped# 1 1
jmp :game_start:

:tutorial_1:
    say #This is the game.# 1 1
    jmp :game_start:

:tutorial_2:
    say #Advanced mode!# 1 1
    
:game_start:
    say #Starting...# 1 1
```

### Why This Design?

The nested structure allows:
1. **Skip all branches**: `ask ... 0` lets you conditionally skip entire choice sections
2. **Graceful defaults**: Invalid input doesn't crash, defaults to first option
3. **Single instruction**: No need for a separate "skip N" instruction
4. **Game-like feel**: Feels natural to players (wrong input = first option)

## Control Flow Patterns

### Nested Choices

For more than 2-3 options, use nested choices:

```whitvm
:main_menu:
    ask 3
    jmp :story:
    jmp :settings:
    jmp :quit:

:settings:
    say #Settings# 1 1
    ask 2
    jmp :difficulty:
    jmp :back:
    
:difficulty:
    # ... more options ...
    jmp :main_menu:

:back:
    jmp :main_menu:

:story:
    # ... story code ...
    halt

:quit:
    say #Goodbye!# 1 1
    halt
```

### Guard Clauses

Use conditional jumps as guards:

```whitvm
:check_alive:
    jmp :dead: ((*health*) <= 0)
    # Player is alive, continue...
    say #You're alive!# 1 1
    halt

:dead:
    say #Game Over!# 1 1
    halt
```

### State Machines

Use variables as state flags:

```whitvm
set *game_state* #start#

:loop:
    jmp :start_scene: (*game_state* == #start#)
    jmp :dungeon: (*game_state* == #dungeon#)
    jmp :boss: (*game_state* == #boss#)
    jmp :ending: (*game_state* == #ending#)

:start_scene:
    say #You begin your adventure...# 1 1
    set *game_state* #dungeon#
    jmp :loop:

:dungeon:
    say #You enter a dungeon.# 1 1
    set *game_state* #boss#
    jmp :loop:

:boss:
    say #FINAL BOSS!# 1 1
    set *game_state* #ending#
    jmp :loop:

:ending:
    say #You won!# 1 1
    halt
```

## Memory and Performance

### Memory Model

WhitVM uses **Harvard Architecture**:
- **IMEM** (Instruction Memory): `.whitvm` code → immutable instructions
- **DMEM** (Data Memory): Variables and state → mutable at runtime

### Variable Scope

All variables are **global**. There are no local scopes:

```whitvm
set *x* 10

:function_a:
    set *x* 20    # Modifies global x
    jmp :function_b:

:function_b:
    say *x* 1 1   # Prints 20 (not 10)
```

To simulate function-local variables, use naming conventions:

```whitvm
set *add_x* 5
set *add_y* 3
jmp :add:

:add:
    set *add_result* ((*add_x*) + (*add_y*))
    # Result is in *add_result*
```

### Performance Notes

- **No function overhead**: All `jmp` is inline, no call stack
- **Minification reduces size 17%+**: Variable/label shrinking, constant folding
- **No garbage collection**: Variables live until program end
- **Linear instruction execution**: O(n) worst case for any program

## Edge Cases and Gotchas

### Gotcha 1: Expressions Need Outer Parentheses

Outer parentheses mark "evaluate this as an expression". Flow is inside-out:

```whitvm
set *x* 5
set *y* 3
set *result* (*x* + *y*)
```

Evaluation (popping bubbles inside-out): `((*x*) + (*y*))` →
1. Pop `(*x*)` → 5
2. Pop `(*y*)` → 3  
3. Pop the `+` with 5 and 3 → 8
4. Return 8

Or simpler `(*x* + *y*)` →
1. Pop `*x*` → 5
2. Pop `*y*` → 3
3. Pop `5 + 3` → 8

Without outer parens:
```whitvm
set *result* *x* + *y*        # ERROR - not recognized as expression
```

### Gotcha 2: String Comparison

Strings are compared lexicographically:

```whitvm
set *name* #alice#
say *name* 1 1 ((*name*) == #alice#)

set *name* #Alice#
say *name* 1 1 ((*name*) == #alice#)
```

First example prints "alice" (condition true).  
Second example prints nothing (case matters - "Alice" != "alice").

### Gotcha 3: Division Rounds Down

Integer division floors, not rounds:

```whitvm
set *result* ((7 / 2))   # 3, not 3.5
set *result* ((10 / 3))  # 3, not 3.33
```

### Gotcha 4: Ask Doesn't Return a Value

You can use a condition with `ask`, but `ask` itself doesn't return a value:

```whitvm
ask 2 ((*x*) > 5)

set *result* (ask 2)
```

The first is VALID - ask conditionally (only if x > 5).  
The second is INVALID - can't store ask's result in a variable.

Ask modifies the program counter directly, it doesn't produce a value.

### Gotcha 5: Infinite Loops

Easy to create accidentally:

```whitvm
:loop:
    say #Looping...# 1 1
    jmp :loop:  # Infinite loop!
```

Always add a break condition:

```whitvm
set *count* 0

:loop:
    say *count* 1 1
    set *count* ((*count*) + 1)
    jmp :loop: ((*count*) < 10)  # Breaks when count >= 10
```

### Gotcha 6: Label Resolution at Load Time

Labels are resolved when code is loaded, not at runtime:

```whitvm
set *target* #:loop:#  # This is just a string, not a label reference

jmp :loop:  # This works - label resolved at load time
# jmp *target*  # This doesn't work - can't jump to variable
```

## Internal Architecture

### Parser → Interpreter Flow

```
.whitvm file
    ↓
WhitVMLoader.load_file()
    ↓
Parser.parse()
├─ Tokenize lines
├─ Extract labels → labels dict
└─ Extract instructions → instructions list
    ↓
Interpreter
├─ dmem: variable storage
├─ pc: program counter
└─ Execute instructions sequentially
    ↓
Output & Program State
```

### Instruction Execution Loop

```python
while pc < len(instructions):
    instr = instructions[pc]
    opcode = instr[0]
    
    if opcode == 'say':
        _exec_say(args)
    elif opcode == 'ask':
        _exec_ask(args)
    elif opcode == 'jmp':
        _exec_jmp(args)
    elif opcode == 'set':
        _exec_set(args)
    elif opcode == 'halt':
        break
    
    pc += 1  # Move to next instruction
```

### Tokenization Rules

When parsing a line:
1. Skip whitespace
2. Match delimited tokens: `#...#`, `(...)`,:...:`
3. Variable: `*name*` (only if followed by alphanumeric)
4. Number/opcode: contiguous alphanumeric

Example tokenization:
```
"say *name* #Hello# ((*x*) + 1) 0"
→ ["say", "*name*", "#Hello#", "((*x*) + 1)", "0"]
```

## Optimization Techniques

### Important: Newlines and String Building

When building strings across multiple `say` statements, remember that `nl_qty` is printed **after** the value:

```whitvm
say #Hello, # 0 1
say *name* 0 1
say #!# 1 1
```

Step by step:
- Line 1: Prints "Hello, " + 0 newlines = "Hello, "
- Line 2: Prints *name* + 0 newlines = "Alice"  
- Line 3: Prints "!" + 1 newline = "!\n"

**Output**: `Hello, Alice!`

The newlines come **after** each value, so they don't interfere. Use `nl_qty=0` to continue on the same line.

### Technique 1: String Pooling

For repeated strings, define once:

```whitvm
set *sep* # --- #

say #Game Start# 1 1
say *sep* 1 1
say #Level 1# 1 1
say *sep* 1 1
say #Boss Battle# 1 1
```

The minifier does this automatically with `whitvm minify --pool-strings`.

### Technique 2: Early Exit

Check conditions early to avoid unnecessary code:

```whitvm
# INEFFICIENT
:game_loop:
    say #Checking health...# 1 1
    say #Calculating damage...# 1 1
    say #Updating inventory...# 1 1
    jmp :dead: ((*health*) <= 0)
    jmp :game_loop:

# EFFICIENT - guard clause
:game_loop:
    jmp :dead: ((*health*) <= 0)
    say #Still alive# 1 1
    jmp :game_loop:
```

### Technique 3: Constant Expressions

Pre-calculate at minification time:

```whitvm
set *max_health* ((100 + 50))   # Can be minified to 150
set *damage* ((((10 * 5) - 10)))  # Can be minified to 40
```

Run `whitvm minify game.whitvm --eval-const` to enable.

### Technique 4: Reduce Label Jumps

Minimize label lookups:

```whitvm
# INEFFICIENT - many label references
jmp :check: ((*x*) > 5)
:check:
    jmp :process:
:process:
    say #Process# 1 1

# EFFICIENT - direct jump
jmp :process: ((*x*) > 5)
:process:
    say #Process# 1 1
```

### Technique 5: Variable Reuse

Reuse variables when their old value is no longer needed:

```whitvm
# INEFFICIENT - many variables
set *temp1* 10
set *temp2* 20
set *result1* ((*temp1*) + (*temp2*))
set *temp3* 5
set *result2* ((*temp3*) + (*result1*))

# EFFICIENT - reuse temp
set *temp* 10
set *temp* ((*temp*) + 20)  # temp=30
set *temp* ((*temp*) + 5)   # temp=35
set *result* *temp*
```

The minifier will rename these to single-letter variables: `*a*`, `*b*`, etc.

## Testing and Debugging

### Debug Pattern: Print State

Use `say` to inspect variables:

```whitvm
set *health* 100
set *gold* 50

say #State at checkpoint 1:# 2 1
say #Health: # 0 1
say *health* 1 1
say #Gold: # 0 1
say *gold* 1 1
```

### Debug Pattern: Trace Execution

Add markers to trace code paths:

```whitvm
say #[TRACE] Entering main_menu# 1 1
ask 2
say #[TRACE] User selected option 1# 1 1
```

### Testing Pattern: Unit Tests

Create small `.whitvm` files to test each feature:

```whitvm
# test_arithmetic.whitvm
set *result* ((5 + 3))
say #Expected: 8, Got: # 0 1
say *result* 1 1

set *result* ((20 / 4))
say #Expected: 5, Got: # 0 1
say *result* 1 1
```

Then run: `whitvm run test_arithmetic.whitvm`

## Summary

Advanced WhitVM development involves:
- Understanding ask's nested conditional structure
- Using control flow patterns (guards, state machines)
- Managing global memory and variable scope
- Avoiding edge cases (string comparison, division, infinite loops)
- Optimizing with minification and smart variable usage
- Testing with debug patterns and unit test files

Master these concepts to write sophisticated, efficient WhitVM games.
