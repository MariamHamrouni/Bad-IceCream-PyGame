from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ai.coach.analyzer import Metrics


@dataclass
class DifficultyConfig:
    enemy_count: int
    spawn_interval: int
    hunter_ratio: float
    patroller_ratio: float
    blocker_ratio: float

    def normalized(self) -> "DifficultyConfig":
        total = self.hunter_ratio + self.patroller_ratio + self.blocker_ratio
        if total <= 0:
            return DifficultyConfig(
                enemy_count=self.enemy_count,
                spawn_interval=self.spawn_interval,
                hunter_ratio=1/3,
                patroller_ratio=1/3,
                blocker_ratio=1/3,
            )
        return DifficultyConfig(
            enemy_count=self.enemy_count,
            spawn_interval=self.spawn_interval,
            hunter_ratio=self.hunter_ratio / total,
            patroller_ratio=self.patroller_ratio / total,
            blocker_ratio=self.blocker_ratio / total,
        )


@dataclass
class DifficultyBounds:
    min_enemies: int = 1
    max_enemies: int = 10
    min_spawn_interval: int = 20
    max_spawn_interval: int = 180


class DifficultyManager:
    def __init__(
        self,
        base_enemy_count: int = 3,
        base_spawn_interval: int = 90,
        base_hunter_ratio: float = 0.4,
        base_patroller_ratio: float = 0.4,
        base_blocker_ratio: float = 0.2,
        bounds: DifficultyBounds | None = None,
    ):
        self.base_enemy_count = base_enemy_count
        self.base_spawn_interval = base_spawn_interval
        self.base_hunter_ratio = base_hunter_ratio
        self.base_patroller_ratio = base_patroller_ratio
        self.base_blocker_ratio = base_blocker_ratio
        self.bounds = bounds or DifficultyBounds()

    # ----------------------------------------------------------

    def adjust_difficulty(self, metrics: Metrics) -> DifficultyConfig:
        performance_score = self._compute_performance_score(metrics)
        factor = self._score_to_factor(performance_score)

        enemy_count = self._compute_enemy_count(factor)
        spawn_interval = self._compute_spawn_interval(factor)
        hunter_ratio, patroller_ratio, blocker_ratio = self._compute_role_ratios(factor)

        config = DifficultyConfig(
            enemy_count=enemy_count,
            spawn_interval=spawn_interval,
            hunter_ratio=hunter_ratio,
            patroller_ratio=patroller_ratio,
            blocker_ratio=blocker_ratio,
        )
        return config.normalized()

    # ----------------------------------------------------------

    def _compute_performance_score(self, metrics: Metrics) -> float:
        score = 0.0
        score += metrics.fruit_collected * 1.0
        score -= metrics.death_count * 2.0

        if metrics.time_between_deaths:
            avg = sum(metrics.time_between_deaths) / len(metrics.time_between_deaths)
            score += min(avg / 100.0, 3.0)

        return score

    def _score_to_factor(self, score: float) -> float:
        score = max(-5.0, min(5.0, score))
        return 1.0 + (score / 10.0)

    def _compute_enemy_count(self, factor: float) -> int:
        count = int(round(self.base_enemy_count * factor))
        count = max(self.bounds.min_enemies, min(self.bounds.max_enemies, count))
        return count

    def _compute_spawn_interval(self, factor: float) -> int:
        interval = int(round(self.base_spawn_interval / factor))
        interval = max(self.bounds.min_spawn_interval,
                       min(self.bounds.max_spawn_interval, interval))
        return interval

    def _compute_role_ratios(self, factor: float):
        hunter = self.base_hunter_ratio
        patroller = self.base_patroller_ratio
        blocker = self.base_blocker_ratio

        delta = (factor - 1.0) * 0.3
        hunter += delta
        patroller -= delta

        hunter = max(0.05, hunter)
        patroller = max(0.05, patroller)

        return hunter, patroller, blocker
