#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "matrix_mult.h"

double benchmark_matrix_multiply(int size, int iterations) {
    fprintf(stderr, "Allocating %dx%d matrices...\n", size, size);
    
    // Initialize random seed
    srand(42);  // Use consistent seed
    
    // Allocate matrices as flat arrays
    double* A = (double*)malloc(size * size * sizeof(double));
    if (!A) {
        fprintf(stderr, "Failed to allocate matrix A\n");
        return -1;
    }
    
    double* B = (double*)malloc(size * size * sizeof(double));
    if (!B) {
        free(A);
        fprintf(stderr, "Failed to allocate matrix B\n");
        return -1;
    }
    
    double* C = (double*)malloc(size * size * sizeof(double));
    if (!C) {
        free(A);
        free(B);
        fprintf(stderr, "Failed to allocate matrix C\n");
        return -1;
    }
    
    fprintf(stderr, "Initializing matrices with random values...\n");
    // Initialize with random values
    for(int i = 0; i < size * size; i++) {
        A[i] = (double)rand() / RAND_MAX;
        B[i] = (double)rand() / RAND_MAX;
    }
    
    fprintf(stderr, "Running warm-up iteration...\n");
    // Warm-up run
    matrix_multiply(A, B, C, size, size, size);
    
    fprintf(stderr, "Running %d benchmark iterations...\n", iterations);
    // Benchmark
    clock_t start = clock();
    for(int i = 0; i < iterations; i++) {
        matrix_multiply(A, B, C, size, size, size);
        if (iterations > 1) {  // Only show progress for multiple iterations
            fprintf(stderr, "  Progress: %d/%d iterations\n", i+1, iterations);
        }
    }
    clock_t end = clock();
    
    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC / iterations;
    fprintf(stderr, "Average time per iteration: %.6f seconds\n", time_taken);
    
    // Free memory
    fprintf(stderr, "Cleaning up memory...\n");
    free(A);
    free(B);
    free(C);
    
    return time_taken;
}

int main() {
    // Updated sizes array with more data points
    int sizes[] = {10, 50, 100, 200, 400, 600, 800, 1000, 1200, 1400, 1600};
    int n_sizes = sizeof(sizes) / sizeof(sizes[0]);
    
    // Open output file
    FILE* csv_file = fopen("../../results/pure_c_results.csv", "w");
    if (!csv_file) {
        fprintf(stderr, "Error: Could not open output file\n");
        return 1;
    }
    
    // Write header to CSV file
    const char* header = "Matrix Size,Time (seconds)\n";
    fprintf(stderr, "Writing header: %s", header);
    fprintf(csv_file, "%s", header);
    fflush(csv_file);
    
    for(int i = 0; i < n_sizes; i++) {
        int size = sizes[i];
        int iterations;
        
        // Adjust iterations based on size and previous results
        if (size <= 50) iterations = 100;        // Very small matrices
        else if (size <= 200) iterations = 50;   // Small matrices
        else if (size <= 400) iterations = 20;   // Medium matrices
        else if (size <= 600) iterations = 10;   // Large matrices (600x600)
        else if (size <= 800) iterations = 5;    // Large matrices (800x800)
        else if (size <= 1200) iterations = 3;   // Very large matrices (1200x1200)
        else iterations = 2;                      // Default case
        
        // Progress info to stderr
        fprintf(stderr, "\n=== Testing %dx%d matrices with %d iterations ===\n", 
                size, size, iterations);
        
        double time = benchmark_matrix_multiply(size, iterations);
        if (time >= 0) {  // Check for error
            // Prepare and verify the result string
            char result[100];
            snprintf(result, sizeof(result), "%d,%.6f\n", size, time);
            fprintf(stderr, "Writing to CSV: %s", result);
            
            // Write results to CSV file
            fprintf(csv_file, "%s", result);
            fflush(csv_file);
            
            // Progress info to stderr
            fprintf(stderr, "=== Completed %dx%d matrices ===\n", size, size);
        } else {
            fprintf(stderr, "Error benchmarking size %d\n", size);
            fclose(csv_file);
            return 1;
        }
    }
    
    fprintf(stderr, "\nAll benchmarks completed successfully!\n");
    fclose(csv_file);
    
    // Verify file was written
    FILE* check = fopen("../../results/pure_c_results.csv", "r");
    if (check) {
        char buffer[256];
        fprintf(stderr, "\nFile contents:\n");
        while (fgets(buffer, sizeof(buffer), check)) {
            fprintf(stderr, "%s", buffer);
        }
        fclose(check);
    } else {
        fprintf(stderr, "Could not read back the file!\n");
    }
    
    return 0;
} 