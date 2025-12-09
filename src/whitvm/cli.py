#!/usr/bin/env python3
"""WhitVM Command-Line Interface - Create, run, and minify WhitVM games."""

import click
import sys
from pathlib import Path
from .interpreter import Interpreter
from .loader import WhitVMLoader
from .minifier import WhitVMMinifier


def success(msg):
    """Format success message."""
    click.echo(click.style("✓ ", fg="green", bold=True) + msg)


def error(msg):
    """Format error message."""
    click.echo(click.style("✗ ", fg="red", bold=True) + click.style(msg, fg="red"), err=True)


def info(msg):
    """Format info message."""
    click.echo(click.style("ℹ ", fg="blue") + msg)


@click.group()
def cli():
    """WhitVM - Create and run interactive text adventure games.

    Write your game logic in .whitvm files and run them with the whitvm command.
    For help with a specific command, use: whitvm COMMAND --help
    """
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def run(file):
    """Run a WhitVM game.

    Example:
        whitvm run my_game.whitvm
    """
    try:
        loader = WhitVMLoader()
        code = loader.load_file(file)
        interpreter = Interpreter()
        interpreter.load(code)
        click.echo()
        interpreter.run()
        click.echo()
    except FileNotFoundError as e:
        error(str(e))
        sys.exit(1)
    except Exception as e:
        error(f"Runtime error: {e}")
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file (default: filename.min.whitvm)",
)
@click.option(
    "--vars",
    is_flag=True,
    default=True,
    help="Shrink variable names (default: enabled)",
)
@click.option(
    "--labels", is_flag=True, default=True, help="Shrink label names (default: enabled)"
)
@click.option("--no-const", is_flag=True, help="Don't evaluate constant expressions")
@click.option("--keep-defaults", is_flag=True, help="Keep default arguments")
def minify(file, output, vars, labels, no_const, keep_defaults):
    """Minify a WhitVM game to reduce file size.

    Example:
        whitvm minify my_game.whitvm -o my_game.min.whitvm
    """
    try:
        loader = WhitVMLoader()
        code = loader.load_file(file)

        minified = WhitVMMinifier.minify(
            code,
            shrink_vars=vars,
            shrink_labels=labels,
            eval_const=not no_const,
            remove_defaults=not keep_defaults,
            pool_strings=True,
        )

        if not output:
            output = str(Path(file).with_suffix(".min.whitvm"))

        with open(output, "w", encoding="utf-8") as f:
            f.write(minified)

        original_size = len(code)
        minified_size = len(minified)
        ratio = 100 * (1 - minified_size / original_size)

        success(f"Minified: {file} → {output}")
        info(f"Size: {original_size} → {minified_size} bytes ({ratio:.1f}% reduction)")
    except FileNotFoundError as e:
        error(str(e))
        sys.exit(1)
    except Exception as e:
        error(str(e))
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def check(file):
    """Validate a WhitVM game without running it.

    Example:
        whitvm check my_game.whitvm
    """
    try:
        loader = WhitVMLoader()
        code = loader.load_file(file)
        WhitVMLoader.validate_syntax(code)

        # Try to parse it
        interpreter = Interpreter()
        interpreter.load(code)

        success(f"{file} is valid")
        info(f"Instructions: {len(interpreter.instructions)}")
        info(f"Labels: {len(interpreter.labels)}")
    except Exception as e:
        error(f"Validation failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("name")
@click.option(
    "-t",
    "--template",
    type=click.Choice(["blank", "dungeon", "story"], case_sensitive=False),
    default="blank",
    help="Game template to use",
)
def new(name, template):
    """Create a new WhitVM game project.

    Example:
        whitvm new MyAdventure --template dungeon
    """
    # Create directory
    game_dir = Path(name)
    if game_dir.exists():
        error(f"Directory '{name}' already exists")
        sys.exit(1)

    game_dir.mkdir(parents=True)
    game_file = game_dir / f"{name}.whitvm"

    # Game templates
    templates = {
        "blank": """:start:
    say #Welcome to """ + name + """!# 2 1
    say #Type: whitvm run """ + name + """/""" + name + """.whitvm# 1 1
""",
        "dungeon": """:start:
    set *health* 100
    set *gold* 0
    say #=== """ + name.upper() + """ ===# 2 1
    say #You awake in a mysterious place.# 1 1
    say #1) Explore  2) Rest# 1 1
    ask 2
    
    jmp :explore:
    jmp :rest:

:explore:
    say #You find 50 gold!# 1 1
    set *gold* 50
    jmp :end:

:rest:
    say #You feel refreshed.# 1 1
    jmp :end:

:end:
    say #Game Over!# 1 1
""",
        "story": """:start:
    say #A Choice-Based Story# 2 1
    say #You stand at a crossroads.# 1 1
    say #1) Take the left path  2) Take the right path# 1 1
    ask 2
    
    jmp :left:
    jmp :right:

:left:
    say #You find a mysterious door.# 1 1
    jmp :end:

:right:
    say #You meet a wise sage.# 1 1
    jmp :end:

:end:
    say #Your journey ends here.# 1 1
""",
    }

    template_code = templates.get(template, templates["blank"])

    with open(game_file, "w") as f:
        f.write(template_code)

    success(f"Created game project: {game_dir}/")
    info(f"Template: {template}")
    info(f"Main file: {game_file}")
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  cd {name}")
    click.echo(f"  whitvm run {name}.whitvm")
    click.echo(f"  whitvm minify {name}.whitvm -o {name}.min.whitvm")


@cli.command()
def version():
    """Show WhitVM version."""
    from . import __version__

    click.echo(f"WhitVM {__version__}")


def main():
    """Entry point for CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo()
        info("Interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
