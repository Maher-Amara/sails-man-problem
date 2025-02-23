#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <string.h>
#include "astar.h"

#define INITIAL_QUEUE_CAPACITY 1024
#define QUEUE_GROWTH_FACTOR 2
#define MAX_EDGES_PER_VERTEX 32
#define MAX_QUEUE_SIZE 50000   // Reduced from 100000
#define PRUNE_THRESHOLD 0.9    // Start pruning earlier at 90% capacity
#define PRUNE_TARGET 0.5       // More aggressive pruning to 50% capacity
#define MAX_ITERATIONS 150000  // Maximum number of iterations before giving up

PriorityQueue* create_priority_queue(int capacity) {
    PriorityQueue* queue = (PriorityQueue*)malloc(sizeof(PriorityQueue));
    queue->nodes = (Node**)malloc(capacity * sizeof(Node*));
    queue->capacity = capacity;
    queue->size = 0;
    return queue;
}

void free_priority_queue(PriorityQueue* queue) {
    for (int i = 0; i < queue->size; i++) {
        free_node(queue->nodes[i]);
    }
    free(queue->nodes);
    free(queue);
}

static void swap_nodes(Node** a, Node** b) {
    Node* temp = *a;
    *a = *b;
    *b = temp;
}

static void sift_up(PriorityQueue* queue, int idx) {
    while (idx > 0) {
        int parent = (idx - 1) / 2;
        if (queue->nodes[idx]->f_cost < queue->nodes[parent]->f_cost) {
            swap_nodes(&queue->nodes[idx], &queue->nodes[parent]);
            idx = parent;
        } else {
            break;
        }
    }
}

static void sift_down(PriorityQueue* queue, int idx) {
    while (true) {
        int smallest = idx;
        int left = 2 * idx + 1;
        int right = 2 * idx + 2;

        if (left < queue->size && queue->nodes[left]->f_cost < queue->nodes[smallest]->f_cost)
            smallest = left;
        if (right < queue->size && queue->nodes[right]->f_cost < queue->nodes[smallest]->f_cost)
            smallest = right;

        if (smallest == idx) break;

        swap_nodes(&queue->nodes[idx], &queue->nodes[smallest]);
        idx = smallest;
    }
}

void push_node(PriorityQueue* queue, Node* node) {
    if (queue->size == queue->capacity) {
        queue->capacity *= 2;
        queue->nodes = (Node**)realloc(queue->nodes, queue->capacity * sizeof(Node*));
    }
    queue->nodes[queue->size] = node;
    sift_up(queue, queue->size);
    queue->size++;
}

Node* pop_node(PriorityQueue* queue) {
    if (queue->size == 0) return NULL;
    
    Node* result = queue->nodes[0];
    queue->size--;
    if (queue->size > 0) {
        queue->nodes[0] = queue->nodes[queue->size];
        sift_down(queue, 0);
    }
    return result;
}

Node* create_node(int* path, int path_length, double g_cost, double h_cost) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->path = (int*)malloc(path_length * sizeof(int));
    memcpy(node->path, path, path_length * sizeof(int));
    node->path_length = path_length;
    node->g_cost = g_cost;
    node->h_cost = h_cost;
    node->f_cost = g_cost + h_cost;
    return node;
}

void free_node(Node* node) {
    free(node->path);
    free(node);
}

bool is_goal(Node* node, AStarState* state) {
    return node->path[node->path_length - 1] == state->end_idx;
}

double calculate_heuristic(AStarState* state, Node* node) {
    int current = node->path[node->path_length - 1];
    
    // Direct distance to goal
    double h_cost = state->graph->costs[current][state->end_idx];
    if (h_cost == DBL_MAX) {
        // If no direct path, use minimum outgoing edge cost as estimate
        h_cost = DBL_MAX;
        for (int i = 0; i < state->n_cities; i++) {
            if (state->graph->costs[current][i] < h_cost) {
                h_cost = state->graph->costs[current][i];
            }
        }
    }
    return h_cost;
}

