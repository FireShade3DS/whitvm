"""WhitVM - Interpreter for interactive fiction.

Parse and execute whitvm scripts for text-based adventures.

Quick start:
    from whitvm import Interpreter
    
    code = '''
    :start:
        say #Hello World!# 1 1
    '''
    
    interp = Interpreter()
    interp.load(code)
    interp.run()

Or use the CLI:
    whitvm new MyGame --template dungeon
    whitvm run MyGame/MyGame.whitvm
    whitvm minify MyGame/MyGame.whitvm
"""

from .interpreter import Interpreter, Parser
from .loader import WhitVMLoader, Loader
from .minifier import WhitVMMinifier
from .profiler import WhitVMProfiler

__version__ = "1.0.0"
__all__ = ["Interpreter", "Parser", "WhitVMLoader", "Loader", "WhitVMMinifier", "WhitVMProfiler"]
