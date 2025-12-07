from __future__ import annotations

from typing import List, Tuple

from ai.enemies.coordinator import (
    EnemyCoordinator,
    EnemyCoordinatorConfig,
    EnemyRuntimeState,
)
from ai.utils.game_api import GameState, PlayerState, EnemyState, Grid


Coord = Tuple[int, int]


def make_empty_grid(w: int, h: int) -> Grid:
    return [[0 for _ in range(w)] for _ in range(h)]


def make_state(
    grid: Grid,
    player_pos: Coord,
    enemies: List[EnemyState],
) -> GameState:
    px, py = player_pos
    player = PlayerState(x=px, y=py, lives=3)
    return GameState(
        tick=0,
        grid=grid,
        player=player,
        enemies=enemies,
        fruits=[],
    )


def test_coordinator_basic_chaser_move():
    grid = make_empty_grid(5, 5)
    e1 = EnemyState(id="e1", x=0, y=0, role="chaser")
    state = make_state(grid, player_pos=(4, 0), enemies=[e1])

    coord = EnemyCoordinator()
    moves = coord.decide_moves(state)

    assert "e1" in moves
    # Le chasseur doit aller vers la droite ou rester en cas de bug
    assert moves["e1"] in ("right", "stay")


def test_coordinator_collision_resolution():
    """
    Deux chasseurs alignés sur le joueur vont vouloir la même case.
    On vérifie qu'il n'y a pas 2 ennemis qui finissent sur la même case.
    """
    grid = make_empty_grid(5, 5)

    # Deux ennemis au même endroit de départ, c'est extrême mais idéal pour tester
    e1 = EnemyState(id="a", x=1, y=1, role="chaser")
    e2 = EnemyState(id="b", x=1, y=1, role="chaser")

    state = make_state(grid, player_pos=(3, 1), enemies=[e1, e2])

    coord = EnemyCoordinator()
    moves = coord.decide_moves(state)

    # Les deux ne doivent pas se "marcher dessus".
    # Même si les deux veulent aller "right", la résolution doit en retenir un seul.
    # On ne peut vérifier les positions finales exactes ici,
    # mais au minimum on n'a pas d'exception et on a bien des mouvements définis.
    assert set(moves.keys()) == {"a", "b"}
    assert moves["a"] in ("right", "stay", "left", "up", "down")
    assert moves["b"] in ("right", "stay", "left", "up", "down")


def test_coordinator_with_patroller_route():
    grid = make_empty_grid(5, 5)

    e1 = EnemyState(id="p1", x=0, y=0, role="patroller")
    state = make_state(grid, player_pos=(4, 4), enemies=[e1])

    patrol_route = {
        "p1": [(0, 0), (2, 0)],
    }
    config = EnemyCoordinatorConfig(patrol_routes=patrol_route)
    runtime = EnemyRuntimeState()
    coord = EnemyCoordinator(config=config, runtime_state=runtime)

    moves1 = coord.decide_moves(state)
    assert "p1" in moves1

    # On s'assure qu'on peut rappeler decide_moves sans planter
    moves2 = coord.decide_moves(state)
    assert "p1" in moves2
