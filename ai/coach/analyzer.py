from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any
import json
from pathlib import Path

from ai.utils.game_api import GameState


@dataclass
class Metrics:
    """
    Métriques globales calculées par le coach.
    """
    death_count: int = 0
    fruit_collected: int = 0
    fruit_order: List[tuple[int, int]] = field(default_factory=list)
    ticks_played: int = 0
    time_between_deaths: List[int] = field(default_factory=list)

    # interne : dernier tick d'une mort détectée
    last_death_tick: int | None = None


class GameAnalyzer:
    """
    Consomme des GameState successifs et met à jour les métriques.
    """

    def __init__(self) -> None:
        self.metrics = Metrics()
        self._previous_state: GameState | None = None

    def update(self, state: GameState) -> None:
        """
        Appeler à chaque tick avec le nouvel état du jeu.
        """
        self.metrics.ticks_played += 1

        if self._previous_state is not None:
            self._detect_death(self._previous_state, state)
            self._detect_fruits_collected(self._previous_state, state)

        self._previous_state = state

    # ---------- détection des événements ---------- #

    def _detect_death(self, prev: GameState, current: GameState) -> None:
        prev_lives = getattr(prev.player, "lives", None)
        curr_lives = getattr(current.player, "lives", None)

        if prev_lives is None or curr_lives is None:
            return

        if curr_lives < prev_lives:
            self.metrics.death_count += 1

            if self.metrics.last_death_tick is not None:
                delta = current.tick - self.metrics.last_death_tick
                if delta >= 0:
                    self.metrics.time_between_deaths.append(delta)

            self.metrics.last_death_tick = current.tick

    def _detect_fruits_collected(self, prev: GameState, current: GameState) -> None:
        prev_set = set(prev.fruits)
        curr_set = set(current.fruits)

        collected = prev_set - curr_set
        if collected:
            self.metrics.fruit_collected += len(collected)
            for fruit in collected:
                self.metrics.fruit_order.append(fruit)

    # ---------- export ---------- #

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self.metrics)
        data.pop("last_death_tick", None)
        return data

    def save_to_json(self, output_dir: str | Path, filename: str) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"metrics_{filename}.json"

        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

        return path
