#!/usr/bin/env python3
"""Silent benchmark without output"""

import sys
import io
from pathlib import Path
from src.whitvm import WhitVMProfiler

# Suppress output during benchmarking
examples = [
    'examples/word_counter.whitvm',
    'examples/aweosme_7_bottles.whitvm',
    'examples/aweosme_function.whitvm',
]

profiler = WhitVMProfiler()

print(f"{'File':<40} {'Instrs':<10} {'Avg Time (ms)':<15} {'Instr/sec':<15}")
print("=" * 80)

for filepath in examples:
    if Path(filepath).exists():
        # Capture stdout to suppress program output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            result = profiler.profile_file(filepath, iterations=10, show_stats=False)
            sys.stdout = old_stdout
            
            print(f"{filepath:<40} {result['instructions']:<10} "
                  f"{result['avg_time']*1000:>10.2f}      {result['instructions_per_second']:>10,.0f}")
        except Exception as e:
            sys.stdout = old_stdout
            print(f"{filepath:<40} ERROR: {e}")
