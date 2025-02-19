#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void matrix_multiply(double* A, double* B, double* C, int m, int n, int p) {
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < p; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[i * n + k] * B[k * p + j];
            }
            C[i * p + j] = sum;
        }
    }
}

double** allocate_matrix(int rows, int cols) {
    double** matrix = (double**)malloc(rows * sizeof(double*));
    if (!matrix) return NULL;
    
    for (int i = 0; i < rows; i++) {
        matrix[i] = (double*)malloc(cols * sizeof(double));
        if (!matrix[i]) {
            // Clean up already allocated memory
            for (int j = 0; j < i; j++) {
                free(matrix[j]);
            }
            free(matrix);
            return NULL;
        }
    }
    return matrix;
}

void free_matrix(double** matrix, int rows) {
    if (matrix) {
        for (int i = 0; i < rows; i++) {
            if (matrix[i]) {
                free(matrix[i]);
            }
        }
        free(matrix);
    }
} 