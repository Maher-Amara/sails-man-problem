from typing import List, Tuple, Optional
import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import os
import pyproj
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import random

def calculate_bounding_box(points: List[Tuple[float, float]], margin: float = 0.01) -> Tuple[float, float, float, float]:
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

def visualize_network_with_points(
    graph: nx.MultiDiGraph,
    points: List[Tuple[float, float]],
    labels: Optional[List[str]] = None,
    save_path: str = 'diagrams/street_network.png'
) -> None:
    """
    Create a single visualization showing both the street network and points of interest.
    
    Args:
        graph: NetworkX graph of the street network
        points: List of (latitude, longitude) coordinates for points of interest
        labels: Optional list of labels for the points
        save_path: Path where to save the visualization
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Create figure and axis
    _, ax = plt.subplots(figsize=(20, 20))  # Larger figure for better node visibility
    
    # Plot the street network with more prominent nodes
    ox.plot_graph(
        graph,
        ax=ax,
        node_color='#3498db',      # Blue nodes
        node_size=50,              # Larger nodes
        node_alpha=0.8,
        node_zorder=2,
        edge_color='#95a5a6',      # Light gray edges
        edge_linewidth=1,
        edge_alpha=0.5,
        bgcolor='white',
        show=False
    )
    
    # Convert points to GeoDataFrame
    geometry = [Point(lon, lat) for lat, lon in points]
    gdf_points = gpd.GeoDataFrame(
        {'geometry': geometry},
        crs=pyproj.CRS.from_epsg(4326)  # WGS84
    )
    
    # Project to the same CRS as the graph
    gdf_points = gdf_points.to_crs(graph.graph['crs'])
    
    # Plot points of interest with a more visible style
    scatter = ax.scatter(
        [p.x for p in gdf_points.geometry],
        [p.y for p in gdf_points.geometry],
        c='#e74c3c',              # Red points
        s=300,                    # Even larger size for POIs
        alpha=0.9,
        zorder=4,
        label='Points of Interest',
        edgecolor='white',        # White edge for better visibility
        linewidth=2
    )
    
    # Add labels if provided
    if labels:
        for idx, label in enumerate(labels):
            point = gdf_points.geometry.iloc[idx]
            # Add white background to text for better readability
            ax.annotate(
                label,
                (point.x, point.y),
                xytext=(8, 8),     # Offset text slightly more
                textcoords='offset points',
                fontsize=14,
                weight='bold',
                bbox=dict(
                    facecolor='white',
                    edgecolor='#666666',
                    alpha=0.8,
                    pad=0.5,
                    boxstyle='round,pad=0.5'
                ),
                zorder=5
            )
    
    # Customize the plot
    ax.set_title('Brussels Street Network & Points of Interest\n' +
                f'Network has {len(graph.nodes)} nodes and {len(graph.edges)} edges', 
                fontsize=16, 
                pad=20,
                weight='bold')
    
    # Add a legend
    ax.legend(loc='upper right',
             frameon=True,
             facecolor='white',
             edgecolor='#666666',
             fontsize=12)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches='tight',
        pad_inches=0.5,
        facecolor='white'
    )
    plt.close()

def save_tsp_file(graph, filename: str) -> None:
    """
    save a TSP file (traveling salesman problem) from the given tsp graph.
    
    Args:
        graph:
        filename: Name of the output file
    """
    pass

def load_tsp_file(filename):
    """
    Load a TSP file (traveling salesman problem) from the given file.
    
    Args:
        filename: Name of the input file
    """
    pass

def visualize_tsp_graph(G: nx.DiGraph,
                       labels: List[str],
                       save_path: str = 'diagrams/tsp_graph.png') -> None:
    """
    Visualize the complete directed TSP graph with points of interest and their interconnecting paths.
    
    Args:
        G: NetworkX directed graph representing the complete TSP graph
        points: List of (latitude, longitude) coordinates for points of interest
        labels: Labels for the points
        save_path: Path where to save the visualization
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Create figure and axis
    plt.figure(figsize=(15, 15))
    
    # Draw edges with weights as labels
    pos = nx.get_node_attributes(G, 'pos')
    
    # Draw edges with arrows to show direction
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5,
                          arrowsize=20, arrowstyle='->', connectionstyle='arc3, rad=0.1')
    
    # Add edge labels with distances
    edge_labels = nx.get_edge_attributes(G, 'weight')
    edge_labels = {k: f'{v:.0f}m' for k, v in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
    
    # Draw nodes and labels
    nx.draw_networkx_nodes(G, pos, node_color='red', node_size=100)
    label_pos = {k: (v[0], v[1] + 0.001) for k, v in pos.items()}  # Adjust label positions
    nx.draw_networkx_labels(G, label_pos, {i: label for i, label in enumerate(labels)}, font_size=10)
    
    # Set axis properties
    plt.title('TSP Graph with Real Street Distances\n(arrows indicate direction)')
    plt.axis('on')
    plt.grid(True)
    
    # Save the plot
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()

def visualize_points_of_interest(graph: nx.MultiDiGraph,
                               points: List[Tuple[float, float]],
                               labels: Optional[List[str]] = None,
                               save_path: str = 'diagrams/street_network_with_points.png') -> None:
    """
    Visualize the downloaded street network along with the specified points of interest.
    
    Creates a visualization showing:
    - The street network in the background
    - Points of interest as highlighted nodes
    
    Args:
        graph (nx.MultiDiGraph): NetworkX graph of the street network
        points (List[Tuple[float, float]]): List of (latitude, longitude) coordinates
        labels (Optional[List[str]], optional): Labels for the points. Defaults to None.
        save_path (str, optional): Path where to save the visualization.
            Defaults to 'diagrams/street_network_with_points.png'.
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Create figure and axis
    _, ax = plt.subplots(figsize=(15, 15))
    
    # Visualize the street network
    visualize_network_with_points(graph, points, labels)
    
    # Save the combined visualization
    ax.set_title('Street Network with Points of Interest', fontsize=16)
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
    plt.close()

def visualize_node_mapping(
    graph: nx.MultiDiGraph,
    point: Tuple[float, float],
    nearest_point: Tuple[float, float],
    point_label: str,
    save_path: str = 'diagrams/node_mapping.png'
) -> None:
    """
    Create a visualization showing how a point is mapped to the nearest node.
    
    Args:
        graph: NetworkX graph of the street network
        point: Original point as (latitude, longitude)
        nearest_point: Coordinates of the nearest node (x, y)
        point_label: Label for the point (e.g., "Grand Place")
        save_path: Path where to save the visualization
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Create figure and axis
    _, ax = plt.subplots(figsize=(20, 20))
    
    # Plot the street network
    ox.plot_graph(
        graph,
        ax=ax,
        node_color='#3498db',      # Blue nodes
        node_size=50,              # Larger nodes
        node_alpha=0.8,
        node_zorder=2,
        edge_color='#95a5a6',      # Light gray edges
        edge_linewidth=1,
        edge_alpha=0.5,
        bgcolor='white',
        show=False
    )
    
    # Convert point to GeoDataFrame
    gdf_point = gpd.GeoDataFrame(
        {'geometry': [Point(point[1], point[0])]},  # lon, lat
        crs=pyproj.CRS.from_epsg(4326)
    )
    gdf_point = gdf_point.to_crs(graph.graph['crs'])
    
    # Calculate the distance
    distance = ((gdf_point.geometry.iloc[0].x - nearest_point[0])**2 + 
               (gdf_point.geometry.iloc[0].y - nearest_point[1])**2)**0.5
    
    # Plot the connection line from original point to nearest node
    ax.plot(
        [gdf_point.geometry.iloc[0].x, nearest_point[0]],
        [gdf_point.geometry.iloc[0].y, nearest_point[1]],
        color='#e67e22',       # Orange line
        linestyle='--',        # Dashed line
        linewidth=2,
        alpha=0.8,
        zorder=2,
        label='Distance to nearest node'
    )
    
    # Add distance label on the connection line
    midpoint_x = (gdf_point.geometry.iloc[0].x + nearest_point[0]) / 2
    midpoint_y = (gdf_point.geometry.iloc[0].y + nearest_point[1]) / 2
    ax.annotate(
        f'{distance:.1f}m',
        (midpoint_x, midpoint_y),
        xytext=(0, 8),
        textcoords='offset points',
        ha='center',
        va='bottom',
        fontsize=12,
        weight='bold',
        bbox=dict(
            facecolor='white',
            edgecolor='#e67e22',
            alpha=0.8,
            pad=0.5,
            boxstyle='round,pad=0.5'
        ),
        zorder=3
    )
    
    # Plot the original point
    ax.scatter(
        gdf_point.geometry.iloc[0].x,
        gdf_point.geometry.iloc[0].y,
        c='#e74c3c',          # Red point
        s=300,                # Large size
        alpha=0.9,
        zorder=4,
        label='Original point',
        edgecolor='white',
        linewidth=2
    )
    
    # Highlight the nearest node
    ax.scatter(
        nearest_point[0],
        nearest_point[1],
        c='#2ecc71',          # Green point
        s=300,                # Large size
        alpha=0.9,
        zorder=4,
        label='Nearest node',
        edgecolor='white',
        linewidth=2
    )
    
    # Add point label
    ax.annotate(
        point_label,
        (gdf_point.geometry.iloc[0].x, gdf_point.geometry.iloc[0].y),
        xytext=(8, 8),
        textcoords='offset points',
        fontsize=14,
        weight='bold',
        bbox=dict(
            facecolor='white',
            edgecolor='#666666',
            alpha=0.8,
            pad=0.5,
            boxstyle='round,pad=0.5'
        ),
        zorder=5
    )
    
    # Add title with mapping information
    ax.set_title(
        f'Point Mapping: {point_label}\n' +
        f'Distance to nearest node: {distance:.2f}m',
        fontsize=16,
        pad=20,
        weight='bold'
    )
    
    # Add legend
    ax.legend(
        loc='upper right',
        frameon=True,
        facecolor='white',
        edgecolor='#666666',
        fontsize=12
    )
    
    # Adjust the view to focus on the relevant area with margin
    margin = 100  # meters
    all_x = [gdf_point.geometry.iloc[0].x, nearest_point[0]]
    all_y = [gdf_point.geometry.iloc[0].y, nearest_point[1]]
    
    # Filter out any NaN or Inf values
    valid_x = [x for x in all_x if not (np.isnan(x) or np.isinf(x))]
    valid_y = [y for y in all_y if not (np.isnan(y) or np.isinf(y))]
    
    if not valid_x or not valid_y:
        raise ValueError("No valid coordinates for view limits")
        
    ax.set_xlim(min(valid_x) - margin, max(valid_x) + margin)
    ax.set_ylim(min(valid_y) - margin, max(valid_y) + margin)
    
    # Save with high DPI
    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches='tight',
        pad_inches=0.5,
        facecolor='white'
    )
    plt.close()

