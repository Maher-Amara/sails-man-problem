"""
Example of using TSPGraphGenerator to process road networks
"""

from tsp.graph.generator import TSPGraphGenerator
from typing import List, Tuple

def main():
    """Main entry point with command line argument parsing"""
    # Points of interest with their labels
    points_with_labels = [
        ((50.8468, 4.3517), "Grand Place"),
        ((50.8550, 4.3753), "European Parliament"),
        ((50.8427, 4.3677), "Palace of Justice"),
        ((50.8589, 4.3407), "Royal Palace"),
        ((50.8472, 4.3573), "Manneken Pis"),
    ]
    
    # Separate points and labels
    points = [p[0] for p in points_with_labels]
    
    # Initialize TSP graph generator
    generator = TSPGraphGenerator(points)
    
    # Log network statistics
    print(f"Loaded graph with {len(generator.graph.nodes)} nodes and {len(generator.graph.edges)} edges")

    # Visualize the street network
    generator.visualize_street_network()

if __name__ == "__main__":
    main()
