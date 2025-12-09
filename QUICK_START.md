# WhitVM Quick Start Guide

## Installation

```bash
pip install -e .
```

## Create Your First Game (2 minutes)

```bash
whitvm new MyGame --template dungeon
whitvm run MyGame/MyGame.whitvm
```

## Basic Game Template

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

## Essential Commands

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

## Core Syntax

| Feature | Syntax | Example |
|---------|--------|---------|
| **Label** | `:name:` | `:start:` |
| **Print** | `say value [nl] [cond]` | `say #Hello# 1 1` |
| **Choice** | `ask n` | `ask 2` |
| **Jump** | `jmp :label: [cond]` | `jmp :end:` |
| **Variable** | `set *name* value` | `set *gold* 100` |
| **Math** | `(expr)` | `((*x*) + 5)` |
| **Stop** | `halt` | `halt` |

## Game Variables

```whitvm
set *health* 100        # Number
set *name* #Hero#       # String
set *level* 1           # Variable
set *damage* (10 + 5)   # Expression
```

## Conditional Execution

```whitvm
say #You're alive!# 1 1 ((*health*) > 0)  # Only if true
jmp :end: ((*turns*) >= 10)                # Conditional jump
```

## Example: Health System

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

## Useful Patterns

### Loop
```whitvm
set *count* 0
:loop:
    say *count* 1 1
    set *count* ((*count*) + 1)
    jmp :loop: ((*count*) < 10)
```

### Random
```whitvm
set *roll* (rng 1 6)    # Roll a 6-sided die
```

### String Building
```whitvm
say #Hello, # 0 1       # No newline
say *name* 0 1          # Continue
say #!# 1 1             # With newline
```

### Hidden Comment
```whitvm
say #This is a note for developers# 1 0
```

## Operators

| Type | Operators |
|------|-----------|
| **Arithmetic** | `+` `-` `*` `/` `%` |
| **Comparison** | `==` `!=` `<` `>` `<=` `>=` |

## CLI Help

```bash
whitvm --help              # Show all commands
whitvm run --help          # Help for specific command
whitvm new --help          # Help for game creation
```

## Tips

1. **Test Frequently**: Use `whitvm check game.whitvm` to catch errors
2. **Use Templates**: Start with `whitvm new` for structure
3. **Minimize**: Use `whitvm minify` before sharing
4. **Comment Out**: Use `say #comment# 1 0` for notes
5. **Organize**: Use labels to structure your game
6. **Debug**: Print variables with `say *var* 1 1`

## Full Documentation

- **Tutorial**: [docs/TUTORIAL.md](docs/TUTORIAL.md)
- **Language Spec**: [docs/isa.md](docs/isa.md)
- **Examples**: [examples/](examples/)
- **Improvements**: [IMPROVEMENTS.md](IMPROVEMENTS.md)

## Common Issues

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

## Next Steps

1. Create a game: `whitvm new MyGame --template blank`
2. Edit it: `vim MyGame/MyGame.whitvm`
3. Run it: `whitvm run MyGame/MyGame.whitvm`
4. Share it: `whitvm minify MyGame/MyGame.whitvm -o release.whitvm`
