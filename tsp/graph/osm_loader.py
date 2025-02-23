"""
OpenStreetMap data loader for TSP optimization
Handles loading and processing of OpenStreetMap data using OSMnx
"""

import osmnx as ox
import networkx as nx
from typing import Tuple

class OSMDataLoader:
    """
    OpenStreetMap data loader for TSP optimization.
    Handles loading and processing of OSM data according to specifications in Osm.md.
    """
    
    def __init__(self, bbox: Tuple[float, float, float, float],
                 network_type: str = 'drive',
                 simplify: bool = False,
                 truncate_by_edge: bool = False,
                 retain_all: bool = True):
        """
        Initialize the OSM data loader
        
        Args:
            bbox: Tuple of (left, bottom, right, top) coordinates in degrees
            network_type: Type of network to download ('drive' only supported)
            simplify: Whether to simplify the graph topology
        """
        
        # Network settings
        if network_type != 'drive':
            raise ValueError("Only 'drive' network type is supported")
        self.network_type = network_type
        self.simplify = simplify
        self.truncate_by_edge = truncate_by_edge
        self.retain_all = retain_all
        
        # Validate and store bbox
        self._validate_bbox(bbox)
        self.bbox = bbox
        
        # Configure OSMnx settings
        ox.settings.use_cache = True
        ox.settings.log_console = False
        ox.settings.timeout = 180  # Increase timeout for larger areas
        ox.settings.cache_folder = '.cache'
        ox.settings.useful_tags_way = ['bridge', 'tunnel', 'oneway', 'lanes', 'ref', 'name',
                                     'highway', 'maxspeed', 'service', 'access', 'area',
                                     'landuse', 'width', 'est_width', 'junction']
    
    def _validate_bbox(self, bbox: Tuple[float, float, float, float]) -> None:
        """
        Validate bounding box coordinates
        
        Args:
            bbox: Tuple of (left, bottom, right, top) coordinates
        """
        if len(bbox) != 4:
            raise ValueError("bbox must be a tuple of 4 coordinates (left, bottom, right, top)")
            
        left, bottom, right, top = bbox
        
        if top <= bottom:
            raise ValueError("Top coordinate must be greater than bottom coordinate")
        if right <= left:
            raise ValueError("Right coordinate must be greater than left coordinate")
            
        # Check if coordinates are within valid ranges
        if not (-90 <= bottom <= 90) or not (-90 <= top <= 90):
            raise ValueError("Latitude values must be between -90 and 90 degrees")
        if not (-180 <= left <= 180) or not (-180 <= right <= 180):
            raise ValueError("Longitude values must be between -180 and 180 degrees")
    
    def _process_graph(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """Process and optimize the graph for TSP"""
        try:
            # Project to UTM for accurate distance calculations
            graph = ox.project_graph(graph)
            
            # Add edge speeds and travel times using routing module
            graph = ox.routing.add_edge_speeds(graph)
            graph = ox.routing.add_edge_travel_times(graph)
            
            # Pre-compute and store the largest strongly connected component
            components = list(nx.strongly_connected_components(graph))
            if not components:
                raise ValueError("No strongly connected components found in graph")
            largest_cc = max(components, key=len)
            
            # Store useful information in the graph object
            graph.graph['largest_cc'] = largest_cc
            graph.graph['projection_info'] = {
                'from_crs': "EPSG:4326",  # WGS84
                'to_crs': "EPSG:32631"    # UTM zone 31N
            }
            
            print(f"Processed graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
            print(f"Largest strongly connected component has {len(largest_cc)} nodes")
            return graph
            
        except Exception as e:
            print(f"Error processing graph: {e}")
            raise
    
    def load_network(self) -> nx.MultiDiGraph:
        """
        Load the road network using OSMnx
        
        Returns:
            NetworkX graph representing the road network
        """
        print("Loading network data...")
        
        # Download graph using bbox
        graph = ox.graph_from_bbox(
            bbox=self.bbox,
            network_type= self.network_type,
            simplify=self.simplify,
            truncate_by_edge=self.truncate_by_edge,
            retain_all=self.retain_all,
        )
        
        # Process and optimize the graph
        graph = self._process_graph(graph)
        
        print(f"Network loaded: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        return graph