def visualize_path(
    graph: nx.MultiDiGraph,
    path: List[int],
    start_point: Tuple[float, float],
    end_point: Tuple[float, float],
    start_label: str,
    end_label: str,
    save_path: str = 'diagrams/path'
) -> None:
    """
    Create a visualization showing the path between two points on the street network.
    
    Args:
        graph: NetworkX graph of the street network
        path: List of node IDs representing the path
        start_point: Starting coordinates (latitude, longitude)
        end_point: End coordinates (latitude, longitude)
        start_label: Label for the start point
        end_label: Label for the end point
        save_path: Path where to save the visualization
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(f"{save_path}"), exist_ok=True)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(20, 20))
    
    # Plot the street network
    ox.plot_graph(
        graph,
        ax=ax,
        node_color='#cccccc',
        node_size=20,
        node_alpha=0.5,
        edge_color='#666666',
        edge_linewidth=1,
        edge_alpha=0.5,
        bgcolor='white',
        show=False
    )
    
    # Convert points to GeoDataFrame
    points = [start_point, end_point]
    geometry = [Point(lon, lat) for lat, lon in points]
    gdf_points = gpd.GeoDataFrame(
        {'geometry': geometry},
        crs=pyproj.CRS.from_epsg(4326)  # WGS84
    )
    gdf_points = gdf_points.to_crs(graph.graph['crs'])
    
    # Plot the path segments
    total_length = 0
    all_x_coords = []
    all_y_coords = []
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        
        # Get node coordinates directly
        u_x, u_y = float(graph.nodes[u]['x']), float(graph.nodes[u]['y'])
        v_x, v_y = float(graph.nodes[v]['x']), float(graph.nodes[v]['y'])
        
        # Check each coordinate individually
        invalid_coords = False
        for coord in [u_x, u_y, v_x, v_y]:
            if np.isnan(coord) or np.isinf(coord):
                invalid_coords = True
                break
        
        if invalid_coords:
            print(f"Invalid coordinates for nodes {u}-{v}, skipping")
            continue
        
        # Calculate progress through the path for color gradient
        progress = i / (len(path) - 2) if len(path) > 2 else 0
        
        # Color gradient from blue to green
        color = (
            0.2 * (1 - progress),  # Red component
            0.6 + 0.2 * progress,  # Green component
            0.8 * (1 - progress)   # Blue component
        )
        
        # Plot the edge as a straight line between nodes
        ax.plot(
            [u_x, v_x],
            [u_y, v_y],
            color=color,
            linewidth=4,
            alpha=0.8,
            zorder=3,
            solid_capstyle='round'
        )
        
        # Add coordinates to the list for view limits
        all_x_coords.extend([u_x, v_x])
        all_y_coords.extend([u_y, v_y])
        
        # Add to total length
        edge_length = np.sqrt((v_x - u_x)**2 + (v_y - u_y)**2)
        total_length += edge_length
    
    # Add start/end point coordinates to ensure they're included in the view
    all_x_coords.extend([gdf_points.geometry[0].x, gdf_points.geometry[1].x])
    all_y_coords.extend([gdf_points.geometry[0].y, gdf_points.geometry[1].y])
    
    if not all_x_coords or not all_y_coords:
        raise ValueError("No valid coordinates found for visualization")
    
    # Plot start point and its mapping
    start_node_x = float(graph.nodes[path[0]]['x'])
    start_node_y = float(graph.nodes[path[0]]['y'])
    
    # Plot connection line from start point to its node
    ax.plot(
        [gdf_points.geometry[0].x, start_node_x],
        [gdf_points.geometry[0].y, start_node_y],
        color='#e67e22',       # Orange line
        linestyle='--',        # Dashed line
        linewidth=2,
        alpha=0.8,
        zorder=2,
        label='Point mapping'
    )
    
    # Plot start point
    ax.scatter(
        [gdf_points.geometry[0].x],
        [gdf_points.geometry[0].y],
        c='#e74c3c',          # Red for start
        s=300,
        alpha=0.9,
        zorder=5,
        label='Start point',
        edgecolor='white',
        linewidth=2
    )
    
    # Plot start node
    ax.scatter(
        [start_node_x],
        [start_node_y],
        c='#f1c40f',          # Yellow for nodes
        s=200,
        alpha=0.9,
        zorder=4,
        label='Network nodes',
        edgecolor='white',
        linewidth=2,
        marker='s'            # Square marker
    )
    
    # Plot end point and its mapping
    end_node_x = float(graph.nodes[path[-1]]['x'])
    end_node_y = float(graph.nodes[path[-1]]['y'])
    
    # Plot connection line from end point to its node
    ax.plot(
        [gdf_points.geometry[1].x, end_node_x],
        [gdf_points.geometry[1].y, end_node_y],
        color='#e67e22',       # Orange line
        linestyle='--',        # Dashed line
        linewidth=2,
        alpha=0.8,
        zorder=2
    )
    
    # Plot end point
    ax.scatter(
        [gdf_points.geometry[1].x],
        [gdf_points.geometry[1].y],
        c='#2ecc71',          # Green for end
        s=300,
        alpha=0.9,
        zorder=5,
        label='End point',
        edgecolor='white',
        linewidth=2
    )
    
    # Plot end node
    ax.scatter(
        [end_node_x],
        [end_node_y],
        c='#f1c40f',          # Yellow for nodes
        s=200,
        alpha=0.9,
        zorder=4,
        edgecolor='white',
        linewidth=2,
        marker='s'            # Square marker
    )
    
    # Add labels
    for i, (point, label) in enumerate(zip(gdf_points.geometry, [start_label, end_label])):
        ax.annotate(
            label,
            (point.x, point.y),
            xytext=(8, 8),
            textcoords='offset points',
            fontsize=14,
            weight='bold',
            bbox=dict(
                facecolor='white',
                edgecolor='#666666',
                alpha=0.8,
                pad=0.5,
                boxstyle='round,pad=0.5'
            ),
            zorder=6
        )
    
    # Calculate mapping distances
    start_mapping_dist = np.sqrt(
        (gdf_points.geometry[0].x - start_node_x)**2 + 
        (gdf_points.geometry[0].y - start_node_y)**2
    )
    end_mapping_dist = np.sqrt(
        (gdf_points.geometry[1].x - end_node_x)**2 + 
        (gdf_points.geometry[1].y - end_node_y)**2
    )
    
    # Add title with path information
    ax.set_title(
        f'Path from {start_label} to {end_label}\n' +
        f'Total path length: {total_length:.0f}m through {len(path)} nodes\n' +
        f'Start point mapping: {start_mapping_dist:.0f}m, End point mapping: {end_mapping_dist:.0f}m',
        fontsize=16,
        pad=20,
        weight='bold'
    )
    
    # Add legend
    ax.legend(
        loc='upper right',
        frameon=True,
        facecolor='white',
        edgecolor='#666666',
        fontsize=12
    )
    
    # Adjust the view to show the entire path with margin
    margin = 100  # meters
    ax.set_xlim(min(all_x_coords) - margin, max(all_x_coords) + margin)
    ax.set_ylim(min(all_y_coords) - margin, max(all_y_coords) + margin)
    
    # Save with high DPI
    plt.savefig(
        f"{save_path}/{start_label}_{end_label}.png",
        dpi=300,
        bbox_inches='tight',
        pad_inches=0.5,
        facecolor='white'
    )
    plt.close()

def random_places_geo(bbox: Tuple[float, float, float, float], n: int) -> List[Tuple[Tuple[float, float], str]]:
    """
    Generate a specified number of real places within a bounding box (bbox)
    from an OpenStreetMap dataset API using OSMnx.
    
    Args:
        bbox: Tuple of (left, bottom, right, top) coordinates in degrees.
        n: Number of random points to generate.
        
    Returns:
        List of tuples containing ((latitude, longitude), label) for each point.
    """
    # Create tags for places we want to fetch (amenities, tourism spots, etc.)
    tags = {
        'amenity': ['restaurant', 'cafe', 'bar', 'pub', 'fast_food', 'museum', 'theatre', 'cinema', 'library', 'marketplace'],
        'tourism': ['attraction', 'museum', 'artwork', 'gallery', 'viewpoint', 'hotel'],
        'leisure': ['park', 'garden', 'sports_centre']
    }
    
    # Get features within the bounding box
    features = ox.features_from_bbox(
        bbox,
        tags=tags
    )
    
    # If no features found, return empty list
    if len(features) == 0:
        print("No features found in the specified bounding box")
        return []
    
    # Filter features to only include those with names
    features = features[features['name'].notna()]
    
    if len(features) == 0:
        print("No named features found in the specified bounding box")
        return []
    
    # Ensure we don't sample more points than available
    num_samples = min(n, len(features))
    
    if num_samples < n:
        print(f"Only found {num_samples} named places, less than requested {n}")
    
    # Randomly select features
    random.seed(1)  # For reproducibility
    sampled_features = features.sample(n=num_samples, random_state=1)
    
    points = []
    for idx, row in sampled_features.iterrows():
        # Get coordinates from the geometry
        lon, lat = row.geometry.centroid.coords[0]
        name = row['name']  # We know this exists because we filtered for it
        points.append(((lat, lon), name))
    
    return points