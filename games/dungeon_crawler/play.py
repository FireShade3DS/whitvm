#!/usr/bin/env python3
"""
Play the Dungeon Crawler game using WhitVM.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from whitvm import Interpreter


def main():
    """Load and run the dungeon crawler game"""
    game_dir = os.path.dirname(__file__)
    game_file = os.path.join(game_dir, 'game.whitvm')
    
    interp = Interpreter()
    interp.load_file(game_file)
    interp.run()


if __name__ == '__main__':
    main()
