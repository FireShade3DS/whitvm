# WhitVM ISA (Instruction Set Architecture)

## Architecture
- **Type**: Harvard (separate Instruction/Data memory)
- **Execution Model**: Sequential execution with conditional flow control (via `ask`, `jmp`, and conditions)
- **Halt Condition**: Automatic when the CPU runs out of instructions, or explicit `halt` instruction

## Syntax Rules

| Element | Format | Example |
|---------|--------|---------|
| Labels | `:label_name:` | `:start_scene:` |
| Variables | `*var_name*` | `*player_health*` |
| Strings | `#text content#` | `#Game Over#` |
| Numbers | decimal integers | `100`, `42`, `-5` |
| Expressions | `(expression)` with operators. Can be nested. | `((*score* % 5) + (*bonus* * 2))` |
| Instructions | `OPCODE arg1 arg2 arg3` | `say #Hello# 1 *cond*` |
| Comments | Use `say #text# 1 0` (condition = 0) | `say #TODO: fix this# 1 0` |

## Instruction Set

| Opcode | Format | Description |
|--------|--------|-------------|
| `say` | `say value [nl_qty] [condition]` | Prints `value` (var, #str#, number, or expression). `nl_qty` specifies number of newlines (default: 1). Executes if `condition` is non-zero (default: 1). |
| `ask` | `ask n [condition]` | Prompts for user input (integer 1 to n). When input is received, PC jumps forward by (input - 1) instructions. Executes if `condition` is non-zero (default: 1). |
| `jmp` | `jmp :label: [condition]` | Jumps PC to `:label:` if `condition` is non-zero (default: 1). |
| `set` | `set *var* value` | Assigns `value` to variable `*var*` in DMEM. `value` can be a number, string, variable reference, or expression. |
| `halt` | `halt [condition]` | Halts program execution if `condition` is non-zero (default: 1). |

## Data Memory (DMEM) Initialization

- Variables must be explicitly initialized with `set` instructions before use
- Accessing an uninitialized variable raises an error
- All variables are stored in a flat namespace

## Operators and Expressions

### Operator Precedence (highest to lowest)
1. **Multiplication/Division/Modulo** (`*`, `/`, `%`) - division is integer (floor) division
2. **Addition/Subtraction** (`+`, `-`)
3. **Comparison** (`==`, `!=`, `<`, `>`, `<=`, `>=`) - returns 1 (true) or 0 (false)

### Comparison Results
- All comparison operators return `1` for true, `0` for false
- Comparisons work on numbers and strings (string equality with `==` and `!=`)
- Example: `(*health* < 20)` evaluates to 1 or 0

### Type Coercion
- String concatenation is not supported; use multiple `say` instructions
- Cannot mix types in arithmetic (e.g., `(#text# + 5)` is invalid)
- Comparison operators can compare strings and numbers separately

## Built-in Functions

| Function | Format | Description |
|----------|--------|-------------|
| `rng` | `(rng min max)` | Returns random integer in range [min, max] inclusive |

Example: `(rng 1 6)` simulates a die roll (1-6)

## Common Patterns

### Conditional Execution
```asm
jmp :skip_message: (*player_health* >= 50)
say #Health is critical!# 1 1
:skip_message:
```

### Loops with Conditional Jumps
```asm
set *count* 0
:loop:
say *count* 0 1
set *count* ((*count*) + 1)
jmp :loop: ((*count*) < 5)
say # items processed# 1 1
```

### Ask-based Branching
After an `ask n` instruction, place n sequential `jmp` instructions. The first option skips 0 jumps, the second skips 1, etc.:
```asm
say #Choose: 1=Attack, 2=Defend, 3=Run# 1 1
ask 3

jmp :attack:          # Option 1: execute this (no skip)
jmp :defend:          # Option 2: skip previous, execute this
jmp :run:             # Option 3: skip previous two, execute this

:attack:
say #You attack!# 1 1
jmp :end:

:defend:
say #You defend!# 1 1
jmp :end:

:run:
say #You run away!# 1 1

:end:
```

### Accumulation with Loops
```asm
set *sum* 0
set *i* 1
:add_loop:
set *sum* ((*sum*) + (*i*))
set *i* ((*i*) + 1)
jmp :add_loop: ((*i*) <= 10)
say #Sum is: # 0 1
say *sum* 1 1
```

## Error Handling

### Runtime Errors
- **Undefined Variable**: Accessing a variable that hasn't been `set` raises an error
- **Undefined Label**: Jumping to a non-existent label raises an error
- **Invalid Input**: `ask` expects integer input; non-integer input causes an error
- **Out of Range Input**: If `ask n` receives input < 1 or > n, the jump does not occur; execution falls through to the next instruction (typically the first option's `jmp`)
- **Division by Zero**: Dividing by zero raises an error

### Syntax Errors
- Unclosed delimiters (`#`, `(`, `*`, `:`) are caught by the loader
- Invalid opcodes raise a runtime error
- Mismatched argument counts raise errors

## Example Program: Gender Selection

```asm
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

## Example Program: Loop with Counter

```asm
set *count* 0
set *max* 3
:countdown:
say #Count: # 0 1
say *count* 1 1
set *count* ((*count*) + 1)
jmp :countdown: ((*count*) < (*max*))
say #Liftoff!# 1 1
```

## Example Program: Dice Roll

```asm
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
