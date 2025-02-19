import numpy as np
import time
import os
import sys
from typing import List
import matplotlib.pyplot as plt

# Add parent directory to path to import implementations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pure_python.matrix_mult import matrix_multiply_pure_python
from src.ctypes.matrix_mult_ctypes import matrix_multiply_ctypes
from src.c_extension.matrix_mult_ext import matrix_multiply as matrix_multiply_ext

def generate_random_matrix(m: int, n: int, seed: int = None) -> np.ndarray:
    """Generate random matrix with consistent seed"""
    if seed is not None:
        np.random.seed(seed)
    return np.random.rand(m, n)

def numpy_to_list(arr: np.ndarray) -> List[List[float]]:
    """Convert numpy array to nested Python list"""
    return arr.tolist()

def measure_performance(func, A: np.ndarray, B: np.ndarray, size: int) -> float:
    """Measure execution time of a function with adaptive iterations"""
    # Determine number of iterations based on size
    if size <= 50:
        iterations = 100        # Very small matrices
    elif size <= 200:
        iterations = 50         # Small matrices
    elif size <= 400:
        iterations = 20         # Medium matrices
    elif size <= 600:
        iterations = 10         # Large matrices (600x600)
    elif size <= 800:
        iterations = 5          # Large matrices (800x800)
    elif size <= 1200:
        iterations = 3          # Very large matrices (1400x1400)
    else:
        iterations = 2          # Default case
    
    print(f"Running {iterations} benchmark iterations...")
    
    # Convert to list for pure Python implementation
    if func == matrix_multiply_pure_python:
        A_input = numpy_to_list(A)
        B_input = numpy_to_list(B)
    else:
        # Ensure contiguous arrays for C implementations
        A_input = np.ascontiguousarray(A)
        B_input = np.ascontiguousarray(B)
    
    print("Running warm-up iteration...")
    # Warm-up run
    func(A_input, B_input)
    
    # Measure time using high-resolution timer
    times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        func(A_input, B_input)
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        if iterations > 1:  # Only show progress for multiple iterations
            print(f"  Progress: {i+1}/{iterations} iterations")
    
    # Remove outliers (optional)
    times.sort()
    trimmed_times = times[1:-1] if len(times) > 2 else times  # Remove fastest and slowest if possible
    
    avg_time = np.mean(trimmed_times)
    print(f"Average time per iteration: {avg_time:.6f} seconds")
    return avg_time

def read_pure_c_results():
    results = {}
    results_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'results', 'pure_c_results.csv')
    try:
        with open(results_path, 'r') as f:
            next(f)  # Skip header
            for line in f:
                size, time = line.strip().split(',')
                results[int(size)] = float(time)
    except FileNotFoundError:
        print("Error: Pure C results not found. Please run compile_all.sh first.")
        sys.exit(1)
    return results

def run_benchmarks():
    # Updated sizes array with more data points
    sizes = [10, 50, 100, 200, 400, 600, 800, 1000, 1200, 1400, 1600]
    
    # Read Pure C results first
    pure_c_results = read_pure_c_results()
    
    implementations = [
        ('Pure C', None),  # No function needed, using pre-computed results
        ('C Extension', matrix_multiply_ext),
        ('ctypes', matrix_multiply_ctypes),
        ('Pure Python', matrix_multiply_pure_python)
    ]
    
    results = {'Pure C': {'time': [pure_c_results[size] for size in sizes]}}
    results.update({name: {'time': []} for name, func in implementations if func})
    
    for size in sizes:
        print(f"\n=== Testing {size}x{size} matrices ===")
        seed = 42
        print(f"Generating {size}x{size} random matrices...")
        A = generate_random_matrix(size, size, seed)
        B = generate_random_matrix(size, size, seed)
        
        for name, func in implementations:
            if func is None:  # Skip Pure C as we already have results
                continue
                
            if size > 600 and name == 'Pure Python':
                print("Skipping Pure Python for matrices larger than 600x600...")
                if len(results['Pure Python']['time']) < len(sizes):
                    remaining = len(sizes) - len(results['Pure Python']['time'])
                    results['Pure Python']['time'].extend([float('inf')] * remaining)
                continue
                
            print(f"\nTesting {name}...")
            time_avg = measure_performance(func, A, B, size)
            results[name]['time'].append(time_avg)
            print(f"{name}: Time = {time_avg:.6f}s")
            print(f"=== Completed {size}x{size} matrices for {name} ===")
        
        sys.stdout.flush()
    
    print("\nAll benchmarks completed successfully!")
    plot_results(sizes, results)

def plot_results(sizes: List[int], results: dict):
    plt.figure(figsize=(10, 6))
    
    for name in results:
        plt.plot(sizes, results[name]['time'], marker='o', label=name)
    
    plt.xlabel('Matrix Size')
    plt.ylabel('Time (seconds)')
    plt.title('Matrix Multiplication Performance Comparison')
    plt.legend()
    plt.grid(True)
    plt.yscale('log')  # Use log scale for better visualization
    
    plt.tight_layout()
    plt.savefig('benchmark_results.png')
    plt.close()

if __name__ == "__main__":
    run_benchmarks()