from setuptools import setup, Extension
import numpy as np

matrix_module = Extension(
    'matrix_mult_ext',
    sources=['matrix_mult_ext.c'],
    include_dirs=[np.get_include()]
)

setup(
    name='matrix_mult_ext',
    version='1.0',
    ext_modules=[matrix_module]
) 