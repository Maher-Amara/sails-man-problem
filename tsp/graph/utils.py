from typing import List, Tuple
import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import os

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

def visualize_street_network(graph: nx.MultiDiGraph) -> None:
    """
    Visualize just the street network without points of interest
    
    Args:
        graph: NetworkX graph of the street network
    """
    print("Generating street network visualization...")
    
    # Create output directory if it doesn't exist
    os.makedirs('out', exist_ok=True)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plot the street network
    ox.plot_graph(
        graph,
        ax=ax,
        node_color='#336699',      # Blue nodes
        node_size=30,
        node_alpha=0.7,
        edge_color='#999999',      # Gray edges
        edge_linewidth=1,
        edge_alpha=0.5,
        bgcolor='white',
        show=False
    )
    
    # Add title
    ax.set_title('Street Network', fontsize=16, pad=20)
    
    # Save the plot to the out directory
    plt.savefig('out/street_network.png',
                dpi=300,
                bbox_inches='tight',
                pad_inches=0.5,
                facecolor='white')
    print("Visualization saved as 'out/street_network.png'")
    
    # Close the figure to free memory
    plt.close()