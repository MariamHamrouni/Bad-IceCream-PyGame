# ai/utils/game_api.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import json
from pathlib import Path

Grid = List[List[int]]  # 0 = libre, 1 = mur (par exemple)


@dataclass
class PlayerState:
    x: int
    y: int
    lives: int = 3


@dataclass
class EnemyState:
    id: str
    x: int
    y: int
    role: str | None = None


@dataclass
class GameState:
    tick: int
    grid: Grid
    player: PlayerState
    enemies: List[EnemyState]
    fruits: List[Tuple[int, int]]
    # tu pourras ajouter d'autres champs plus tard (score, timer, etc.)


class GameAPIError(Exception):
    """Erreur générique pour le GameAPI."""
    pass


class SnapshotGameAPI:
    """
    Charge des snapshots JSON pour la simulation headless.
    """

    def __init__(self, snapshots_dir: str | Path):
        self.snapshots_dir = Path(snapshots_dir)
        if not self.snapshots_dir.exists():
            raise GameAPIError(f"Snapshots directory not found: {self.snapshots_dir}")

    def load_snapshot(self, name: str) -> GameState:
        """
        name = nom de fichier sans extension, ex: 'example_tick0'
        -> lit data/snapshots/example_tick0.json
        """
        path = self.snapshots_dir / f"{name}.json"
        if not path.exists():
            raise GameAPIError(f"Snapshot not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        grid = raw["grid"]
        player_raw = raw["player"]
        enemies_raw = raw.get("enemies", [])
        fruits_raw = raw.get("fruits", [])

        player = PlayerState(
            x=player_raw["x"],
            y=player_raw["y"],
            lives=player_raw.get("lives", 3),
        )

        enemies = [
            EnemyState(
                id=str(e["id"]),
                x=e["x"],
                y=e["y"],
                role=e.get("role"),
            )
            for e in enemies_raw
        ]

        fruits = [(f[0], f[1]) for f in fruits_raw]

        return GameState(
            tick=raw.get("tick", 0),
            grid=grid,
            player=player,
            enemies=enemies,
            fruits=fruits,
        )
