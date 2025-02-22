from .osm_loader import OSMDataLoader
from .astar import Astar
from .utils import calculate_bounding_box, visualize_street_network
from typing import List, Tuple

class TSPGraphGenerator:
    def __init__(self, points: List[Tuple[float, float]]):
        self.bbox = calculate_bounding_box(points)
        self.locations = points
        self.loader = OSMDataLoader(self.bbox,
            network_type='drive',
            simplify=True
            )
        self.graph = self.loader.load_network()
        self.astar = Astar()

    def visualize_street_network(self):
        visualize_street_network(self.graph)

    def calculate_distances(self):
        distances = {}
        for i in range(len(self.locations)):
            for j in range(i + 1, len(self.locations)):
                start = self.locations[i]
                end = self.locations[j]
                distance = self.astar.find_path(self.graph, start, end)  # Assuming find_path is a method in Astar
                distances[(start, end)] = distance
        return distances