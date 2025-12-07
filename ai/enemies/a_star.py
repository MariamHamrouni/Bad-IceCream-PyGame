# ai/enemies/a_star.py
from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Dict, List, Optional, Set, Tuple

from ai.utils.game_api import Grid, GameState, EnemyState

Coord = Tuple[int, int]


@dataclass(frozen=True)
class PathfindingConfig:
    """
    Configuration simple pour l'A*.

    - allow_diagonal : pour l'instant False (4-neighbors), mais extensible.
    - max_nodes      : sécurité pour éviter les boucles infinies sur de grandes grilles.
    """
    allow_diagonal: bool = False
    max_nodes: int = 10_000


# ==========================
#   Helpers sur la grille
# ==========================

def grid_size(grid: Grid) -> Tuple[int, int]:
    """Retourne (width, height) d'une grille."""
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    return w, h


def in_bounds(pos: Coord, grid: Grid) -> bool:
    """Vérifie que la position est dans la grille."""
    x, y = pos
    w, h = grid_size(grid)
    return 0 <= x < w and 0 <= y < h


def is_walkable(pos: Coord, grid: Grid) -> bool:
    """
    0 = libre, 1 = mur (comme défini dans GameAPI.Grid).
    On considère que toute valeur != 0 est bloquante.
    """
    if not in_bounds(pos, grid):
        return False
    x, y = pos
    return grid[y][x] == 0


def neighbors(pos: Coord, grid: Grid, allow_diagonal: bool = False) -> List[Coord]:
    """Retourne les voisins accessibles (4 ou 8 directions)."""
    x, y = pos
    candidates: List[Coord] = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]

    if allow_diagonal:
        candidates.extend(
            [
                (x + 1, y + 1),
                (x - 1, y + 1),
                (x + 1, y - 1),
                (x - 1, y - 1),
            ]
        )

    return [p for p in candidates if is_walkable(p, grid)]


# ==========================
#   Heuristique et A*
# ==========================

def manhattan(a: Coord, b: Coord) -> int:
    """Heuristique Manhattan pour un mouvement en 4 directions."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(
    came_from: Dict[Coord, Coord],
    current: Coord,
    start: Coord,
) -> List[Coord]:
    """
    Reconstruit le chemin depuis start jusqu'à current.

    Retourne une liste de positions [start, ..., current].
    """
    path: List[Coord] = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()

    # petit garde-fou : on s'assure que le chemin commence bien par start
    if not path or path[0] != start:
        path.insert(0, start)
    return path


def find_path(
    start: Coord,
    goal: Coord,
    grid: Grid,
    config: Optional[PathfindingConfig] = None,
) -> List[Coord]:
    """
    Algorithme A* sur une grille.

    Parameters
    ----------
    start : (x, y)
    goal  : (x, y)
    grid  : Grid (list[list[int]]) où 0 = libre, 1 = mur
    config: PathfindingConfig (optionnel)

    Returns
    -------
    List[Coord]
        Chemin incluant start et goal : [start, ..., goal]
        Si aucun chemin n'est trouvé -> [].
    """
    if config is None:
        config = PathfindingConfig()

    if start == goal:
        return [start]

    if not is_walkable(start, grid) or not is_walkable(goal, grid):
        # Impossible de démarrer ou d'arriver sur une case bloquée
        return []

    open_heap: List[Tuple[int, Coord]] = []
    heappush(open_heap, (0, start))

    came_from: Dict[Coord, Coord] = {}
    g_score: Dict[Coord, float] = {start: 0.0}
    f_score: Dict[Coord, float] = {start: manhattan(start, goal)}

    closed: Set[Coord] = set()
    explored_nodes = 0

    while open_heap:
        _, current = heappop(open_heap)

        if current in closed:
            continue

        closed.add(current)
        explored_nodes += 1

        if explored_nodes > config.max_nodes:
            # On coupe pour éviter une explosion combinatoire.
            return []

        if current == goal:
            return reconstruct_path(came_from, current, start)

        for nb in neighbors(current, grid, allow_diagonal=config.allow_diagonal):
            tentative_g = g_score[current] + 1  # coût uniforme

            if tentative_g < g_score.get(nb, float("inf")):
                came_from[nb] = current
                g_score[nb] = tentative_g
                f = tentative_g + manhattan(nb, goal)
                f_score[nb] = f
                heappush(open_heap, (f, nb))

    # Aucun chemin
    return []


# ==========================
#   Helpers orientés jeu
# ==========================

def path_enemy_to_player(
    state: GameState,
    enemy: EnemyState,
    config: Optional[PathfindingConfig] = None,
) -> List[Coord]:
    """
    Helper pratique : calcule le chemin d'un ennemi vers le joueur.

    Utile plus tard pour les rôles "chasseur" par ex.

    Returns
    -------
    List[Coord]
        Chemin [ (enemy.x, enemy.y), ..., (player.x, player.y) ]
        ou [] si aucun chemin faisable.
    """
    start = (enemy.x, enemy.y)
    goal = (state.player.x, state.player.y)
    return find_path(start, goal, state.grid, config)
