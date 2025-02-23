from .osm_loader import OSMDataLoader
from .astar import Astar
from .utils import calculate_bounding_box, visualize_network_with_points, visualize_node_mapping, visualize_path, save_tsp_file
from typing import List, Tuple, Optional
import networkx as nx
import os

class TSPGraphGenerator:
    """
    A class to generate TSP (Traveling Salesman Problem) instances based on real street networks.
    
    This class takes a list of geographic coordinates as input and:
    - Downloads real street map data from OpenStreetMap API for the given locations
    - Calculates shortest paths between locations using A* algorithm
    - Provides visualization of the street network and points of interest
    
    Attributes:
        bbox (Tuple[float, float, float, float]): Bounding box containing all locations
        locations (List[Tuple[float, float]]): List of (lat, lon) coordinates to visit
        labels (List[str]): Labels for the locations
        graph (nx.MultiDiGraph): NetworkX graph of the street network
        astar (Astar): A* path finding algorithm implementation
    """

    def __init__(self, points: List[Tuple[float, float]], labels: Optional[List[str]] = None) -> None:
        """
        Initialize the TSP graph generator with a list of geographic coordinates.

        Args:
            points: List of (latitude, longitude) tuples representing locations to visit
            labels: Optional labels for the points. Defaults to "Point {i+1}"
        
        Raises:
            ValueError: If points list is empty
        """
        if not points:
            raise ValueError("Must provide at least one point")
            
        self.bbox = calculate_bounding_box(points)
        self.locations = points
        self.labels = labels if labels else [f"Point {i+1}" for i in range(len(points))]
        
        # Initialize OSM loader with optimized settings
        loader = OSMDataLoader(
            bbox=self.bbox,
            network_type='drive',
            simplify=True,  # Simplify the graph topology
            truncate_by_edge=True,  # Include edges that cross the bounding box
            retain_all=False,  # Remove disconnected components
        )
        self.graph = loader.load_network()
        self.astar = Astar(caching=True)

    def visualize(self, save_path: str = 'diagrams/street_network.png') -> None:
        """
        Create a visualization of the street network with points of interest.
        
        Args:
            save_path: Path where to save the visualization
        """
        visualize_network_with_points(self.graph, self.locations, self.labels, save_path)
        
    def visualize_node_mapping(self, save_path: str = 'diagrams/node_mapping') -> None:
        """
        Create a debug visualization showing how all points are mapped to their nearest network nodes.
        
        Args:
            save_path: Path where to save the visualization
        """
        # Get nearest nodes for all points in batch
        nearest_nodes = self.astar.batch_find_nearest_node(self.graph, self.locations)
        
        # Create visualizations for each point
        for (point, label, (_, proj_point)) in zip(self.locations, self.labels, nearest_nodes):
            visualize_node_mapping(self.graph, point, proj_point, label, save_path=f"{save_path}/{label}_mapping.png")
    
    def visualize_path(self,
                      path: List[int],
                      start: Tuple[float, float],
                      end: Tuple[float, float],
                      start_label: str,
                      end_label: str,
                      save_path: str = 'diagrams/paths') -> None:
        """
        Create a visualization showing the path between two points.
        
        Args:
            path: List of node IDs representing the path
            start: Starting coordinates (latitude, longitude)
            end: End coordinates (latitude, longitude)
            start_label: Label for the start point
            end_label: Label for the end point
            save_path: Path where to save the visualization
        """
        visualize_path(self.graph, path, start, end, start_label, end_label, save_path)

    def create_distance_matrix(self) -> nx.DiGraph:
        """
        Create a directed graph with A* distances between all points.
        
        Returns:
            NetworkX directed graph with distances between all points
        """
        # Create a directed graph
        G = nx.DiGraph()
        n = len(self.locations)
        
        # Get the largest strongly connected component first
        components = list(nx.strongly_connected_components(self.graph))
        if not components:
            raise ValueError("No strongly connected components found in graph")
            
        largest_cc = max(components, key=len)
        graph_scc = self.graph.subgraph(largest_cc).copy()
        
        print(f"\nUsing largest connected component with {len(graph_scc.nodes)} nodes")
        
        # Add nodes with labels and positions
        for i, (point, label) in enumerate(zip(self.locations, self.labels)):
            lat, lon = point
            G.add_node(i, 
                      pos=(lon, lat),  # Store lon/lat for visualization
                      coords=point,    # Store original coordinates
                      label=label)     # Store label
        
        # Find nearest nodes for all points
        print("\nFinding nearest nodes...")
        nearest_nodes = self.astar.batch_find_nearest_node(graph_scc, self.locations)
        
        # Create all pairs of indices, excluding self-loops
        pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
        start_nodes = [nearest_nodes[i] for i, _ in pairs]
        end_nodes = [nearest_nodes[j] for _, j in pairs]
        
        # Find all paths in batch
        print(f"\nCalculating paths between {n} points ({len(pairs)} paths)...")
        path_results = self.astar.batch_find_path(graph_scc, start_nodes, end_nodes)
        
        # Add edges to graph and fill distance matrix
        for (path, distance), (i, j) in zip(path_results, pairs):
            if path:  # Only add edge if path exists
                G.add_edge(i, j, 
                          weight=distance,    # Store distance as weight
                          path=path,          # Store path nodes
                          length=distance)    # Store length for compatibility
        return G
    
    def save_distance_matrix(self, graph: nx.DiGraph, location: str = 'be', save_path: str = 'assets/') -> None:
        """
        Save the distance matrix to a TSP file in TSPLIB format.
        
        Args:
            graph: NetworkX directed graph with distances between points
            save_path: Path where to save the TSP file
        """
        # Ensure the graph has all required attributes
        for i in range(len(self.locations)):
            if 'pos' not in graph.nodes[i]:
                raise ValueError(f"Node {i} missing 'pos' attribute")
            if 'label' not in graph.nodes[i]:
                raise ValueError(f"Node {i} missing 'label' attribute")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the graph in TSPLIB format
        save_tsp_file(graph, str(os.path.join(save_path, f"{location}{len(self.locations)}.tsp")))
