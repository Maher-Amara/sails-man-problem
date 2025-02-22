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

1. **Data Collection**:
   - Collects road network data from OpenStreetMap (OSM) format
   - Supports any location worldwide using either:
     - Place names (e.g., "Paris, France", "New York, USA")
     - Custom bounding box coordinates
   - Caches data locally for improved performance

2. **Data Processing**:
   - Converts the OSM data into a graph format where intersections are nodes and roads are edges
   - Handles different road types and their characteristics
   - Calculates realistic travel times based on road types and speed limits

3. **Shortest Path Calculation**:
   - Utilizes the A* algorithm to calculate the shortest path between each pair of nodes
   - Takes into account actual road networks and travel times
   - Supports both time-based and distance-based optimization

4. **Visualization**:
   - Interactive web-based visualization of road networks
   - Color-coded road types (highways, major roads, minor roads)
   - Optional display of intersections and points of interest
   - Support for viewing the optimized route

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

## Usage Example

```python
from tsp.graph.osm_loader import OSMDataLoader

# Create TSP instance for any location
loader = OSMDataLoader("Tokyo, Japan")
graph = loader.load_network()

# Add points of interest
points = [
    (35.6762, 139.6503),  # Shinjuku
    (35.6586, 139.7454),  # Tokyo Tower
    # ... more points
]

# Generate and visualize the route
instance = loader.create_tsp_instance(points)
loader.visualize_network(graph)
```
