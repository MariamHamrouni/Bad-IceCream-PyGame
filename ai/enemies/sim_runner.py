from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Tuple

from ai.utils.game_api import GameState, PlayerState, EnemyState, Grid
from ai.enemies.coordinator import (
    EnemyCoordinator,
    EnemyCoordinatorConfig,
    EnemyRuntimeState,
)
from ai.enemies.a_star import in_bounds



Coord = Tuple[int, int]


# =====================================================
#   Helpers de construction de GameState
# =====================================================

def make_empty_grid(w: int, h: int) -> Grid:
    return [[0 for _ in range(w)] for _ in range(h)]


def make_demo_state() -> Tuple[GameState, EnemyCoordinator]:
    """
    Construit un petit scénario de démo :

    - grille 10x7
    - joueur à droite
    - 3 ennemis :
        * e_chase : chasseur
        * e_patrol : patrouilleur sur 2 points
        * e_block : bloqueur visant un "couloir"
    """
    grid = make_empty_grid(10, 7)

    player = PlayerState(x=8, y=3, lives=3)

    enemies: List[EnemyState] = [
        EnemyState(id="e_chase", x=0, y=3, role="chaser"),
        EnemyState(id="e_patrol", x=2, y=1, role="patroller"),
        EnemyState(id="e_block", x=5, y=5, role="blocker"),
    ]

    state = GameState(
        tick=0,
        grid=grid,
        player=player,
        enemies=enemies,
        fruits=[],
    )

    patrol_routes: Dict[str, List[Coord]] = {
        "e_patrol": [(2, 1), (2, 5)],  # patrouille verticale
    }

    block_targets: Dict[str, Coord] = {
        "e_block": (6, 3),  # un point "stratégique" proche du joueur
    }

    config = EnemyCoordinatorConfig(
        patrol_routes=patrol_routes,
        block_targets=block_targets,
    )
    runtime = EnemyRuntimeState()
    coordinator = EnemyCoordinator(config=config, runtime_state=runtime)

    return state, coordinator


# =====================================================
#   Simulation
# =====================================================

def step_state(
    state: GameState,
    coordinator: EnemyCoordinator,
) -> GameState:
    """
    Fait avancer l'état du jeu d'1 tick :

    - calcule les mouvements des ennemis via EnemyCoordinator
    - applique ces mouvements
    - incrémente le tick

    (Le joueur reste immobile dans cette démo.)
    """
    moves = coordinator.decide_moves(state)

    # Appliquer les mouvements aux ennemis
    new_enemies: List[EnemyState] = []
    for e in state.enemies:
        move = moves.get(e.id, "stay")
        dx, dy = 0, 0
        if move == "right":
            dx = 1
        elif move == "left":
            dx = -1
        elif move == "down":
            dy = 1
        elif move == "up":
            dy = -1

        new_x = e.x + dx
        new_y = e.y + dy
        if not in_bounds((new_x, new_y), state.grid):
            new_x, new_y = e.x, e.y

        # Ici on ne vérifie pas les collisions avec les murs pour simplifier,
        # mais tu peux facilement ajouter un check sur state.grid.
        new_enemies.append(
            EnemyState(
                id=e.id,
                x=new_x,
                y=new_y,
                role=e.role,
            )
        )

    new_state = replace(
        state,
        tick=state.tick + 1,
        enemies=new_enemies,
    )
    return new_state


def print_state(state: GameState) -> None:
    """
    Affiche l'état de la grille, du joueur et des ennemis.
    """
    print(f"\n=== TICK {state.tick} ===")
    print(f"Player: ({state.player.x}, {state.player.y})")

    for e in state.enemies:
        print(f"Enemy {e.id:8s} [{e.role or 'None':9s}] -> ({e.x}, {e.y})")


def run_demo(steps: int = 10) -> None:
    """
    Lance une petite simulation sur 'steps' ticks.

    Exemple d'utilisation :
        python -m ai.enemies.sim_runner
    """
    state, coordinator = make_demo_state()

    print("DÉMARRAGE DE LA SIMULATION DEMO")
    print_state(state)

    for _ in range(steps):
        state = step_state(state, coordinator)
        print_state(state)


if __name__ == "__main__":
    run_demo(steps=12)
