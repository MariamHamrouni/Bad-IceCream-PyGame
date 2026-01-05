# Emplacement: ai/enemies/a_star.py
import heapq
import math
from typing import List, Tuple, Optional, Set

class Node:
    """Représente une case dans la grille de pathfinding"""
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0  # Coût du départ à ici
        self.h = 0  # Heuristique (estimation jusqu'à l'arrivée)
        self.f = 0  # Score total (g + h)

    def __lt__(self, other):
        return self.f < other.f

class AStarPathfinder:
    def __init__(self, grid_width=20, grid_height=15, cell_size=40):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size

    def find_path(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 obstacles: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Trouve le chemin le plus court.
        start_pos/end_pos/obstacles sont en PIXELS.
        Retourne une liste de points en PIXELS (le centre des cases).
        """
        # 1. Conversion Pixels -> Grille
        start_node = Node(*self._to_grid(start_pos))
        end_node = Node(*self._to_grid(end_pos))
        
        # Optimisation : Si départ == arrivée, on ne bouge pas
        if start_node.x == end_node.x and start_node.y == end_node.y:
            return []

        # Conversion des obstacles en Set de coordonnées grille pour recherche rapide O(1)
        obstacles_grid = set()
        for obs in obstacles:
            ox, oy = self._to_grid(obs)
            obstacles_grid.add((ox, oy))

        open_list = []
        closed_list = set()
        
        heapq.heappush(open_list, start_node)
        
        # PROTECTION : Limite pour éviter le freeze si pas de chemin
        iterations = 0
        max_iterations = 1000 

        while open_list:
            iterations += 1
            if iterations > max_iterations:
                return [] # Abandon : chemin trop complexe ou impossible

            current_node = heapq.heappop(open_list)
            closed_list.add((current_node.x, current_node.y))

            # Arrivée atteinte ?
            if current_node.x == end_node.x and current_node.y == end_node.y:
                return self._reconstruct_path(current_node)

            # Voisins (Haut, Bas, Gauche, Droite)
            neighbors = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            
            for dx, dy in neighbors:
                node_position = (current_node.x + dx, current_node.y + dy)

                # Vérification limites grille
                if (node_position[0] < 0 or node_position[0] >= self.grid_width or 
                    node_position[1] < 0 or node_position[1] >= self.grid_height):
                    continue

                # Vérification obstacles (Murs, Glace)
                if node_position in obstacles_grid:
                    continue
                    
                if node_position in closed_list:
                    continue

                new_node = Node(node_position[0], node_position[1], current_node)
                new_node.g = current_node.g + 1
                # Heuristique de Manhattan (plus rapide que Pythagore)
                new_node.h = abs(new_node.x - end_node.x) + abs(new_node.y - end_node.y)
                new_node.f = new_node.g + new_node.h

                # Vérifier si un meilleur chemin existe déjà dans open_list
                # Note: Une implémentation pure vérifierait open_list, 
                # ici on simplifie pour la performance Python
                heapq.heappush(open_list, new_node)

        return [] # Pas de chemin trouvé

    def _reconstruct_path(self, current_node):
        """Remonte les parents pour créer le chemin"""
        path = []
        while current_node is not None:
            # On convertit les coordonnées grille en coordonnées pixels (centre de la case)
            pixel_pos = (
                current_node.x * self.cell_size + self.cell_size // 2,
                current_node.y * self.cell_size + self.cell_size // 2
            )
            path.append(pixel_pos)
            current_node = current_node.parent
        return path[::-1] # Inverser pour avoir start -> end

    def _to_grid(self, pos):
        """Convertit pixels -> grille"""
        return (int(pos[0] // self.cell_size), int(pos[1] // self.cell_size))