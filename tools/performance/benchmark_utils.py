#!/usr/bin/env python3
"""
Performance Benchmarking Utilities
性能基準測試工具

Provides utilities to measure and compare performance of optimized vs original code.
"""

import time
import functools
from typing import Callable, Any, Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    name: str
    execution_time: float
    iterations: int
    throughput: float = 0.0
    
    def __str__(self) -> str:
        result = [
            f"\n{'='*60}",
            f"Benchmark: {self.name}",
            f"{'='*60}",
            f"Execution time: {self.execution_time:.4f}s",
            f"Iterations: {self.iterations}",
        ]
        
        if self.throughput > 0:
            result.append(f"Throughput: {self.throughput:.2f} items/s")
        
        result.append(f"{'='*60}\n")
        return '\n'.join(result)


def benchmark(
    func: Callable,
    *args,
    iterations: int = 1,
    warmup: int = 0,
    name: Optional[str] = None,
    **kwargs
) -> BenchmarkResult:
    """Benchmark a function's execution time."""
    func_name = name or func.__name__
    
    # Warmup runs
    for _ in range(warmup):
        func(*args, **kwargs)
    
    # Actual benchmark
    start_time = time.time()
    result = None
    
    for _ in range(iterations):
        result = func(*args, **kwargs)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Calculate throughput if result is iterable
    throughput = 0.0
    if hasattr(result, '__len__'):
        try:
            item_count = len(result) * iterations
            throughput = item_count / execution_time if execution_time > 0 else 0
        except TypeError:
            pass
    
    return BenchmarkResult(
        name=func_name,
        execution_time=execution_time,
        iterations=iterations,
        throughput=throughput
    )


def compare_performance(
    original_func: Callable,
    optimized_func: Callable,
    test_data: Any = None,
    iterations: int = 1,
    warmup: int = 0
) -> Tuple[BenchmarkResult, BenchmarkResult, float]:
    """Compare performance of two functions."""
    print("🏁 Running performance comparison...")
    print(f"   Iterations: {iterations}")
    print(f"   Warmup: {warmup}")
    print()
    
    # Benchmark original
    print("⏱️  Benchmarking original function...")
    if test_data is not None:
        original_result = benchmark(
            original_func,
            test_data,
            iterations=iterations,
            warmup=warmup,
            name=f"{original_func.__name__} (Original)"
        )
    else:
        original_result = benchmark(
            original_func,
            iterations=iterations,
            warmup=warmup,
            name=f"{original_func.__name__} (Original)"
        )
    
    # Benchmark optimized
    print("⚡ Benchmarking optimized function...")
    if test_data is not None:
        optimized_result = benchmark(
            optimized_func,
            test_data,
            iterations=iterations,
            warmup=warmup,
            name=f"{optimized_func.__name__} (Optimized)"
        )
    else:
        optimized_result = benchmark(
            optimized_func,
            iterations=iterations,
            warmup=warmup,
            name=f"{optimized_func.__name__} (Optimized)"
        )
    
    # Calculate improvement
    if original_result.execution_time > 0:
        improvement = (
            (original_result.execution_time - optimized_result.execution_time)
            / original_result.execution_time
            * 100
        )
    else:
        improvement = 0.0
    
    # Print results
    print(original_result)
    print(optimized_result)
    print("📊 Performance Comparison:")
    print(f"   Original time: {original_result.execution_time:.4f}s")
    print(f"   Optimized time: {optimized_result.execution_time:.4f}s")
    print(f"   Improvement: {improvement:+.2f}%")
    
    if optimized_result.throughput > 0 and original_result.throughput > 0:
        throughput_improvement = (
            (optimized_result.throughput - original_result.throughput)
            / original_result.throughput
            * 100
        )
        print(f"   Throughput improvement: {throughput_improvement:+.2f}%")
    
    if optimized_result.execution_time > 0:
        speedup = original_result.execution_time / optimized_result.execution_time
        print(f"   Speedup: {speedup:.2f}x")
    else:
        print(f"   Speedup: N/A (optimized execution time too small to measure)")
    print()
    
    return original_result, optimized_result, improvement
