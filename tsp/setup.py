from setuptools import setup, Extension, find_packages
import os

# Read README.md
with open(os.path.join(os.path.dirname(__file__), "..", "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

# Common compiler flags for optimization
COMPILER_FLAGS = [
    "-O3",  # Highest optimization level
    "-Wall",  # Enable all warnings
    "-Wextra",  # Enable extra warnings
    "-Wno-unused-parameter",  # Don't warn about unused parameters
    "-fPIC",  # Position Independent Code
    "-std=c99",  # Use C99 standard
]

def get_numpy_include():
    try:
        import numpy as np
        return np.get_include()
    except ImportError:
        return None

numpy_include = get_numpy_include()
if numpy_include is None:
    extensions = []  # Skip C extensions if numpy is not available
else:
    # Define all C extensions with correct source paths
    extensions = [
        Extension(
            "c_extension.astar",
            sources=["c_extension/astar.c"],
            include_dirs=[numpy_include, "c_extension"],
            extra_compile_args=COMPILER_FLAGS,
        ),
        
    ]

setup(
    name="optimeet-tsp",
    version="1.0.0",
    description="OptiMeet - Optimizing sales meeting schedules using TSP algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Maher Amara",
    author_email="maheramara32@gmail.com",
    url="https://github.com/Maher-Amara/sails-man-problem",
    packages=find_packages(),
    ext_modules=extensions,
    include_package_data=True,
    install_requires=[
        "networkx>=2.8.0",
        "osmnx>=1.3.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "folium>=0.12.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "scipy>=1.7.0",
        "python-dateutil>=2.8.0",
        "Cython>=0.29.0",
        "folium>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "pytest-cov>=2.12.0",
            "sphinx>=4.0.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: C",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Office/Business :: Scheduling",
    ],
    keywords="tsp, scheduling, optimization, sales, routing",
    setup_requires=['numpy>=1.21.0'],
    package_data={
        'tsp': [
            'graph/*.py',
            'c_extension/*.c',
            'c_extension/*.h',
        ],
    },
)