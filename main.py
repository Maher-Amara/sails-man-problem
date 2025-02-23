"""
Example script demonstrating the use of TSPGraphGenerator for finding optimal paths
between points of interest in Brussels.
"""

from tsp.graph.generator import TSPGraphGenerator
from tsp.graph.utils import random_places_geo, calculate_bounding_box, visualize_tsp_graph

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

    # calculate bounding box
    bbox = calculate_bounding_box([p[0] for p in points_with_labels], 0)
    # get points of interest
    points_with_labels.extend(random_places_geo(bbox, 3))

    # teke just the firs three points
    # points_with_labels = points_with_labels[:5]

    # Separate points and labels
    points = [p[0] for p in points_with_labels]
    labels = [p[1] for p in points_with_labels]
    
    # Create TSP graph generator
    generator = TSPGraphGenerator(points, labels)
    
    # Create visualization of the street network and points
    generator.visualize('diagrams/street_network.png')

    generator.visualize_node_mapping(save_path='diagrams/node_mapping')

    # Create the complete bidirectional graph with real street distances
    G = generator.create_distance_matrix()
    
    # Save the graph visualization
    visualize_tsp_graph(G, labels, save_path='diagrams/tsp_graph.png')

if __name__ == "__main__":
    main()
