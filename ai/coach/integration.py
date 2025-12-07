from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import time

from ai.coach.analyzer import GameAnalyzer
from ai.coach.hints import HintEngine, HintConfig
from ai.design.difficulty_manager import DifficultyManager
from ai.utils.game_api import GameState


@dataclass
class CoachState:
    hint_enabled: bool = True      # toggle H
    last_hint: Optional[str] = None
    last_hint_time: float = 0.0     # pour l'affichage (cooldown visuel)


class CoachIntegration:
    """
    Relié au jeu PyGame :
    - lit le GameState en live
    - alimente l'analyzer
    - récupère un hint
    - décide d'un ajustement de difficulté
    """

    def __init__(self):
        self.analyzer = GameAnalyzer()
        self.hint_engine = HintEngine(HintConfig(cooldown_ticks=40))
        self.difficulty_manager = DifficultyManager()
        self.state = CoachState()

    def update(self, game_state: GameState):
        """
        Met à jour le coach à chaque frame/tick du jeu.
        """
        # 1) Mise à jour des metrics
        self.analyzer.update(game_state)

        # 2) Génération du hint
        if self.state.hint_enabled:
            hint = self.hint_engine.generate_hint(
                self.analyzer.metrics, game_state.tick
            )
            if hint:
                self.state.last_hint = hint
                self.state.last_hint_time = time.time()

    def get_hint(self) -> Optional[str]:
        """Retourne le dernier hint."""
        return self.state.last_hint

    def toggle_hints(self):
        self.state.hint_enabled = not self.state.hint_enabled

    def compute_difficulty(self):
        """
        Retourne une DifficultyConfig (optionnel dans semaine 5).
        """
        return self.difficulty_manager.adjust_difficulty(self.analyzer.metrics)
