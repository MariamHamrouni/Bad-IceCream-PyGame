from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Literal

from ai.utils.game_api import GameState, EnemyState, Grid
from ai.enemies.a_star import (
    PathfindingConfig,
    find_path,
    path_enemy_to_player,
)

Coord = Tuple[int, int]
Move = Literal["up", "down", "left", "right", "stay"]


@dataclass(frozen=True)
class RoleConfig:
    """
    Configuration simple pour les rôles.

    - path_config : configuration de l'A*.
    """
    path_config: PathfindingConfig = PathfindingConfig()


def coord_to_move(start: Coord, nxt: Coord) -> Move:
    """
    Convertit un déplacement entre deux cases en mouvement symbolique.

    start = (x0, y0), nxt = (x1, y1)
    """
    x0, y0 = start
    x1, y1 = nxt
    dx = x1 - x0
    dy = y1 - y0

    if dx == 1 and dy == 0:
        return "right"
    if dx == -1 and dy == 0:
        return "left"
    if dx == 0 and dy == 1:
        return "down"
    if dx == 0 and dy == -1:
        return "up"
    return "stay"


# =========================================================
#  Rôles individuels (logique pure, sans état global)
# =========================================================

def next_step_chaser(
    state: GameState,
    enemy: EnemyState,
    config: Optional[RoleConfig] = None,
) -> Coord:
    """
    Ennemi 'chasseur' : cherche à atteindre directement le joueur.

    Utilise path_enemy_to_player, puis retourne la prochaine case du chemin.
    Si aucun chemin trouvé -> reste sur place.
    """
    if config is None:
        config = RoleConfig()

    path = path_enemy_to_player(state, enemy, config.path_config)

    if len(path) >= 2:
        # path[0] = position actuelle, path[1] = prochaine case
        return path[1]

    # Pas de chemin ou déjà sur la cible
    return (enemy.x, enemy.y)


def next_step_towards_target(
    grid: Grid,
    start: Coord,
    goal: Coord,
    path_config: Optional[PathfindingConfig] = None,
) -> Coord:
    """
    Helper générique : calcule un chemin A* entre start et goal
    puis renvoie la prochaine case à emprunter.
    Si aucun chemin n'existe, on reste sur place (start).
    """
    if path_config is None:
        path_config = PathfindingConfig()

    if start == goal:
        return start

    path = find_path(start, goal, grid, path_config)
    if len(path) >= 2:
        return path[1]

    return start


def next_step_patroller(
    state: GameState,
    enemy: EnemyState,
    patrol_points: List[Coord],
    current_index: int,
    config: Optional[RoleConfig] = None,
) -> Tuple[Coord, int]:
    """
    Ennemi 'patrouilleur' : suit une liste de waypoints en boucle.

    Parameters
    ----------
    patrol_points : liste de positions (x,y) à visiter dans l'ordre.
    current_index : index actuel dans la liste.

    Returns
    -------
    (next_coord, new_index)
    """
    if config is None:
        config = RoleConfig()

    if not patrol_points:
        # Pas de route définie -> on reste sur place
        return (enemy.x, enemy.y), current_index

    x, y = enemy.x, enemy.y
    start: Coord = (x, y)

    # Si l'ennemi est déjà sur le point courant, on passe au suivant
    target_index = current_index % len(patrol_points)
    target = patrol_points[target_index]

    if start == target:
        target_index = (target_index + 1) % len(patrol_points)
        target = patrol_points[target_index]

    next_coord = next_step_towards_target(
        state.grid,
        start,
        target,
        config.path_config,
    )

    return next_coord, target_index


def next_step_blocker(
    state: GameState,
    enemy: EnemyState,
    block_target: Coord,
    config: Optional[RoleConfig] = None,
) -> Coord:
    """
    Ennemi 'bloqueur' : vise une position stratégique (couloir, entrée...).

    On le fait se déplacer vers block_target via A*.
    """
    if config is None:
        config = RoleConfig()

    start: Coord = (enemy.x, enemy.y)
    return next_step_towards_target(
        state.grid,
        start,
        block_target,
        config.path_config,
    )


def choose_next_coord_for_enemy(
    state: GameState,
    enemy: EnemyState,
    role: Optional[str] = None,
    *,
    patrol_points: Optional[List[Coord]] = None,
    patrol_index: int = 0,
    block_target: Optional[Coord] = None,
    config: Optional[RoleConfig] = None,
) -> Tuple[Coord, int]:
    """
    Point d'entrée générique pour les rôles.

    Parameters
    ----------
    role : str ou None
        Si None, on utilise enemy.role, sinon la valeur fournie.
        Valeurs supportées : "chaser", "patroller", "blocker".
    patrol_points, patrol_index :
        Utilisés si role == "patroller".
    block_target :
        Utilisé si role == "blocker".

    Returns
    -------
    (next_coord, new_patrol_index)
    """
    if config is None:
        config = RoleConfig()

    r = role or enemy.role or "chaser"

    if r == "patroller":
        coord, new_idx = next_step_patroller(
            state,
            enemy,
            patrol_points or [],
            patrol_index,
            config,
        )
        return coord, new_idx

    if r == "blocker" and block_target is not None:
        coord = next_step_blocker(state, enemy, block_target, config)
        return coord, patrol_index

    # Cas par défaut : chasseur
    coord = next_step_chaser(state, enemy, config)
    return coord, patrol_index
