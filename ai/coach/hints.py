from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ai.coach.analyzer import Metrics


@dataclass
class HintConfig:
    cooldown_ticks: int = 30
    min_deaths_for_warning: int = 1
    fruit_goal: int = 3
    stuck_threshold: int = 200


class HintEngine:
    """
    Génère des hints à partir des métriques, avec un cooldown
    pour éviter le spam.
    """

    def __init__(self, config: HintConfig | None = None):
        self.config = config or HintConfig()
        self.last_hint_tick: int = -9999

    def generate_hint(self, metrics: Metrics, current_tick: int) -> Optional[str]:
        # 1) cooldown
        if current_tick - self.last_hint_tick < self.config.cooldown_ticks:
            return None

        # 2) trop de morts
        if metrics.death_count >= self.config.min_deaths_for_warning:
            self.last_hint_tick = current_tick
            return "Tu perds souvent une vie ici… essaie de changer de trajet ou d’éviter les ennemis."

        # 3) pas assez de fruits
        if metrics.fruit_collected < self.config.fruit_goal and metrics.ticks_played > 100:
            self.last_hint_tick = current_tick
            return "Essaie de collecter davantage de fruits pour progresser dans le niveau."

        # 4) joueur possiblement bloqué
        if metrics.ticks_played > self.config.stuck_threshold:
            self.last_hint_tick = current_tick
            return "Tu sembles bloqué… essaie un autre chemin ou casse des blocs pour avancer."

        return None
