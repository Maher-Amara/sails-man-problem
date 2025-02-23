from .osm_loader import OSMDataLoader
from .astar import Astar
from .utils import calculate_bounding_box, visualize_network_with_points, visualize_node_mapping
from typing import List, Tuple, Optional

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
        
        # Load the street network
        loader = OSMDataLoader(self.bbox, network_type='drive', simplify=False)
        self.graph = loader.load_network()
        self.astar = Astar()

    def find_optimal_path(self,
                         start: Tuple[float, float],
                         end: Tuple[float, float]) -> Tuple[List[int], float]:
        """
        Find the optimal path between two points using A* algorithm.
        
        Args:
            start: Starting point as (latitude, longitude)
            end: Destination point as (latitude, longitude)
            
        Returns:
            Tuple containing:
                - List of node IDs representing the optimal path
                - Total path distance in meters
                
        Raises:
            ValueError: If no path can be found between the points
        """
        try:
            path, distance = self.astar.find_path(self.graph, start, end)
            return path, distance
        except Exception as e:
            raise ValueError(f"Could not find path between points: {str(e)}")

    def visualize(self, save_path: str = 'diagrams/street_network.png') -> None:
        """
        Create a visualization of the street network with points of interest.
        
        Args:
            save_path: Path where to save the visualization
        """
        visualize_network_with_points(self.graph, self.locations, self.labels, save_path)
        
    def visualize_node_mapping(self, 
                             point: Tuple[float, float],
                             label: str,
                             save_path: str) -> None:
        """
        Create a debug visualization showing how a point is mapped to a network node.
        
        Args:
            point: Point coordinates as (latitude, longitude)
            label: Label for the point (e.g., "Grand Place")
            save_path: Path where to save the visualization
        """
        # Find the mapped edge and projected point using the same logic as in A*
        start_node, end_node, proj_point = self.astar.find_nearest_node(self.graph, point)
        visualize_node_mapping(self.graph, point, (start_node, end_node), proj_point, label, save_path)
        
    def visualize_path(self,
                      path: List[int],
                      start: Tuple[float, float],
                      end: Tuple[float, float],
                      start_label: str,
                      end_label: str,
                      save_path: str = 'diagrams/path.png') -> None:
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
        from .utils import visualize_path
        visualize_path(self.graph, path, start, end, start_label, end_label, save_path)