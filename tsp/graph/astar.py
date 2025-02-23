import numpy as np
from tsp.c_extension import astar
import networkx as nx
from typing import List, Tuple
import numpy.typing as npt
import logging
import pyproj
from math import sqrt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Astar:
    """A* algorithm implementation for solving Traveling Salesman Problem."""
    
    def __init__(self):
        """Initialize the A* solver."""
        self._distance_matrix = None
        # Initialize coordinate transformers
        self.wgs84_to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32631", always_xy=True)
        
    def _convert_to_utm(self, lat: float, lon: float) -> Tuple[float, float]:
        """Convert WGS84 coordinates (lat, lon) to UTM coordinates (x, y)."""
        x, y = self.wgs84_to_utm.transform(lon, lat)
        return x, y
        
    def _euclidean_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
    def _project_point_to_line(self, point: Tuple[float, float], 
                               line_start: Tuple[float, float], 
                               line_end: Tuple[float, float]) -> Tuple[float, float, float]:
        """
        Project a point onto a line segment and return the projected point and distance.
        
        Args:
            point: Point to project (x, y)
            line_start: Start point of line segment (x, y)
            line_end: End point of line segment (x, y)
            
        Returns:
            Tuple containing:
                - x coordinate of projected point
                - y coordinate of projected point
                - distance from original point to projected point
        """
        try:
            # Convert to numpy arrays for easier vector operations
            p = np.array(point)
            a = np.array(line_start)
            b = np.array(line_end)
            
            # Vector from a to b
            ab = b - a
            # Vector from a to p
            ap = p - a
            
            # Calculate the projection
            ab_length_squared = np.dot(ab, ab)
            
            if ab_length_squared == 0:
                # If the line segment is actually a point
                return a[0], a[1], np.linalg.norm(ap)
                
            # Calculate the position of the projection along the line segment
            t = np.dot(ap, ab) / ab_length_squared
            
            if t < 0:
                # Point projects before start of line segment
                proj = a
            elif t > 1:
                # Point projects after end of line segment
                proj = b
            else:
                # Point projects onto line segment
                proj = a + t * ab
                
            # Calculate distance from point to projection
            distance = np.linalg.norm(p - proj)
            
            return float(proj[0]), float(proj[1]), float(distance)
            
        except Exception as e:
            logger.warning(f"Error in point projection: {str(e)}")
            # Return the closest endpoint as a fallback
            dist_to_start = np.linalg.norm(p - a)
            dist_to_end = np.linalg.norm(p - b)
            if dist_to_start < dist_to_end:
                return float(a[0]), float(a[1]), float(dist_to_start)
            else:
                return float(b[0]), float(b[1]), float(dist_to_end)
        
    def _project_point_to_linestring(self, point: Tuple[float, float], 
                                    linestring: List[Tuple[float, float]]) -> Tuple[float, float, float]:
        """
        Project a point onto a linestring (multi-segment line) and return the projected point and distance.
        
        Args:
            point: Point to project (x, y)
            linestring: List of (x, y) coordinates representing the street geometry
            
        Returns:
            Tuple containing:
                - x coordinate of projected point
                - y coordinate of projected point
                - distance from original point to projected point
        """
        if not linestring:
            raise ValueError("Empty linestring provided")
            
        if len(linestring) < 2:
            return linestring[0][0], linestring[0][1], self._euclidean_distance(
                point[0], point[1], linestring[0][0], linestring[0][1]
            )
            
        # Find the closest segment in the linestring
        min_distance = float('inf')
        nearest_proj = None
        
        # Check each segment in the linestring
        for i in range(len(linestring) - 1):
            try:
                proj_x, proj_y, dist = self._project_point_to_line(
                    point,
                    linestring[i],
                    linestring[i + 1]
                )
                
                if dist < min_distance:
                    min_distance = dist
                    nearest_proj = (proj_x, proj_y)
            except Exception as e:
                logger.warning(f"Failed to project point onto segment {i}: {str(e)}")
                continue
        
        # If no valid projection found, use the closest endpoint
        if nearest_proj is None:
            distances = [
                (self._euclidean_distance(point[0], point[1], x, y), (x, y))
                for x, y in linestring
            ]
            min_distance, nearest_proj = min(distances, key=lambda x: x[0])
            logger.info(f"No valid projection found, using closest endpoint at distance {min_distance:.2f}m")
        
        return nearest_proj[0], nearest_proj[1], min_distance
        
    def find_nearest_node(self, graph: nx.MultiDiGraph, point: Tuple[float, float]) -> Tuple[int, int, Tuple[float, float]]:
        """
        Find the nearest node in the graph to the given point.
        
        Args:
            graph: NetworkX graph of the street network
            point: Point coordinates as (latitude, longitude)
            
        Returns:
            Tuple containing:
                - ID of the nearest node
                - Same ID (for compatibility)
                - Coordinates of the nearest node (x, y)
        """
        # Convert input point to UTM
        point_x, point_y = self._convert_to_utm(point[0], point[1])
        
        # Find the nearest node by Euclidean distance
        nearest_node = None
        min_distance = float('inf')
        nearest_coords = None
        
        for node_id, data in graph.nodes(data=True):
            try:
                node_x = float(data['x'])
                node_y = float(data['y'])
                
                # Skip nodes with invalid coordinates
                if np.isnan(node_x) or np.isnan(node_y):
                    continue
                    
                distance = self._euclidean_distance(point_x, point_y, node_x, node_y)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = node_id
                    nearest_coords = (node_x, node_y)
                    
            except Exception as e:
                logger.warning(f"Failed to process node {node_id}: {str(e)}")
                continue
        
        if nearest_node is None:
            raise ValueError("Could not find nearest node in graph")
            
        logger.info(f"Found nearest node {nearest_node} at distance {min_distance:.2f}m")
        
        # Return the same node ID twice for compatibility with existing code
        return nearest_node, nearest_node, nearest_coords
        
    def find_path(self, graph: nx.MultiDiGraph,
                  start: tuple[float, float],
                  end: tuple[float, float]) -> tuple[List[int], float]:
        """
        Find the shortest path between two coordinates using A* algorithm.
        
        Args:
            graph: NetworkX graph representing the road network
            start: Starting coordinates (latitude, longitude)
            end: Destination coordinates (latitude, longitude)
            
        Returns:
            Tuple containing the path (list of node indices) and total cost
        """
        # Convert input coordinates from WGS84 to UTM
        start_x, start_y = self._convert_to_utm(start[0], start[1])
        end_x, end_y = self._convert_to_utm(end[0], end[1])
        
        logger.info(f"Start UTM coordinates: ({start_x:.2f}, {start_y:.2f})")
        logger.info(f"End UTM coordinates: ({end_x:.2f}, {end_y:.2f})")
        
        # Convert graph to distance matrix
        nodes = list(graph.nodes(data=True))
        n = len(nodes)
        node_to_idx = {node_id: i for i, (node_id, _) in enumerate(nodes)}
        
        # Find nearest edges and projection points
        start_u, start_v, start_proj = self.find_nearest_node(graph, start)
        end_u, end_v, end_proj = self.find_nearest_node(graph, end)
        
        # Create distance matrix
        dist_matrix = np.full((n + 2, n + 2), np.inf)  # Add 2 nodes for projected points
        
        # Fill the main part of the matrix
        for u, v, data in graph.edges(data=True):
            i, j = node_to_idx[u], node_to_idx[v]
            dist_matrix[i, j] = data.get('length', np.inf)
            if not data.get('oneway', False):
                dist_matrix[j, i] = data.get('length', np.inf)
        
        # Add connections for projected points
        start_idx = n  # Index for projected start point
        end_idx = n + 1  # Index for projected end point
        
        # Connect start projection to its edge endpoints
        start_u_idx = node_to_idx[start_u]
        start_v_idx = node_to_idx[start_v]
        start_u_dist = self._euclidean_distance(
            start_proj[0], start_proj[1],
            float(graph.nodes[start_u]['x']), float(graph.nodes[start_u]['y'])
        )
        start_v_dist = self._euclidean_distance(
            start_proj[0], start_proj[1],
            float(graph.nodes[start_v]['x']), float(graph.nodes[start_v]['y'])
        )
        dist_matrix[start_idx, start_u_idx] = start_u_dist
        dist_matrix[start_idx, start_v_idx] = start_v_dist
        dist_matrix[start_u_idx, start_idx] = start_u_dist
        dist_matrix[start_v_idx, start_idx] = start_v_dist
        
        # Connect end projection to its edge endpoints
        end_u_idx = node_to_idx[end_u]
        end_v_idx = node_to_idx[end_v]
        end_u_dist = self._euclidean_distance(
            end_proj[0], end_proj[1],
            float(graph.nodes[end_u]['x']), float(graph.nodes[end_u]['y'])
        )
        end_v_dist = self._euclidean_distance(
            end_proj[0], end_proj[1],
            float(graph.nodes[end_v]['x']), float(graph.nodes[end_v]['y'])
        )
        dist_matrix[end_idx, end_u_idx] = end_u_dist
        dist_matrix[end_idx, end_v_idx] = end_v_dist
        dist_matrix[end_u_idx, end_idx] = end_u_dist
        dist_matrix[end_v_idx, end_idx] = end_v_dist
        
        # Solve path using A*
        path_indices, cost = astar.solve_astar(dist_matrix, n + 2, start_idx, end_idx)
        
        if path_indices is None or len(path_indices) == 0:
            raise ValueError("No path found between start and end points")
            
        # Convert indices back to original nodes, excluding the artificial start/end nodes
        path = []
        for i in path_indices:
            if i < n:  # Only include real nodes
                path.append(nodes[i][0])
        
        return path, cost