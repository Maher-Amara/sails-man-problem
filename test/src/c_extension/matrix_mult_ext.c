#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>

static PyObject* matrix_multiply_ext(PyObject* self, PyObject* args) {
    PyArrayObject *A, *B, *C;
    
    if (!PyArg_ParseTuple(args, "O!O!", &PyArray_Type, &A, &PyArray_Type, &B)) {
        return NULL;
    }
    
    int m = PyArray_DIM(A, 0);
    int n = PyArray_DIM(A, 1);
    int p = PyArray_DIM(B, 1);
    
    npy_intp dims[2] = {m, p};
    C = (PyArrayObject*)PyArray_SimpleNew(2, dims, NPY_DOUBLE);
    
    double *a_data = (double*)PyArray_DATA(A);
    double *b_data = (double*)PyArray_DATA(B);
    double *c_data = (double*)PyArray_DATA(C);
    
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < p; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += a_data[i * n + k] * b_data[k * p + j];
            }
            c_data[i * p + j] = sum;
        }
    }
    
    return (PyObject*)C;
}

static PyMethodDef MatrixMethods[] = {
    {"matrix_multiply", matrix_multiply_ext, METH_VARARGS, "Multiply two matrices"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef matrix_module = {
    PyModuleDef_HEAD_INIT,
    "matrix_mult_ext",
    NULL,
    -1,
    MatrixMethods
};

PyMODINIT_FUNC PyInit_matrix_mult_ext(void) {
    import_array();
    return PyModule_Create(&matrix_module);
} 