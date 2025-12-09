# WhitVM Quick Reference

## Commands

```bash
whitvm new MyGame --template [blank|dungeon|story]  # Create project
whitvm run game.whitvm                              # Execute game
whitvm check game.whitvm                            # Validate syntax
whitvm minify game.whitvm -o game.min.whitvm        # Optimize
whitvm version                                      # Show version
```

## Syntax at a Glance

### Labels (Markers)
```whitvm
:label_name:
```

### Variables (Storage)
```whitvm
set *name* value        # Strings: #text#
                        # Numbers: 123
                        # Variables: *other_var*
                        # Expressions: (expr)
```

### Output (Display)
```whitvm
say value [newlines] [condition]
say #Hello# 1 1         # Print "Hello" with 1 newline
say *name* 0 1          # Print variable, no newline
say (expr) 1 1          # Print result of expression
```

### Input (Player Choice)
```whitvm
ask n [condition]       # Wait for choice 1-n, then jump n-1 instructions
ask 2                   # Expect 1 or 2
jmp :option1:           # If they chose 1
jmp :option2:           # If they chose 2
```

### Jumps (Control Flow)
```whitvm
jmp :label: [condition]     # Go to label if condition true
jmp :start:                 # Unconditional jump
jmp :loop: ((*count*) < 10) # Conditional jump
```

### Halt (Stop)
```whitvm
halt [condition]        # End game if condition true
halt                    # Unconditional end
```

## Expressions

| Operator | Meaning |
|----------|---------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Integer division |
| `%` | Modulo (remainder) |
| `==` | Equal to |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `(rng min max)` | Random integer [min, max] |

Always wrap expressions in parentheses:
```whitvm
set *x* (5 + 3)         # OK
set *health* 100        # OK (no parentheses needed for literals)
set *y* ((*x*) * 2)     # OK (variables in expressions)
```

## Operator Precedence (High to Low)

1. `*` `/` `%` (Multiply, Divide, Modulo)
2. `+` `-` (Add, Subtract)
3. `==` `!=` `<` `>` `<=` `>=` (Comparisons)

## Truthiness

- Non-zero: TRUE (executes)
- Zero: FALSE (skips)

```whitvm
say #You're alive!# 1 1 ((*health*) > 0)  # Only if health > 0
jmp :win: ((*score*) >= 100)              # Only if score >= 100
```

## Common Patterns

### Loop (Repeat)
```whitvm
set *i* 0
:loop:
    say *i* 1 1
    set *i* ((*i*) + 1)
    jmp :loop: ((*i*) < 10)
```

### Conditional (If-Then)
```whitvm
jmp :weak: ((*health*) < 25)
say #You're strong!# 1 1
jmp :continue:

:weak:
    say #You're weak!# 1 1

:continue:
    say #Next...# 1 1
```

### Choice (Multiple Options)
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

### String Building (Concatenate)
```whitvm
say #Hello, # 0 1      # No newline
say *name* 0 1         # Continue
say #!# 1 1            # With newline
```

### Counter/Accumulator
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

### Hidden Comment
```whitvm
say #This is a note for developers# 1 0
```

## Type Coercion

Variables can hold any value. Automatic coercion in expressions:

```whitvm
set *str* #42#
set *result* ((*str*) + 8)  # Treats "42" as 42, result = 50
```

## What Can Go Wrong

| Error | Cause | Fix |
|-------|-------|-----|
| "Undefined variable" | Using `*var*` before `set` | Always `set` first |
| "Undefined label" | Jumping to non-existent label | Check label spelling |
| Division by zero | Dividing by 0 | Check divisor isn't 0 |
| "Unclosed string" | Missing closing `#` | Match `#text#` |
| "Unclosed paren" | Missing `)` in expression | Match `(expr)` |
| Unreachable code | `halt` or `jmp` with no return | Plan control flow |

## Example: Simple Quiz

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

## Example: Simple Game

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

## Tips

1. Always indent with 4 spaces for readability
2. Use descriptive variable names: `*player_health*` not `*h*`
3. Test frequently with `whitvm check`
4. Comment with `say #comment# 1 0` (condition 0 = doesn't print)
5. Break complex games into labeled sections
6. Initialize all variables at the start
7. Plan your jumps before coding
8. Keep expressions simple (break into multiple sets if needed)

## Learn More

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 5-minute guide
- **[TUTORIAL.md](docs/TUTORIAL.md)** - Complete guide
- **[QUICK_START.md](QUICK_START.md)** - Command cheat sheet
- **[STYLE_GUIDE.md](docs/STYLE_GUIDE.md)** - Best practices
- **[examples/](examples/)** - Real working games

---

WhitVM Reference | v1.0.1 | [https://github.com/yourusername/whitvm](https://github.com)
