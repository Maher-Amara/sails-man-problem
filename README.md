# OptiMeet (Traveling Salesman Problem)

OptiMeet is an algorithm designed to find the optimal schedule for a salesman visiting clients. It acts as a scheduling recommendation tool for sales teams, optimizing routes and meeting times worldwide.

## Roles

- Sales Person: The person who is selling the product.
- Client: The person who is buying the product.
- Agent: The person who is scheduling the meetings.

## How it works

The agent will call the client to schedule a time for the sales person to visit the client at their location.
The agent will use the OptiMeet algorithm to find the best time for the sales person to visit the client.
The sales person will use the OptiMeet Mobile App to navigate to the client's location.

## Project Components

### 1. Generation of a Traveling Salesman Problem (TSP) graph

This module facilitates the generation of a TSP graph using real-world data from OpenStreetMap for any location worldwide:

1. **Data Collection and Network Generation**:
   - Collects road network data from OpenStreetMap (OSM) format via OSMnx
   - Supports any location worldwide using Bounding box coordinates
   - Generates a NetworkX MultiDiGraph optimized for path finding
   - Handles non-planar elements like bridges, tunnels, and interchanges
   - Ensures strong connectivity by retaining largest connected component
   - Supports topology simplification for complex intersections
   - Automatic error handling and retries for data retrieval

2. **Data Processing and Graph Enhancement**:
   - Converts OSM data into a graph structure where:
     - Nodes (intersections) contain:
       - Unique OSM identifier
       - UTM projected coordinates (x, y)
       - Geographic coordinates (latitude, longitude)
       - Intersection type indicators
     - Edges (roads) contain:
       - Physical distance in meters
       - Travel time in seconds
       - Speed limits and road type
       - Directional flow (one-way/bidirectional)
       - Road geometry information
   - Projects coordinates to UTM for accurate distance calculations
   - Validates network connectivity and handles edge cases
   - Processes edge speeds and travel times automatically
   - Supports smart caching with configurable timeout

3. **A* Path Finding Implementation**:
   - Implements A* algorithm with components:
     - Heuristic function h(n): Estimates remaining distance to goal
     - Cost function g(n): Tracks actual travel costs
     - Evaluation function f(n) = g(n) + h(n)
   - Optimizes for:
     - Geographic distance calculations
     - Real road networks and travel times
     - Road type characteristics
     - One-way streets and turn restrictions
   - Provides efficient path finding between any two points
   - Handles both time-based and distance-based optimization
   - Includes robust error handling and validation

4. **Visualization and Analysis Tools**:
   - Interactive web-based visualization features:
     - Color-coded road classifications
     - Node representation of intersections
     - Edge representation of street segments
     - Multiple zoom levels and layer management
   - Support for:
     - Points of interest marking
     - Distance measurements
     - Area overview
     - Interactive navigation controls
   - Route visualization capabilities:
     - Path geometry display
     - Turn-by-turn directions
     - Travel time estimates
     - Distance calculations

### 2. Benchmarking TSP Algorithms

To select the optimal algorithm for our scheduling system, we evaluate various TSP algorithms based on accuracy and execution time:

### Exact Algorithms

- **Brute Force**: \(O(n!)\), optimal for small \(n\).
- **Held-Karp**: \(O(n^2 \times 2^n)\), optimal, feasible up to \(n \approx 20\).
- **Branch and Bound**: \(O(n!)\) worst case, often faster, optimal.

### Approximation Algorithms (Symmetric TSP)

- **Christofides**: \(O(n^3)\), 1.5-approximation.
- **Double-Tree**: \(O(n^2)\), 2-approximation.

### Approximation (Asymmetric TSP, Triangle Inequality)

- **Frieze-Galil-Margolies**: \(O(n^3)\), 2-approximation.

### Heuristics

- **Nearest Neighbor**: \(O(n^2)\), no guarantee of optimality.
- **2-opt**: \(O(n^2)\) per iteration, no guarantee of optimality.

### Metaheuristics

- **Genetic Algorithms**: Variable polynomial time complexity, no guarantee of optimality.

### 3. Final Product: OptiMeet Scheduling Module

The final product is a Python module that optimizes meeting schedules globally by recommending the best time slot for a new meeting location, given an existing schedule.

### Input

- List of locations from the existing schedule (coordinates or addresses)
- New location to be added to the schedule
- Current schedule timing constraints
- Optional location-specific parameters (e.g., traffic patterns, time zones)

### Process Flow

1. **Dynamic TSP Graph Generation**:
   - Downloads and processes road network data for any location
   - Uses A* algorithm to calculate realistic travel times
   - Considers local road networks and traffic patterns
   - Caches data for frequently accessed areas

2. **Schedule Optimization**:
   - Solves the updated TSP problem using the optimal algorithm
   - Considers existing schedule constraints and time windows
   - Handles time zone differences and local business hours
   - Minimizes total travel time and maximizes schedule efficiency

3. **Time Slot Recommendation**:
   - Analyzes the optimized route
   - Identifies feasible time slots that maintain schedule integrity
   - Considers local business hours and customs
   - Recommends optimal meeting times that minimize disruption

### Output

- Recommended time slot for the new meeting
- Updated optimized route with turn-by-turn directions
- Estimated travel times between locations
- Interactive visualization of the route and schedule
