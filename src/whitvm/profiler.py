#!/usr/bin/env python3
"""
WhitVM Profiler - Analyze performance of WhitVM programs
"""

import time
import cProfile
import pstats
import io
from pathlib import Path
from typing import Dict, Any, Tuple
from .interpreter import Interpreter
from .loader import WhitVMLoader


class WhitVMProfiler:
    """Profile WhitVM code execution"""
    
    def __init__(self):
        self.execution_times: Dict[str, float] = {}
        self.instruction_counts: Dict[str, int] = {}
        self.variable_usage: Dict[str, int] = {}
    
    def profile_file(self, filepath: str, iterations: int = 1, show_stats: bool = True) -> Dict[str, Any]:
        """Profile a .whitvm file
        
        Args:
            filepath: Path to .whitvm file
            iterations: Number of times to run the program
            show_stats: Whether to print statistics
            
        Returns:
            Dictionary with profiling results
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        return self.profile_code(code, iterations, show_stats, str(filepath))
    
    def profile_code(self, code: str, iterations: int = 1, show_stats: bool = True, 
                     name: str = "program") -> Dict[str, Any]:
        """Profile WhitVM code
        
        Args:
            code: WhitVM source code
            iterations: Number of times to run
            show_stats: Whether to print statistics
            name: Name for display
            
        Returns:
            Dictionary with profiling results
        """
        # Parse code
        try:
            from .interpreter import Parser
            parser = Parser(code)
        except Exception as e:
            raise ValueError(f"Failed to parse code: {e}")
        
        # Count instructions
        instr_count = len(parser.instructions)
        label_count = len(parser.labels)
        
        # Time execution
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            interp = Interpreter()
            interp.load(code)
            interp.run()
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        results = {
            'name': name,
            'iterations': iterations,
            'total_time': total_time,
            'avg_time': avg_time,
            'instructions': instr_count,
            'labels': label_count,
            'instructions_per_second': (instr_count * iterations) / total_time if total_time > 0 else 0,
        }
        
        if show_stats:
            self._print_stats(results)
        
        return results
    
    def benchmark_suite(self, file_patterns: list = None) -> Dict[str, Dict[str, Any]]:
        """Run benchmark on multiple files
        
        Args:
            file_patterns: List of glob patterns to match files (default: examples/*.whitvm)
            
        Returns:
            Dictionary mapping filenames to benchmark results
        """
        if file_patterns is None:
            file_patterns = ['examples/**/*.whitvm']
        
        results = {}
        
        for pattern in file_patterns:
            for filepath in Path('.').glob(pattern):
                if filepath.is_file():
                    try:
                        result = self.profile_file(str(filepath), iterations=5, show_stats=False)
                        results[filepath.name] = result
                    except Exception as e:
                        print(f"Failed to profile {filepath}: {e}")
        
        # Print summary
        self._print_benchmark_summary(results)
        return results
    
    def profile_with_cprofile(self, code: str, iterations: int = 1) -> str:
        """Profile code using cProfile for detailed function profiling
        
        Args:
            code: WhitVM source code
            iterations: Number of iterations
            
        Returns:
            String containing cProfile stats
        """
        pr = cProfile.Profile()
        
        pr.enable()
        for _ in range(iterations):
            interp = Interpreter()
            interp.load(code)
            interp.run()
        pr.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        return s.getvalue()
    
    @staticmethod
    def _print_stats(results: Dict[str, Any]) -> None:
        """Print benchmark results"""
        print(f"\n{'='*60}")
        print(f"Profile: {results['name']}")
        print(f"{'='*60}")
        print(f"Instructions:        {results['instructions']}")
        print(f"Labels:              {results['labels']}")
        print(f"Iterations:          {results['iterations']}")
        print(f"Total time:          {results['total_time']*1000:.2f} ms")
        print(f"Avg time per run:    {results['avg_time']*1000:.2f} ms")
        print(f"Instructions/sec:    {results['instructions_per_second']:,.0f}")
        print(f"{'='*60}\n")
    
    @staticmethod
    def _print_benchmark_summary(results: Dict[str, Dict[str, Any]]) -> None:
        """Print benchmark summary for multiple files"""
        if not results:
            print("No files profiled")
            return
        
        print(f"\n{'='*80}")
        print(f"{'File':<30} {'Instrs':<10} {'Avg Time':<15} {'Instr/sec':<15}")
        print(f"{'='*80}")
        
        for filename, result in sorted(results.items()):
            print(f"{filename:<30} {result['instructions']:<10} "
                  f"{result['avg_time']*1000:>6.2f} ms      {result['instructions_per_second']:>10,.0f}")
        
        print(f"{'='*80}\n")


def main():
    """Command-line interface for profiler"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Profile WhitVM code execution')
    parser.add_argument('file', nargs='?', help='WhitVM file to profile')
    parser.add_argument('-i', '--iterations', type=int, default=1, 
                        help='Number of iterations (default: 1)')
    parser.add_argument('-c', '--cprofile', action='store_true',
                        help='Use cProfile for detailed profiling')
    parser.add_argument('-b', '--benchmark', action='store_true',
                        help='Run benchmark suite on example files')
    
    args = parser.parse_args()
    
    profiler = WhitVMProfiler()
    
    try:
        if args.benchmark:
            profiler.benchmark_suite()
        elif args.file:
            if args.cprofile:
                with open(args.file, 'r') as f:
                    code = f.read()
                print(profiler.profile_with_cprofile(code, args.iterations))
            else:
                profiler.profile_file(args.file, args.iterations)
        else:
            parser.print_help()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
