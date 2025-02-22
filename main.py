"""
Example of using OSMDataLoader to process road networks
"""

from tsp.graph.osm_loader import OSMDataLoader
from tsp.utils.visualize import visualize_street_network
from typing import List, Tuple
import networkx as nx

def calculate_bounding_box(points: List[Tuple[float, float]], margin: float = 0.1) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box that contains all points with a margin
    
    Args:
        points: List of (latitude, longitude) coordinates
        margin: Margin to add around the points as a percentage (0.1 = 10%)
        
    Returns:
        Tuple of (left, bottom, right, top) coordinates in degrees
    """
    if not points:
        raise ValueError("No points provided")
        
    # Extract coordinates
    lats, lons = zip(*points)
    
    # Calculate basic bounds
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    # Calculate the size of the area
    lat_size = max_lat - min_lat
    lon_size = max_lon - min_lon
    
    # Add margin
    margin_lat = lat_size * margin
    margin_lon = lon_size * margin
    
    # Ensure minimum area size for very close points
    min_size = 0.01  # About 1km
    if lat_size < min_size:
        margin_lat = max(margin_lat, min_size/2)
    if lon_size < min_size:
        margin_lon = max(margin_lon, min_size/2)
    
    # Return as (left, bottom, right, top)
    return (
        min_lon - margin_lon,  # left
        min_lat - margin_lat,  # bottom
        max_lon + margin_lon,  # right
        max_lat + margin_lat   # top
    )

def load_street_network(points_of_interest: List[Tuple[float, float]],
                       simplify: bool = True) -> nx.MultiDiGraph:
    """
    Load street network for a given set of points and visualize it
    
    Args:
        points_of_interest: List of (latitude, longitude) coordinates
        point_labels: List of labels for the points of interest
        simplify: Whether to simplify the graph topology
        visualize_points: Whether to include points of interest in visualization
    """
    # Calculate bounds from points
    bbox = calculate_bounding_box(points_of_interest)
    
    # Initialize the OSM data loader
    osm_loader = OSMDataLoader(
        bbox=bbox,
        network_type='drive',
        simplify=simplify
    )
    
    # Load road network
    print("Loading road network...")
    graph = osm_loader.load_network()
    
    # Log network statistics
    print(f"Loaded graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    
    return graph

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
    
    # Load the street network with labeled points
    graph = load_street_network(
        points_of_interest=points,
        simplify=True  # Set to False to show only the street network
    )

    visualize_street_network(graph)

if __name__ == "__main__":
    main()
