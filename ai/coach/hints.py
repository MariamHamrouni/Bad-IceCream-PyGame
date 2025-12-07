# ai/coach/hints.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ai.coach.analyzer import Metrics


@dataclass
class HintConfig:
    cooldown_ticks: int = 30   # éviter le spam
    min_deaths_for_warning: int = 1
    fruit_goal: int = 3        # si joueur n’a pas mangé assez de fruits → hint
    stuck_threshold: int = 200 # si joueur joue longtemps sans rien faire → hint


class HintEngine:
    """
    Analyse les métriques du joueur et génère un message d'aide.
    Un cooldown empêche d'envoyer des hints trop souvent.
    """

    def __init__(self, config: HintConfig | None = None):
        self.config = config or HintConfig()
        self.last_hint_tick: int = -9999

    def generate_hint(self, metrics: Metrics, current_tick: int) -> Optional[str]:
        """
        Retourne un message (str) ou None si aucun hint n'est nécessaire.
        """

        # ---- 1) Vérifier le cooldown ----
        if current_tick - self.last_hint_tick < self.config.cooldown_ticks:
            return None

        # ---- 2) Hints basés sur les morts ----
        if metrics.death_count >= self.config.min_deaths_for_warning:
            self.last_hint_tick = current_tick
            return "Tu perds souvent une vie ici… essaie d’éviter les ennemis ou change de trajet."

        # ---- 3) Hints basés sur les fruits ----
        if metrics.fruit_collected < self.config.fruit_goal and metrics.ticks_played > 100:
            self.last_hint_tick = current_tick
            return "Tu devrais collecter davantage de fruits pour progresser dans le niveau."

        # ---- 4) Détection d'inactivité (optionnel mais utile) ----
        if metrics.ticks_played > self.config.stuck_threshold:
            self.last_hint_tick = current_tick
            return "Tu sembles bloqué… essaie un autre chemin ou casse un bloc pour avancer."

        # Pas de hint pertinent
        return None
