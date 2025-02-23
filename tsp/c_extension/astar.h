#ifndef ASTAR_H
#define ASTAR_H

#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdbool.h>

// Configuration constants
#define INITIAL_QUEUE_CAPACITY 4096  // Increased from 1024
#define QUEUE_GROWTH_FACTOR 2
#define MAX_EDGES_PER_VERTEX 64     // Increased from 32
#define MAX_QUEUE_SIZE 200000       // Increased from 50000
#define PRUNE_THRESHOLD 0.95        // Less aggressive pruning
#define PRUNE_TARGET 0.7            // Less aggressive pruning target
#define MAX_ITERATIONS 500000       // Increased from 150000

// Core node structure for A*
typedef struct Node {
    int* path;              // Current path
    int path_length;        // Length of current path
    double g_cost;         // Cost from start to current node
    double h_cost;         // Estimated cost from current node to goal
    double f_cost;         // Total cost (g_cost + h_cost)
} Node;

// Priority queue for open set
typedef struct {
    Node** nodes;
    int size;
    int capacity;
} PriorityQueue;

// Graph representation
typedef struct {
    double** costs;        // Cost matrix
    int n_vertices;
} Graph;

// Main A* state
typedef struct {
    Graph* graph;
    PriorityQueue* open_list;
    double best_cost;
    int* best_path;
    int n_cities;
    int start_idx;         // Starting node index
    int end_idx;          // Goal node index
} AStarState;

// Core function declarations
static PyObject* solve_astar(PyObject* self, PyObject* args);
Node* create_node(int* path, int path_length, double g_cost, double h_cost);
void free_node(Node* node);
double calculate_heuristic(AStarState* state, Node* node);
void expand_node(AStarState* state, Node* node);
bool is_goal(Node* node, AStarState* state);

// Priority queue operations
PriorityQueue* create_priority_queue(int capacity);
void free_priority_queue(PriorityQueue* queue);
void push_node(PriorityQueue* queue, Node* node);
Node* pop_node(PriorityQueue* queue);

// Node comparison function for sorting
static int compare_nodes(const Node** a, const Node** b);

#endif // ASTAR_H 