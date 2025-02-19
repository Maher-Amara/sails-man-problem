import ctypes
import numpy as np
import os

# Load the shared library
lib_path = os.path.join(os.path.dirname(__file__), 'libmatrix_mult.so')
_lib = ctypes.CDLL(lib_path)

# Define argument types for the C function
_lib.matrix_multiply.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=2, flags='C_CONTIGUOUS'),
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int
]
_lib.matrix_multiply.restype = None

def matrix_multiply_ctypes(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Multiply two matrices using ctypes implementation.
    
    Args:
        A: First matrix (m x n)
        B: Second matrix (n x p)
    Returns:
        Resulting matrix C (m x p)
    """
    if A.shape[1] != B.shape[0]:
        raise ValueError("Matrix dimensions do not match for multiplication")
    
    m, n = A.shape
    p = B.shape[1]
    
    # Create output array
    C = np.zeros((m, p), dtype=np.float64)
    
    # Call C function
    _lib.matrix_multiply(A, B, C, m, n, p)
    
    return C 