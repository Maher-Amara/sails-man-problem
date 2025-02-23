"""
Example script demonstrating the use of TSPGraphGenerator for finding optimal paths
between points of interest in Brussels.
"""

from tsp.graph.generator import TSPGraphGenerator
import networkx as nx
import numpy as np
from tsp.graph.utils import visualize_tsp_graph

def create_distance_matrix(generator: TSPGraphGenerator, points: list[tuple[float, float]], labels: list[str]) -> tuple[nx.Graph, np.ndarray]:
    """Create a complete bidirectional graph with A* distances between all points."""
    # Create a complete graph
    G = nx.Graph()
    n = len(points)
    distance_matrix = np.zeros((n, n))
    
    # Add nodes with labels
    for i, (point, label) in enumerate(zip(points, labels)):
        G.add_node(i, pos=point, label=label)
    
    # Calculate distances between all pairs of points
    print("\nCalculating distances between all points...")
    for i in range(n):
        for j in range(i + 1, n):  # Only calculate each pair once
            try:
                path, distance = generator.find_optimal_path(points[i], points[j])
                # Add edge with distance and path
                G.add_edge(i, j, weight=distance, path=path)
                # Store in distance matrix (both directions since it's bidirectional)
                distance_matrix[i][j] = distance
                distance_matrix[j][i] = distance
                print(f"Distance from {labels[i]} to {labels[j]}: {distance:.0f} meters")
            except Exception as e:
                print(f"Warning: Could not find path between {labels[i]} and {labels[j]}: {str(e)}")
                # Use Euclidean distance as fallback
                lat1, lon1 = points[i]
                lat2, lon2 = points[j]
                euclidean_dist = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111000  # Rough conversion to meters
                G.add_edge(i, j, weight=euclidean_dist)
                distance_matrix[i][j] = euclidean_dist
                distance_matrix[j][i] = euclidean_dist
    
    return G, distance_matrix

def main():
    """Main entry point for the Brussels points of interest example."""
    
    # Define points of interest in Brussels with their labels
    points_with_labels = [
        ((50.8467862, 4.3479732), "Grand Place"),
        ((50.8467289, 4.3509936), "Hotel Amigo"),
        ((50.8468831, 4.3532189), "Théâtre Royal de Toone"),
        ((50.8550, 4.3753), "European Parliament"),
        ((50.8427, 4.3677), "Palace of Justice"),
        ((50.8589, 4.3407), "Royal Palace"),
        ((50.8472, 4.3573), "Manneken Pis"),
    ]

    # Separate points and labels
    points = [p[0] for p in points_with_labels]
    labels = [p[1] for p in points_with_labels]
    
    # Create TSP graph generator
    generator = TSPGraphGenerator(points, labels)
    
    # Create visualization of the street network and points
    generator.visualize('diagrams/street_network.png')
    
    # Generate node mapping visualizations for all points
    print("\nGenerating node mapping visualizations for all points...")
    for i, (point, label) in enumerate(zip(points, labels)):
        generator.visualize_node_mapping(
            point, 
            label, 
            f'diagrams/node_mapping/{i}_{label.lower().replace(" ", "_")}.png'
        )
    
    # Create the complete bidirectional graph with real street distances
    G, distance_matrix = create_distance_matrix(generator, points, labels)
    
    # Print the distance matrix
    print("\nDistance matrix (meters):")
    print("From/To:", " ".join(f"{label:>15}" for label in labels))
    for i, row in enumerate(distance_matrix):
        print(f"{labels[i]:8}", " ".join(f"{dist:15.0f}" for dist in row))
    
    # Save the graph visualization
    visualize_tsp_graph(G, points, labels, save_path='diagrams/tsp_graph.png')

if __name__ == "__main__":
    main()
