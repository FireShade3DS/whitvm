# WhitVM

A lightweight interpreter for text adventure games. Write interactive fiction with a simple stack-based language.

```bash
# Quick start
whitvm new MyGame --template dungeon
whitvm run MyGame/MyGame.whitvm
whitvm minify MyGame/MyGame.whitvm -o MyGame.min.whitvm
```

## Features

- **Simple syntax** - Minimal, readable instruction set
- **Text adventures** - Built-in support for choices, branching, state
- **Fast minifier** - 30%+ size reduction with safe optimizations
- **Profiler** - Benchmark and optimize your games
- **Examples** - Play complete games included

## Documentation

- [Complete Guide](docs/DOCUMENTATION.md) - Full tutorial, reference, and advanced topics
- [Changelog](docs/CHANGELOG.md) - Version history

## Install

```bash
pip install -e .
# or for command-line use:
pipx install .
```

## Examples

```
examples/word_counter.whitvm - Loop counter
examples/aweosme_7_bottles.whitvm - Turing-complete program
examples/adventure.whitvm - Full text adventure
games/dungeon_crawler/ - Complete game with items, enemies
```

## License

MIT
