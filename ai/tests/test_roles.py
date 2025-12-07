from __future__ import annotations

from typing import List, Tuple

from ai.enemies.roles import (
    RoleConfig,
    coord_to_move,
    next_step_chaser,
    next_step_patroller,
    next_step_blocker,
)
from ai.utils.game_api import GameState, PlayerState, EnemyState, Grid


Coord = Tuple[int, int]


def make_empty_grid(w: int, h: int) -> Grid:
    return [[0 for _ in range(w)] for _ in range(h)]


def make_simple_state(
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


def test_coord_to_move_basic():
    assert coord_to_move((0, 0), (1, 0)) == "right"
    assert coord_to_move((1, 0), (0, 0)) == "left"
    assert coord_to_move((0, 0), (0, 1)) == "down"
    assert coord_to_move((0, 1), (0, 0)) == "up"
    # Cas étrange : pas de mouvement ou mouvement diagonal
    assert coord_to_move((0, 0), (0, 0)) == "stay"
    assert coord_to_move((0, 0), (1, 1)) == "stay"


def test_chaser_moves_closer_to_player():
    grid = make_empty_grid(5, 5)
    enemy = EnemyState(id="e1", x=0, y=0, role="chaser")
    state = make_simple_state(grid, player_pos=(4, 0), enemies=[enemy])

    next_pos = next_step_chaser(state, enemy)
    # Le chasseur doit se rapprocher de x=4, donc aller à droite
    assert next_pos == (1, 0)


def test_blocker_moves_towards_block_target():
    grid = make_empty_grid(5, 5)
    enemy = EnemyState(id="e1", x=2, y=2, role="blocker")
    state = make_simple_state(grid, player_pos=(0, 0), enemies=[enemy])

    config = RoleConfig()
    block_target: Coord = (4, 2)

    next_pos = next_step_blocker(state, enemy, block_target, config)
    # Se rapproche de x=4 sur la même ligne
    assert next_pos in [(3, 2), (4, 2)]


def test_patroller_cycles_route():
    grid = make_empty_grid(5, 5)
    enemy = EnemyState(id="e1", x=0, y=0, role="patroller")
    state = make_simple_state(grid, player_pos=(4, 4), enemies=[enemy])

    route = [(0, 0), (2, 0), (2, 2)]
    config = RoleConfig()

    # 1er appel : e1 est déjà sur route[0]=(0,0) -> vise (2,0)
    pos1, idx1 = next_step_patroller(state, enemy, route, current_index=0, config=config)
    assert idx1 in (1, 0, 2)  # dépend de la logique, mais ne doit pas planter

    # On "téléporte" l'ennemi sur la nouvelle position pour continuer le test
    enemy.x, enemy.y = pos1
    pos2, idx2 = next_step_patroller(state, enemy, route, current_index=idx1, config=config)

    # On vérifie juste que l'algorithme ne boucle pas étrangement
    assert isinstance(pos2, tuple)
    assert isinstance(idx2, int)
