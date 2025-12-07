from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ai.utils.game_api import GameState, EnemyState
from ai.enemies.roles import (
    Coord,
    Move,
    RoleConfig,
    choose_next_coord_for_enemy,
    coord_to_move,
)


@dataclass
class EnemyRuntimeState:
    """
    État interne côté IA pour chaque ennemi.
    (Séparé de EnemyState qui vient du GameAPI.)
    """
    patrol_index_by_id: Dict[str, int] = field(default_factory=dict)


@dataclass
class EnemyCoordinatorConfig:
    """
    Configuration de coordination.

    - patrol_routes : routes de patrouille pour certains ennemis.
    - block_targets : positions "stratégiques" pour les bloqueurs.
    """
    patrol_routes: Dict[str, List[Coord]] = field(default_factory=dict)
    block_targets: Dict[str, Coord] = field(default_factory=dict)
    role_config: RoleConfig = RoleConfig()


class EnemyCoordinator:
    """
    Coordonne plusieurs ennemis :

    - choisit la prochaine case par ennemi en fonction du rôle
    - évite les collisions simples (2 ennemis sur la même case)
    - retourne des mouvements symboliques "up"/"down"/etc.
    """

    def __init__(
        self,
        config: Optional[EnemyCoordinatorConfig] = None,
        runtime_state: Optional[EnemyRuntimeState] = None,
    ) -> None:
        self.config = config or EnemyCoordinatorConfig()
        self.runtime_state = runtime_state or EnemyRuntimeState()

    # --------------------------------------------------
    #  API principale
    # --------------------------------------------------
    def decide_moves(self, state: GameState) -> Dict[str, Move]:
        """
        Décide le mouvement de chaque ennemi pour un tick de jeu.

        Returns
        -------
        Dict[enemy_id, Move]
        """
        desired_positions: Dict[str, Coord] = {}
        start_positions: Dict[str, Coord] = {}

        # 1) Calculer la case désirée pour chaque ennemi (sans coord.)
        for enemy in state.enemies:
            eid = enemy.id
            start_pos: Coord = (enemy.x, enemy.y)
            start_positions[eid] = start_pos

            patrol_index = self.runtime_state.patrol_index_by_id.get(eid, 0)
            patrol_route = self.config.patrol_routes.get(eid, [])
            block_target = self.config.block_targets.get(eid)

            next_coord, new_patrol_index = choose_next_coord_for_enemy(
                state,
                enemy,
                role=enemy.role,
                patrol_points=patrol_route,
                patrol_index=patrol_index,
                block_target=block_target,
                config=self.config.role_config,
            )

            self.runtime_state.patrol_index_by_id[eid] = new_patrol_index
            desired_positions[eid] = next_coord

        # 2) Résoudre les collisions (plusieurs ennemis voulant la même case)
        resolved_positions = self._resolve_collisions(
            desired_positions,
            start_positions,
        )

        # 3) Convertir en mouvements symboliques
        moves: Dict[str, Move] = {}
        for eid, new_pos in resolved_positions.items():
            start = start_positions[eid]
            moves[eid] = coord_to_move(start, new_pos)

        return moves

    # --------------------------------------------------
    #  Résolution simple de collisions
    # --------------------------------------------------
    @staticmethod
    def _resolve_collisions(
        desired: Dict[str, Coord],
        starts: Dict[str, Coord],
    ) -> Dict[str, Coord]:
        """
        Stratégie simple :
        - si plusieurs ennemis veulent aller sur la même case :
            * on laisse passer celui avec le plus petit id (ordre lexical)
            * les autres restent sur leur case de départ.
        """
        # Regroupe par case désirée
        tile_to_enemies: Dict[Coord, List[str]] = {}
        for eid, pos in desired.items():
            tile_to_enemies.setdefault(pos, []).append(eid)

        resolved: Dict[str, Coord] = {}

        for pos, eids in tile_to_enemies.items():
            if len(eids) == 1:
                # aucun conflit
                eid = eids[0]
                resolved[eid] = pos
            else:
                # conflit : on choisit celui avec l'id lexicographiquement min
                eids_sorted = sorted(eids)
                winner = eids_sorted[0]
                resolved[winner] = pos

                # Les autres restent sur place
                for loser in eids_sorted[1:]:
                    resolved[loser] = starts[loser]

        return resolved
