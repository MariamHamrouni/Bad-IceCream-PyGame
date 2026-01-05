import random
from typing import List, Tuple, Dict

class MazeGenerator:
    """Générateur de labyrinthe itératif (Stack-based)"""
    
    def __init__(self, cols=20, rows=15):
        self.cols = cols
        self.rows = rows
        self.grid = []
        self.stack = []
        self.cell_size_x = 40
        self.cell_size_y = 58

    def generate_ice_maze(self, difficulty: float = 0.5) -> Dict:
        """Génère un niveau type 'Glace' (Labyrinthe)"""
        # 1. Init Grille (Tout est mur au début = 1)
        # 0 = Vide, 1 = Mur
        self.grid = [[1 for _ in range(self.rows)] for _ in range(self.cols)]
        
        # 2. Backtracking Itératif
        start_cell = (0, 0)
        self.grid[0][0] = 0 # Marquer visité/vide
        self.stack.append(start_cell)
        
        while self.stack:
            current_x, current_y = self.stack[-1]
            neighbors = self._get_unvisited_neighbors(current_x, current_y)
            
            if neighbors:
                next_x, next_y = random.choice(neighbors)
                self.grid[next_x][next_y] = 0
                self.stack.append((next_x, next_y))
            else:
                self.stack.pop()
        
        # 3. Ouverture supplémentaire (Looping)
        openness = int((1.0 - difficulty) * (self.cols * self.rows * 0.2))
        for _ in range(openness):
            rx = random.randint(1, self.cols-2)
            ry = random.randint(1, self.rows-2)
            self.grid[rx][ry] = 0

        # 4. Conversion en données de niveau
        return self._convert_to_level_data()

    def _get_unvisited_neighbors(self, x, y):
        candidates = []
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                if self.grid[nx][ny] == 1: # Si c'est un mur (non visité)
                    self.grid[x + dx//2][y + dy//2] = 0
                    candidates.append((nx, ny))
        return candidates

    def _convert_to_level_data(self):
        level_data = {
            "metadata": {"theme": "ice_maze"},
            "iceblocks": [],
            "fruits": [],
            "trolls": [],
            "player_start": (60, 60)
        }
        
        for x in range(self.cols):
            for y in range(self.rows):
                if self.grid[x][y] == 1: # Mur
                    px = 50 + x * self.cell_size_x
                    py = 50 + y * self.cell_size_y
                    if not (abs(px - 60) < 50 and abs(py - 60) < 50):
                        level_data["iceblocks"].append((px, py))
                else:
                    if random.random() < 0.05:
                        px = 50 + x * self.cell_size_x + 20
                        py = 50 + y * self.cell_size_y + 29
                        level_data["fruits"].append({"pos": (px, py), "type": "grape"})
        
        return level_data