void expand_node(AStarState* state, Node* node) {
    if (is_goal(node, state)) {
        double total_cost = node->g_cost;
        if (total_cost < state->best_cost) {
            state->best_cost = total_cost;
            memcpy(state->best_path, node->path, node->path_length * sizeof(int));
        }
        return;
    }
    
    int current = node->path[node->path_length - 1];
    bool* visited = (bool*)calloc(state->n_cities, sizeof(bool));
    
    // Mark visited cities
    for (int i = 0; i < node->path_length; i++) {
        visited[node->path[i]] = true;
    }
    
    // Try all unvisited neighbors
    for (int next = 0; next < state->n_cities; next++) {
        if (!visited[next] && state->graph->costs[current][next] != DBL_MAX) {
            double new_g_cost = node->g_cost + state->graph->costs[current][next];
            
            // Create new path
            int* new_path = (int*)malloc((node->path_length + 1) * sizeof(int));
            memcpy(new_path, node->path, node->path_length * sizeof(int));
            new_path[node->path_length] = next;
            
            // Create and evaluate new node
            Node* new_node = create_node(new_path, node->path_length + 1, new_g_cost, 0);
            new_node->h_cost = calculate_heuristic(state, new_node);
            
            if (new_node->f_cost < state->best_cost) {
                push_node(state->open_list, new_node);
            } else {
                free_node(new_node);
            }
            
            free(new_path);
        }
    }
    
    free(visited);
}

static PyObject* solve_astar(PyObject* self, PyObject* args) {
    PyArrayObject* cost_matrix;
    int n_vertices;
    int start_idx;
    int end_idx;
    
    if (!PyArg_ParseTuple(args, "O!iii", &PyArray_Type, &cost_matrix, &n_vertices, &start_idx, &end_idx))
        return NULL;
    
    // Initialize A* state
    AStarState* state = (AStarState*)malloc(sizeof(AStarState));
    state->n_cities = n_vertices;
    state->best_cost = DBL_MAX;
    state->best_path = (int*)malloc(n_vertices * sizeof(int));
    state->open_list = create_priority_queue(INITIAL_QUEUE_CAPACITY);
    state->start_idx = start_idx;
    state->end_idx = end_idx;
    
    // Create graph
    state->graph = (Graph*)malloc(sizeof(Graph));
    state->graph->n_vertices = n_vertices;
    state->graph->costs = (double**)malloc(n_vertices * sizeof(double*));
    for (int i = 0; i < n_vertices; i++) {
        state->graph->costs[i] = (double*)malloc(n_vertices * sizeof(double));
        for (int j = 0; j < n_vertices; j++) {
            double cost = *(double*)PyArray_GETPTR2(cost_matrix, i, j);
            state->graph->costs[i][j] = isinf(cost) ? DBL_MAX : cost;
        }
    }
    
    // Create initial node
    int* initial_path = (int*)malloc(sizeof(int));
    initial_path[0] = start_idx;  // Start from specified start node
    Node* start_node = create_node(initial_path, 1, 0.0, 0.0);
    start_node->h_cost = calculate_heuristic(state, start_node);
    push_node(state->open_list, start_node);
    free(initial_path);
    
    // Main A* loop
    int iterations = 0;
    while (state->open_list->size > 0 && iterations < MAX_ITERATIONS) {
        Node* current = pop_node(state->open_list);
        if (current == NULL) break;
        
        expand_node(state, current);
        free_node(current);
        iterations++;
    }
    
    // Create return values
    PyObject* path = NULL;
    if (state->best_cost < DBL_MAX) {
        int path_length = 0;
        for (int i = 0; i < n_vertices; i++) {
            if (state->best_path[i] == end_idx) {
                path_length = i + 1;
                break;
            }
        }
        
        path = PyList_New(path_length);
        for (int i = 0; i < path_length; i++) {
            PyList_SET_ITEM(path, i, PyLong_FromLong(state->best_path[i]));
        }
    } else {
        path = PyList_New(0);  // Empty path if no solution found
    }
    
    PyObject* result = Py_BuildValue("(Od)", path, state->best_cost);
    
    // Cleanup
    Py_DECREF(path);
    for (int i = 0; i < n_vertices; i++) {
        free(state->graph->costs[i]);
    }
    free(state->graph->costs);
    free(state->graph);
    free(state->best_path);
    free_priority_queue(state->open_list);
    free(state);
    
    return result;
}

static PyMethodDef AStarMethods[] = {
    {"solve_astar", solve_astar, METH_VARARGS, "Solve TSP using A* algorithm"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef astar_module = {
    PyModuleDef_HEAD_INIT,
    "astar",
    "A* algorithm for solving TSP",
    -1,
    AStarMethods
};

PyMODINIT_FUNC PyInit_astar(void) {
    import_array();
    return PyModule_Create(&astar_module);
} 