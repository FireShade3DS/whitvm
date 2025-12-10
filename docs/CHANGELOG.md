# Changelog

All notable changes to WhitVM are documented in this file.

## [1.0.3] - 2025

### Added
- Profiler tool for benchmarking and optimizing games (measures instructions/second)
- 8 new comprehensive minification optimization tests
- Proper pytest test suite structure with dedicated test files

### Changed
- **Minifier refactor**: Separated concerns into minifier_core.py and minifier.py
  - Core minification (comments, defaults, whitespace) always applied, safe
  - Advanced optimizations (name shrinking, constant evaluation, string pooling, dead code removal, unreachable code elimination) opt-in flags
- Consolidated documentation: 6 separate markdown files merged into single `docs/DOCUMENTATION.md`
- Reorganized file structure: scripts moved to `scripts/`, CHANGELOG moved to `docs/`
- Improved .gitignore with comprehensive Python, testing, IDE, and OS patterns

### Fixed
- Fixed tokenizer to properly handle `*` (multiplication) in constant expressions by using non-greedy regex
- Fixed unreachable code elimination to correctly handle ask dispatch patterns (jumps after ask are reachable)
- Resolved symbol ambiguity between `*` multiplication operator and `*var*` variable references

### Technical
- Minifier achieves 30%+ file size reduction on complex games
- All optimization passes work safely together
- Conservative multi-pass strategy preserves labels even if unused
- Reduced repo clutter: 964K total, 33 source files, comprehensive .gitignore

## [1.0.2] - 2025

### Fixed
- Fixed `halt` instruction with condition=0 not skipping execution properly
- Fixed `WhitVMLoader.load_file()` and `load_from_string()` to be static methods (API compatibility)
- Fixed aweosme constant test with correct expected output
- Fixed minifier tests to check semantic correctness

## [1.0.1] - 2025

### Added
- Professional Click-based CLI with 5 commands (run, minify, check, new, version)
- Game scaffolding system with three templates: blank, dungeon, story
- Comprehensive documentation: TUTORIAL.md, QUICK_START.md, ADVANCED.md
- Example games: quiz_game.whitvm, word_counter.whitvm
- Enhanced error handling and validation in CLI
- Color-coded output for CLI feedback (success, error, info)
- File size reduction reporting for minification
- Syntax validation without execution (check command)

### Changed
- Improved README.md with better feature descriptions and examples
- Enhanced CLI output formatting with consistent messaging
- Better user guidance in `new` command with next steps
- Revised features list to prioritize game development use cases

### Fixed
- Ask instruction now correctly skips n jumps when condition=0
- Improved nested conditional logic testing for ask instruction
- Fixed error messages to be more user-friendly

### Technical
- Added Click dependency to pyproject.toml
- Entry points configured for whitvm CLI command
- Full backwards compatibility maintained with v1.0.0

## [1.0.0] - 2025

### Initial Release
- Harvard-architecture interpreter for .whitvm script execution
- Core instructions: say, ask, jmp, set, halt
- Variable support with proper initialization
- Expression evaluation with operator precedence
- Conditional execution on all instructions
- Comprehensive test suite (62 unit tests)
- Minification support for code size reduction
- Aweosme-complete specification support
- Example programs and games

