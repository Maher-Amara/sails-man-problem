"""
C extensions for OptiMeet TSP algorithms
"""

from .astar import solve_astar

__all__ = [
    "solve_astar",
]