import numpy as np
from typing import List
import time

def matrix_multiply_pure_python(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    """
    Multiply two matrices using pure Python implementation.
    
    Args:
        A: First matrix (m x n)
        B: Second matrix (n x p)
    Returns:
        Resulting matrix C (m x p)
    """
    if not A or not B or not A[0] or not B[0]:
        raise ValueError("Input matrices cannot be empty")
    
    m, n = len(A), len(A[0])
    n2, p = len(B), len(B[0])
    
    if n != n2:
        raise ValueError("Matrix dimensions do not match for multiplication")
    
    # Initialize result matrix with zeros
    C = [[0.0 for _ in range(p)] for _ in range(m)]
    
    # Perform matrix multiplication
    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    
    return C 