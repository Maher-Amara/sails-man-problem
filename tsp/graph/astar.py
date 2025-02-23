import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Optional
import pyproj
from math import sqrt
import time

class Astar:
    """A* algorithm implementation for solving Traveling Salesman Problem."""
    
    def __init__(self, caching: bool = False):
        """Initialize the A* solver."""
        self._distance_matrix = None
        # Initialize coordinate transformers
        self.wgs84_to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32631", always_xy=True)
        # Cache for coordinate transformations
        self._coord_cache: Dict[Tuple[float, float], Tuple[float, float]] = {}
        # Cache for nearest nodes
        self._nearest_node_cache: Dict[Tuple[float, float], Tuple[int, Tuple[float, float]]] = {}
        # Cache for paths - now using nested dict for O(1) lookup
        self._path_cache: Dict[int, Dict[int, Tuple[List[int], float]]] = {}
        self.caching = caching
        
    def _convert_to_utm(self, lat: float, lon: float) -> Tuple[float, float]:
        """Convert WGS84 coordinates (lat, lon) to UTM coordinates (x, y)."""
        coord_key = (lat, lon)
        if coord_key in self._coord_cache:
            return self._coord_cache[coord_key]
            
        x, y = self.wgs84_to_utm.transform(lon, lat)
        self._coord_cache[coord_key] = (x, y)
        return x, y
        
    def _euclidean_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
    def _find_nearest_node(self, point: Tuple[float, float], coords_array: np.ndarray, node_ids: List) -> Tuple[int, Tuple[float, float]]:
        """
        Find the nearest node in the coords_array to the given point.

        Args:
            point: Point coordinates as (latitude, longitude)
            coords_array: Array of coordinates
            node_ids: List of node ids
            
        Returns:
            Tuple containing:
            - Nearest node ID
            - Nearest node coordinates (x, y)
        """
        # Convert input point to UTM
        point_x, point_y = self._convert_to_utm(point[0], point[1])
        
        # Calculate distances using vectorized operations
        distances = np.sqrt(np.sum((coords_array - np.array([point_x, point_y])) ** 2, axis=1))
        min_idx = np.argmin(distances)
        nearest_node = node_ids[min_idx]
        nearest_coords = tuple(coords_array[min_idx])
        
        if nearest_node is None:
            raise ValueError("Could not find nearest node in graph")
            
        return (nearest_node, nearest_coords)

    def batch_find_nearest_node(self, graph: nx.MultiDiGraph, points: List[Tuple[float, float]]) -> List[Tuple[int, Tuple[float, float]]]:
        """
        Find the nearest node for a batch of points efficiently.
        
        Args:
            graph: NetworkX graph
            points: List of (latitude, longitude) coordinates
            
        Returns:
            List of tuples containing:
            - Nearest node ID
            - Nearest node coordinates (x, y)
        """
        start_time = time.time()
        
        # First check cache for all points
        if self.caching:
            cached_results = [self._nearest_node_cache.get(point) for point in points]
            if all(result is not None for result in cached_results):
                print("Using cached nearest nodes")
                return cached_results
        
        # Pre-calculate UTM coordinates for all nodes once
        node_coords = []
        node_ids = []
        for node_id, data in graph.nodes(data=True):
            try:
                node_x = float(data['x'])
                node_y = float(data['y'])
                if not (np.isnan(node_x) or np.isnan(node_y)):
                    node_coords.append((node_x, node_y))
                    node_ids.append(node_id)
            except Exception as e:
                print(f"Failed to process node {node_id}: {str(e)}")
                continue
        
        coords_array = np.array(node_coords)
        
        # Process points that weren't in cache
        results = []
        for i, point in enumerate(points):
            if self.caching and cached_results[i] is not None:
                results.append(cached_results[i])
            else:
                result = self._find_nearest_node(point, coords_array, node_ids)
                if self.caching:
                    self._nearest_node_cache[point] = result
                results.append(result)
        
        execution_time = time.time() - start_time
        print(f"Found nearest nodes in {execution_time:.4f} seconds for {len(points)} points")
        
        return results

    def _get_cached_path(self, start_id: int, end_id: int) -> Optional[Tuple[List[int], float]]:
        """Get a path from cache if it exists."""
        if not self.caching:
            return None
        return self._path_cache.get(start_id, {}).get(end_id)

    def _cache_path(self, start_id: int, end_id: int, path_data: Tuple[List[int], float]) -> None:
        """Cache a path and its cost."""
        if not self.caching:
            return
        if start_id not in self._path_cache:
            self._path_cache[start_id] = {}
        self._path_cache[start_id][end_id] = path_data

    def _find_single_path(self, graph: nx.MultiDiGraph, start_id: int, end_id: int) -> Tuple[List[int], float]:
        """Find a single path between two nodes."""
        try:
            path = nx.astar_path(graph, start_id, end_id, weight='length')
            cost = sum(graph[path[k]][path[k+1]][0]['length'] for k in range(len(path)-1))
            return path, cost
        except nx.NetworkXNoPath:
            return [], float('inf')
        
    def batch_find_path(self, graph: nx.MultiDiGraph,
                       start_nodes: List[Tuple[int, Tuple[float, float]]],
                       end_nodes: List[Tuple[int, Tuple[float, float]]]
                       ) -> List[Tuple[List[int], float]]:
        """
        Find the shortest paths between multiple pairs of nodes using A* algorithm in batch.
        The graph should be pre-processed by OSMDataLoader (projected to UTM, with edge weights).
        Handles bidirectional paths separately as A→B may be different from B→A.
        
        Args:
            graph: NetworkX graph (already processed by OSMDataLoader)
            start_nodes: List of (node_id, coordinates) for start points
            end_nodes: List of (node_id, coordinates) for end points
            
        Returns:
            List of (path, cost) tuples
        """
        if len(start_nodes) != len(end_nodes):
            raise ValueError("Number of start and end nodes must match")
            
        start_time = time.time()
        total_paths = len(start_nodes)
        
        print(f"\nFinding {total_paths} paths...")
        
        # Extract just the node IDs from start/end nodes
        start_ids = [node_id for node_id, _ in start_nodes]
        end_ids = [node_id for node_id, _ in end_nodes]
        
        # Get the largest strongly connected component from pre-processed graph
        largest_cc = graph.graph.get('largest_cc')
        if largest_cc is None:
            print("Warning: Graph does not have pre-computed strongly connected component")
            components = list(nx.strongly_connected_components(graph))
            if not components:
                raise ValueError("No strongly connected components found in graph")
            largest_cc = max(components, key=len)
        
        # Process paths in batches for better performance
        batch_size = 100
        results = []
        cache_hits = 0
        cache_misses = 0
        
        for i in range(0, total_paths, batch_size):
            batch_end_idx = min(i + batch_size, total_paths)
            current_start_ids = start_ids[i:batch_end_idx]
            current_end_ids = end_ids[i:batch_end_idx]
            
            # Find paths for this batch
            for j, (start_id, end_id) in enumerate(zip(current_start_ids, current_end_ids)):
                try:
                    # Skip if nodes not in largest component
                    if start_id not in largest_cc or end_id not in largest_cc:
                        raise ValueError(f"Nodes {start_id} and/or {end_id} not in largest connected component")
                    
                    # Check cache first
                    cached_result = self._get_cached_path(start_id, end_id)
                    if cached_result is not None:
                        results.append(cached_result)
                        cache_hits += 1
                        continue
                        
                    cache_misses += 1
                    
                    # Compute new path
                    result = self._find_single_path(graph, start_id, end_id)
                    results.append(result)
                    
                    # Cache the result
                    self._cache_path(start_id, end_id, result)
                    
                except Exception as ex:
                    print(f"Warning: Failed to find path {i+j+1}/{total_paths}: {str(ex)}")
                    results.append(([], float('inf')))
        
        total_time = time.time() - start_time
        if self.caching:
            cache_hit_rate = (cache_hits / total_paths) * 100
            print(f"Cache statistics:")
            print(f"  Hits: {cache_hits}, Misses: {cache_misses}")
            print(f"  Hit rate: {cache_hit_rate:.1f}%")
            print(f"  Cache size: {sum(len(v) for v in self._path_cache.values())} paths")
        print(f"Found all paths in {total_time:.1f} seconds (avg {total_time/total_paths:.4f}s per path)")
        
        return results