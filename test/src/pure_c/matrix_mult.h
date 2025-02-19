#ifndef MATRIX_MULT_H
#define MATRIX_MULT_H

// Function for flat array implementation
void matrix_multiply(double* A, double* B, double* C, int m, int n, int p);

double** allocate_matrix(int rows, int cols);
void free_matrix(double** matrix, int rows);

#endif 