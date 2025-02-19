#!/bin/bash

# Create results directory if it doesn't exist
mkdir -p results

echo "Compiling Pure C implementation..."
cd src/pure_c
gcc -shared -o libmatrix_mult.so -fPIC matrix_mult.c
if [ $? -eq 0 ]; then
    echo "Pure C compilation successful"
else
    echo "Pure C compilation failed"
    exit 1
fi

echo -e "\nCompiling Pure C benchmark..."
gcc -O3 -o benchmark benchmark.c matrix_mult.c
if [ $? -eq 0 ]; then
    echo "Pure C benchmark compilation successful"
    # Run the benchmark and save results
    echo "Running Pure C benchmark..."
    # Redirect stdout to CSV file and stderr to terminal
    ./benchmark 2>&1 1>../../results/pure_c_results.csv
    if [ $? -eq 0 ]; then
        echo "Pure C benchmark results saved to results/pure_c_results.csv"
        # Verify the file is not empty
        if [ ! -s ../../results/pure_c_results.csv ]; then
            echo "Error: Pure C results file is empty"
            exit 1
        fi
    else
        echo "Error running Pure C benchmark"
        exit 1
    fi
else
    echo "Pure C benchmark compilation failed"
    exit 1
fi

echo -e "\nCompiling C Extension..."
cd ../c_extension
python3 setup.py build_ext --inplace
if [ $? -eq 0 ]; then
    echo "C Extension compilation successful"
else
    echo "C Extension compilation failed"
    exit 1
fi

echo -e "\nCompiling ctypes implementation..."
cd ../ctypes
gcc -shared -o libmatrix_mult.so -fPIC matrix_mult_lib.c
if [ $? -eq 0 ]; then
    echo "ctypes compilation successful"
else
    echo "ctypes compilation failed"
    exit 1
fi

echo -e "\nAll compilations completed successfully!"
