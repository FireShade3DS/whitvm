# WhitVM Complete Documentation

A lightweight interpreter for text adventure games. Write interactive fiction with a simple stack-based language.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Core Syntax Reference](#core-syntax-reference)
4. [Game Development Guide](#game-development-guide)
5. [Advanced Topics](#advanced-topics)
6. [Instruction Set Architecture](#instruction-set-architecture)
7. [Complete Examples](#complete-examples)

---

## Quick Start

### Installation

```bash
pip install -e .
# or for command-line use:
pipx install .
```

### Create Your First Game (2 minutes)

```bash
whitvm new MyGame --template dungeon
whitvm run MyGame/MyGame.whitvm
```

### Essential Commands

```bash
# Run your game
whitvm run game.whitvm

# Check for errors without running
whitvm check game.whitvm

# Minify for distribution (reduce file size)
whitvm minify game.whitvm -o game.min.whitvm

# Create new game from template
whitvm new GameName --template dungeon
```

### Basic Game Template

```whitvm
:start:
    say #Welcome to My Game!# 2 1
    say #What do you do?# 1 1
    say #1) Go left  2) Go right# 1 1
    ask 2
    
    jmp :left:
    jmp :right:

:left:
    say #You went left!# 1 1
    halt

:right:
    say #You went right!# 1 1
    halt
```

---

## Installation

### Development Mode

```bash
pip install -e .
```

Install in development mode for local development or testing.

### Command-Line Use

```bash
pipx install .
```

After installation, you have access to the `whitvm` command globally.

---

## Core Syntax Reference

### Syntax at a Glance

| Feature | Syntax | Example |
|---------|--------|---------|
| **Label** | `:name:` | `:start:` |
| **Print** | `say value [nl] [cond]` | `say #Hello# 1 1` |
| **Choice** | `ask n` | `ask 2` |
| **Jump** | `jmp :label: [cond]` | `jmp :end:` |
| **Variable** | `set *name* value` | `set *gold* 100` |
| **Math** | `(expr)` | `((*x*) + 5)` |
| **Stop** | `halt` | `halt` |

### Labels (Markers)

Labels mark locations in your code that you can jump to:

```whitvm
:label_name:
```

Example:
```whitvm
:start:
    say #You're at the start!# 1 1

:ending:
    say #Game over!# 1 1
    halt
```

### Variables (Storage)

Store and manipulate data:

```whitvm
set *name* value        # Strings: #text#
                        # Numbers: 123
                        # Variables: *other_var*
                        # Expressions: (expr)
```

Examples:
```whitvm
set *health* 100        # Number
set *name* #Hero#       # String
set *level* 1           # Variable
set *damage* (10 + 5)   # Expression
```

**Important**: Variables must be explicitly initialized with `set` before use.

### Output (Display)

Print values to the player:

```whitvm
say value [newlines] [condition]
say #Hello# 1 1         # Print "Hello" with 1 newline
say *name* 0 1          # Print variable, no newline
say (expr) 1 1          # Print result of expression
```

Parameters:
- `value`: Text (#...#), variable (*...*), number, or expression
- `newlines`: Number of newlines after value (default: 1)
- `condition`: Execute only if non-zero (default: 1, always execute)

### Input (Player Choice)

Get player input and branch:

```whitvm
ask n [condition]       # Wait for choice in range 1-n, then jump n-1 instructions
ask 2                   # Expect 1 or 2
jmp :option1:           # If they chose 1
jmp :option2:           # If they chose 2
```

After `ask n`, place exactly `n` `jmp` instructions. The first option skips 0 jumps, the second skips 1, etc.

### Jumps (Control Flow)

Change the flow of execution:

```whitvm
jmp :label: [condition]     # Go to label if condition true
jmp :start:                 # Unconditional jump
jmp :loop: ((*count*) < 10) # Conditional jump
```

### Halt (Stop)

End execution:

```whitvm
halt [condition]        # End game if condition true
halt                    # Unconditional end
```

### Expressions

Perform calculations within parentheses:

```whitvm
set *x* (5 + 3)         # OK
set *health* 100        # OK (no parentheses needed for literals)
set *y* ((*x*) * 2)     # OK (variables in expressions)
```

| Operator | Meaning |
|----------|---------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Integer division (floors) |
| `%` | Modulo (remainder) |
| `==` | Equal to |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `(rng min max)` | Random integer [min, max] |

### Operator Precedence (High to Low)

1. `*` `/` `%` (Multiply, Divide, Modulo)
2. `+` `-` (Add, Subtract)
3. `==` `!=` `<` `>` `<=` `>=` (Comparisons)

### Truthiness

- Non-zero: TRUE (executes)
- Zero: FALSE (skips)

```whitvm
say #You're alive!# 1 1 ((*health*) > 0)  # Only if health > 0
jmp :win: ((*score*) >= 100)              # Only if score >= 100
```

### Type Coercion

Variables can hold any value. Automatic coercion in expressions:

```whitvm
set *str* #42#
set *result* ((*str*) + 8)  # Treats "42" as 42, result = 50
```

### Comments

Use the condition=0 pattern:

```whitvm
say #This is a note for developers# 1 0
say #TODO: fix this# 1 0
```

---

## Game Development Guide

### Your First Game

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

Output:
```
Hello, adventurer!
Welcome to WhitVM.
```

### Building Choices

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

### Game Variables

Store information:

```whitvm
set *health* 100
set *name* #Hero#
set *gold* 0
```

### Health System Example

```whitvm
:start:
    set *health* 100
    
:combat:
    say #Health: # 0 1
    say *health* 1 1
    say #Fight? (1=yes, 2=no)# 1 1
    ask 2
    
    jmp :fight:
    jmp :escape:

:fight:
    set *health* ((*health*) - 20)
    jmp :combat: ((*health*) > 0)
    say #You died!# 1 1
    halt

:escape:
    say #You escaped!# 1 1
    halt
```

### Common Patterns

#### Loop (Repeat)

```whitvm
set *count* 0
:loop:
    say *count* 1 1
    set *count* ((*count*) + 1)
    jmp :loop: ((*count*) < 10)
```

#### Conditional (If-Then)

```whitvm
jmp :weak: ((*health*) < 25)
say #You're strong!# 1 1
jmp :continue:

:weak:
    say #You're weak!# 1 1

:continue:
    say #Next...# 1 1
```

#### Choice (Multiple Options)

```whitvm
say #Choose: 1=A  2=B  3=C# 1 1
ask 3

jmp :choice_a:
jmp :choice_b:
jmp :choice_c:

:choice_a:
    say #You chose A# 1 1
    halt

:choice_b:
    say #You chose B# 1 1
    halt

:choice_c:
    say #You chose C# 1 1
    halt
```

#### String Building (Concatenation)

```whitvm
say #Hello, # 0 1       # No newline
say *name* 0 1          # Continue
say #!# 1 1             # With newline
```

#### Counter/Accumulator

```whitvm
set *total* 0
set *count* 0

:add_loop:
    set *total* ((*total*) + (*count*))
    set *count* ((*count*) + 1)
    jmp :add_loop: ((*count*) < 10)

say #Total: # 0 1
say *total* 1 1
```

#### Random Numbers

```whitvm
set *roll* (rng 1 6)    # Roll a 6-sided die
```

### Example: Health Game

```whitvm
set *health* 100

:start:
    say #Health: # 0 1
    say *health* 1 1
    say #1) Attack  2) Defend  3) Heal# 1 1
    ask 3
    
    jmp :attack:
    jmp :defend:
    jmp :heal:

:attack:
    set *health* ((*health*) - 25)
    jmp :start: ((*health*) > 0)
    say #You died!# 1 1
    halt

:defend:
    say #You defended successfully!# 1 1
    jmp :start:

:heal:
    set *health* ((*health*) + 10)
    jmp :start: ((*health*) <= 100)
    say #Already at full health!# 1 1
    jmp :start:
```

### Example: Simple Quiz

```whitvm
set *score* 0

say #Question 1: What is 2+2?# 1 1
say #1) 3  2) 4  3) 5# 1 1
ask 3

jmp :q1_wrong:
jmp :q1_right:
jmp :q1_wrong:

:q1_right:
    set *score* ((*score*) + 1)

:q1_wrong:
    say #Score: # 0 1
    say *score* 1 1
    halt
```

### Tips & Best Practices

1. **Test Frequently**: Use `whitvm check game.whitvm` to catch errors
2. **Use Templates**: Start with `whitvm new` for structure
3. **Minimize**: Use `whitvm minify` before sharing
4. **Comment Out**: Use `say #comment# 1 0` for notes
5. **Organize**: Use labels to structure your game
6. **Debug**: Print variables with `say *var* 1 1`
7. **Always indent** with 4 spaces for readability
8. **Use descriptive variable names**: `*player_health*` not `*h*`
9. **Break complex games** into labeled sections
10. **Initialize all variables** at the start
11. **Plan your jumps** before coding
12. **Keep expressions simple** (break into multiple sets if needed)

### Common Issues

**"Undefined variable" error**
```whitvm
# WRONG - using before setting
say *name* 1 1

# RIGHT - set first
set *name* #Hero#
say *name* 1 1
```

**"Undefined label" error**
```whitvm
# WRONG - wrong spelling
jmp :beginning:     # but label is :start:

# RIGHT - match exactly
:start:
    say #Hi# 1 1
    jmp :start:
```

**Input not working**
```whitvm
# WRONG - missing jmp instructions
ask 2
say #You chose option 1# 1 1

# RIGHT - jmp for each option
ask 2
jmp :option1:
jmp :option2:

:option1:
    say #Option 1# 1 1
    halt

:option2:
    say #Option 2# 1 1
    halt
```

---

## Advanced Topics

### Ask Instruction Deep Dive

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

#### Behavior Breakdown

**Case 1: Normal Ask (condition=1)**
```whitvm
ask 2
jmp :option_a:     # executed if input=1 (no jump)
jmp :option_b:     # executed if input=2 (jump 1)
```

- Input 1 → PC doesn't change → execute `:option_a:`
- Input 2 → PC += 1 → skip `:option_a:`, execute `:option_b:`
- Input 99 → invalid → default to option 1 (execute `:option_a:`)

**Case 2: Disabled Ask (condition=0)**
```whitvm
ask 2 0
jmp :option_a:     # SKIPPED
jmp :option_b:     # SKIPPED
say #Continues here# 1 1
```

When disabled, the instruction **skips forward by `n` positions**, jumping past all option branches entirely.

#### Example: Conditional Questionnaire

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

### Control Flow Patterns

#### Nested Choices

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

#### Guard Clauses

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

#### State Machines

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

### Memory and Performance

#### Memory Model

WhitVM uses **Harvard Architecture**:
- **IMEM** (Instruction Memory): `.whitvm` code → immutable instructions
- **DMEM** (Data Memory): Variables and state → mutable at runtime

#### Variable Scope

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

#### Performance Notes

- **No function overhead**: All `jmp` is inline, no call stack
- **Minification reduces size 17%+**: Variable/label shrinking, constant folding
- **No garbage collection**: Variables live until program end
- **Linear instruction execution**: O(n) worst case for any program

### Edge Cases and Gotchas

#### Gotcha 1: Expressions Need Outer Parentheses

Outer parentheses mark "evaluate this as an expression". Flow is inside-out:

```whitvm
set *x* 5
set *y* 3
set *result* ((*x*) + (*y*))
```

Without outer parens:
```whitvm
set *result* *x* + *y*        # ERROR - not recognized as expression
```

#### Gotcha 2: String Comparison

Strings are compared lexicographically and case-sensitively:

```whitvm
set *name* #alice#
say *name* 1 1 ((*name*) == #alice#)  # Prints "alice" (true)

set *name* #Alice#
say *name* 1 1 ((*name*) == #alice#)  # Prints nothing (false, case matters)
```

#### Gotcha 3: Division Rounds Down

Integer division floors, not rounds:

```whitvm
set *result* ((7 / 2))   # 3, not 3.5
set *result* ((10 / 3))  # 3, not 3.33
```

#### Gotcha 4: Ask Doesn't Return a Value

```whitvm
ask 2 ((*x*) > 5)        # VALID - ask conditionally

set *result* (ask 2)     # INVALID - can't store ask's result
```

Ask modifies the program counter directly, it doesn't produce a value.

#### Gotcha 5: Infinite Loops

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

#### Gotcha 6: Label Resolution at Load Time

Labels are resolved when code is loaded, not at runtime:

```whitvm
set *target* #:loop:#  # This is just a string, not a label reference

jmp :loop:  # This works - label resolved at load time
# jmp *target*  # This doesn't work - can't jump to variable
```

### Optimization Techniques

#### String Pooling

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

#### Early Exit

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

#### Constant Expressions

Pre-calculate at minification time:

```whitvm
set *max_health* ((100 + 50))   # Can be minified to 150
set *damage* ((((10 * 5) - 10)))  # Can be minified to 40
```

Run `whitvm minify game.whitvm --eval-const` to enable.

#### Variable Reuse

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

### Testing and Debugging

#### Debug Pattern: Print State

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

#### Debug Pattern: Trace Execution

Add markers to trace code paths:

```whitvm
say #[TRACE] Entering main_menu# 1 1
ask 2
say #[TRACE] User selected option 1# 1 1
```

#### Testing Pattern: Unit Tests

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

---

## Instruction Set Architecture

### Architecture

- **Type**: Harvard (separate Instruction/Data memory)
- **Execution Model**: Sequential execution with conditional flow control (via `ask`, `jmp`, and conditions)
- **Halt Condition**: Automatic when the CPU runs out of instructions, or explicit `halt` instruction

### Syntax Rules

| Element | Format | Example |
|---------|--------|---------|
| Labels | `:label_name:` | `:start_scene:` |
| Variables | `*var_name*` | `*player_health*` |
| Strings | `#text content#` | `#Game Over#` |
| Numbers | decimal integers | `100`, `42`, `-5` |
| Expressions | `(expression)` with operators. Can be nested. | `((*score* % 5) + (*bonus* * 2))` |
| Instructions | `OPCODE arg1 arg2 arg3` | `say #Hello# 1 *cond*` |
| Comments | Use `say #text# 1 0` (condition = 0) | `say #TODO: fix this# 1 0` |

### Instruction Set

| Opcode | Format | Description |
|--------|--------|-------------|
| `say` | `say value [nl_qty] [condition]` | Prints `value` (var, #str#, number, or expression). `nl_qty` specifies number of newlines (default: 1). Executes if `condition` is non-zero (default: 1). |
| `ask` | `ask n [condition]` | Prompts for user input (integer 1 to n). When input is received, PC jumps forward by (input - 1) instructions. Executes if `condition` is non-zero (default: 1). |
| `jmp` | `jmp :label: [condition]` | Jumps PC to `:label:` if `condition` is non-zero (default: 1). |
| `set` | `set *var* value` | Assigns `value` to variable `*var*` in DMEM. `value` can be a number, string, variable reference, or expression. |
| `halt` | `halt [condition]` | Halts program execution if `condition` is non-zero (default: 1). |

### Data Memory (DMEM) Initialization

- Variables must be explicitly initialized with `set` instructions before use
- Accessing an uninitialized variable raises an error
- All variables are stored in a flat namespace

### Built-in Functions

| Function | Format | Description |
|----------|--------|-------------|
| `rng` | `(rng min max)` | Returns random integer in range [min, max] inclusive |

Example: `(rng 1 6)` simulates a die roll (1-6)

### Error Handling

#### Runtime Errors
- **Undefined Variable**: Accessing a variable that hasn't been `set` raises an error
- **Undefined Label**: Jumping to a non-existent label raises an error
- **Invalid Input**: `ask` expects integer input; non-integer input causes an error
- **Out of Range Input**: If `ask n` receives input < 1 or > n, the jump does not occur; execution falls through to the next instruction (typically the first option's `jmp`)
- **Division by Zero**: Dividing by zero raises an error

#### Syntax Errors
- Unclosed delimiters (`#`, `(`, `*`, `:`) are caught by the loader
- Invalid opcodes raise a runtime error
- Mismatched argument counts raise errors

---

## Complete Examples

### Example 1: Gender Selection

```whitvm
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
```

### Example 2: Loop with Counter

```whitvm
set *count* 0
set *max* 3
:countdown:
say #Count: # 0 1
say *count* 1 1
set *count* ((*count*) + 1)
jmp :countdown: ((*count*) < (*max*))
say #Liftoff!# 1 1
```

### Example 3: Dice Roll

```whitvm
set *roll* (rng 1 6)
say #You rolled: # 0 1
say *roll* 1 1
jmp :high_roll: (*roll* > 3)
say #Low roll# 1 1
jmp :end:

:high_roll:
say #High roll!# 1 1

:end:
```

### Example 4: Complete Dungeon Game

See `examples/` directory for a complete game with items, enemies, and progression.

Run it with: `whitvm run examples/game.whitvm`

---

## CLI Help

```bash
whitvm --help              # Show all commands
whitvm run --help          # Help for specific command
whitvm new --help          # Help for game creation
whitvm minify --help       # Minification options
whitvm check --help        # Syntax checking options
```

---

## Next Steps

1. Create a game: `whitvm new MyGame --template blank`
2. Edit it: `vim MyGame/MyGame.whitvm`
3. Run it: `whitvm run MyGame/MyGame.whitvm`
4. Share it: `whitvm minify MyGame/MyGame.whitvm -o release.whitvm`

Happy game making!
