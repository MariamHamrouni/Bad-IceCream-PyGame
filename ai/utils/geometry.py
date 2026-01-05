# Emplacement: ai/utils/geometry.py
import math
from dataclasses import dataclass
from typing import Tuple, Union

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Rectangle:
    """Représentation géométrique simple pour les calculs hors Pygame"""
    x: int
    y: int
    width: int
    height: int

    @property
    def left(self): return self.x
    @property
    def right(self): return self.x + self.width
    @property
    def top(self): return self.y
    @property
    def bottom(self): return self.y + self.height
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def intersects(self, other: 'Rectangle') -> bool:
        """Vérifie l'intersection avec un autre rectangle"""
        return not (self.right <= other.left or 
                    self.left >= other.right or 
                    self.bottom <= other.top or 
                    self.top >= other.bottom)

    def contains(self, point: Tuple[int, int]) -> bool:
        """Vérifie si un point est dans le rectangle"""
        px, py = point
        return self.left <= px < self.right and self.top <= py < self.bottom

# --- Fonctions Utilitaires ---

def distance_between(p1: Union[Tuple, Point], p2: Union[Tuple, Point]) -> float:
    """Distance Euclidienne (Vol d'oiseau) - Précis"""
    x1, y1 = p1 if isinstance(p1, tuple) else (p1.x, p1.y)
    x2, y2 = p2 if isinstance(p2, tuple) else (p2.x, p2.y)
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    """Distance de Manhattan (Grille) - Rapide pour A*"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def rectangles_overlap(r1: Tuple[int, int, int, int], r2: Tuple[int, int, int, int]) -> bool:
    """Helper rapide pour tuples (x, y, w, h)"""
    return not (r1[0] + r1[2] <= r2[0] or 
                r1[0] >= r2[0] + r2[2] or 
                r1[1] + r1[3] <= r2[1] or 
                r1[1] >= r2[1] + r2[3])

def calculate_centroid(points: list) -> Tuple[int, int]:
    """Calcule le centre géométrique d'un groupe de points"""
    if not points:
        return (0, 0)
    sum_x = sum(p[0] for p in points)
    sum_y = sum(p[1] for p in points)
    return (int(sum_x / len(points)), int(sum_y / len(points)))