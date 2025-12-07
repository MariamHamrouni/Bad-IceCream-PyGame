# ai/tests/test_pathfinding.py
from __future__ import annotations

from typing import List

from ai.enemies.a_star import find_path, PathfindingConfig
from ai.utils.game_api import Grid


def make_empty_grid(width: int, height: int) -> Grid:
    return [[0 for _ in range(width)] for _ in range(height)]


def test_straight_line_path():
    """
    Sur une ligne droite sans obstacles, l'A* doit trouver le chemin
    le plus court (ici, simplement aller tout droit).
    """
    grid: Grid = make_empty_grid(5, 5)

    start = (0, 0)
    goal = (4, 0)

    path = find_path(start, goal, grid)

    # Le chemin doit commencer par start et finir par goal
    assert path[0] == start
    assert path[-1] == goal

    # Distance Manhattan = 4 -> nombre de cases = 5 (start + 4 mouvements)
    assert len(path) == 5

    # On doit se déplacer d'une case à la fois
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        assert abs(x1 - x2) + abs(y1 - y2) == 1


def test_path_avoids_wall():
    """
    L'algorithme doit contourner les murs au lieu de passer "à travers".
    """
    grid: Grid = make_empty_grid(5, 5)

    # On crée un mur horizontal au milieu, sauf sur les bords
    for x in range(1, 4):
        grid[2][x] = 1  # 0 = libre, 1 = mur

    start = (0, 2)
    goal = (4, 2)

    path = find_path(start, goal, grid)

    # Un chemin existe en haut ou en bas du mur
    assert path, "Aucun chemin trouvé alors qu'il en existe au moins un."

    # Aucune des positions du chemin ne doit être un mur
    for x, y in path:
        assert grid[y][x] == 0


def test_no_path_when_fully_blocked():
    """
    Cas où le goal est complètement enfermé par des murs - aucun chemin.
    """
    grid: Grid = make_empty_grid(5, 5)

    goal = (2, 2)
    start = (0, 0)

    # On entoure la case (2,2) de murs
    neighbors = [(3, 2), (1, 2), (2, 3), (2, 1)]
    for x, y in neighbors:
        grid[y][x] = 1

    path = find_path(start, goal, grid)

    assert path == [], "Un chemin a été trouvé alors que le goal est enfermé."


def test_start_or_goal_on_wall_returns_empty():
    """
    Si start ou goal est sur un mur, on retourne directement [].
    """
    grid: Grid = make_empty_grid(3, 3)

    # Start sur un mur
    grid[0][0] = 1
    path1 = find_path((0, 0), (2, 2), grid)
    assert path1 == []

    # Goal sur un mur
    grid[0][0] = 0
    grid[2][2] = 1
    path2 = find_path((0, 0), (2, 2), grid)
    assert path2 == []


def test_small_max_nodes_cutoff():
    """
    Vérifie que max_nodes est bien pris en compte.
    (On force un cutoff en mettant max_nodes très petit.)
    """
    grid: Grid = make_empty_grid(10, 10)
    config = PathfindingConfig(max_nodes=1)  # coupe très tôt

    path = find_path((0, 0), (9, 9), grid, config=config)

    # On ne peut pas garantir exactement le résultat,
    # mais on sait que l'algorithme doit renvoyer [] à cause du cutoff.
    assert path == []
