from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from ai.utils.game_api import GameState, PlayerState, EnemyState, Grid
from ai.enemies.coordinator import EnemyCoordinator, EnemyCoordinatorConfig, EnemyRuntimeState
from ai.enemies.roles import Move

Coord = Tuple[int, int]


@dataclass
class EnemyAIController:
    """
    Couche d'adaptation entre le moteur PyGame et l'IA.

    - construit un GameState à partir de données "brutes" (grille, joueur, ennemis, fruits)
    - utilise EnemyCoordinator pour décider des mouvements
    - conserve son propre tick interne
    """

    coordinator: EnemyCoordinator
    tick: int = 0

    @classmethod
    def create_default(cls) -> "EnemyAIController":
        """
        Fabrique un contrôleur IA avec une config par défaut.
        (Tu pourras plus tard passer des patrol_routes ou block_targets.)
        """
        config = EnemyCoordinatorConfig()
        runtime = EnemyRuntimeState()
        coordinator = EnemyCoordinator(config=config, runtime_state=runtime)
        return cls(coordinator=coordinator)

    # ------------------------------------------------------------------
    #  API principale appelée depuis la boucle de jeu PyGame
    # ------------------------------------------------------------------
    def decide_moves_from_raw(
        self,
        grid: Grid,
        player_pos: Coord,
        player_lives: int,
        enemies_raw: List[dict],
        fruits: List[Coord],
    ) -> Dict[str, Move]:
        """
        Paramètres:
        ----------
        grid : Grid
            Grille 2D (0 = libre, 1 = mur) en coordonnées tiles.
        player_pos : (x, y)
            Position du joueur en coordonnées tiles.
        player_lives : int
            Nombre de vies restantes.
        enemies_raw : liste de dicts:
            Chaque dict doit contenir :
                - "id"   : str unique par ennemi
                - "x","y": int position en tiles
                - "role" : str, ex "chaser" / "patroller" / "blocker"
        fruits : liste de (x, y) en tiles

        Retour:
        -------
        Dict[id_enemy -> Move]
        """
        px, py = player_pos
        player = PlayerState(x=px, y=py, lives=player_lives)

        enemies: List[EnemyState] = []
        for e in enemies_raw:
            enemies.append(
                EnemyState(
                    id=str(e["id"]),
                    x=int(e["x"]),
                    y=int(e["y"]),
                    role=e.get("role"),
                )
            )

        state = GameState(
            tick=self.tick,
            grid=grid,
            player=player,
            enemies=enemies,
            fruits=list(fruits),
        )

        moves = self.coordinator.decide_moves(state)
        self.tick += 1
        return moves
