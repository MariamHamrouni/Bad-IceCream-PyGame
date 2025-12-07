from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

Coord = Tuple[int, int]

@dataclass
class EnemySpawn:
    role: str              # "chaser" | "patroller" | "blocker" | ...
    pos: Coord             # (x,y) en tiles
    patrol_route: Optional[List[Coord]] = None
    block_target: Optional[Coord] = None


@dataclass
class LevelSpec:
    width: int                 # cols (ex: 18)
    height: int                # rows (ex: 9)

    walls: List[Coord]         # liste de murs
    ice_blocks: List[Coord]    # liste de glaces
    fruits: List[Coord]        # positions fruits

    enemies: List[EnemySpawn]  # trolls IA-layer

    metadata: Dict = None      # pour l’IA coach
