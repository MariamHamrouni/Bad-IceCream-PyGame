# Emplacement: ai/coach/hints.py
from enum import Enum
from typing import List, Dict, Optional, Tuple
import time
from dataclasses import dataclass
import math

# Assurez-vous que GameState est bien importé si vous utilisez le type hint
# from ai.utils.game_api import GameState 

class HintPriority(Enum):
    """Priorité des conseils"""
    LOW = 1      # Suggestions générales (ex: Mangez des fruits)
    MEDIUM = 2   # Conseils stratégiques (ex: Utilisez la glace)
    HIGH = 3     # Alertes importantes (ex: Zone dangereuse)
    CRITICAL = 4 # Danger immédiat (ex: Ennemi derrière !)

@dataclass
class Hint:
    """Représentation d'un conseil"""
    message: str
    priority: HintPriority
    category: str    # ex: "combat", "movement", "collect"
    duration: float  # Durée d'affichage en secondes
    cooldown: float  # Temps avant de pouvoir répéter ce conseil spécifique
    last_displayed: float = 0  # Timestamp dernier affichage
    
    def is_ready(self, current_time: float) -> bool:
        """Vérifie si le conseil peut être affiché (cooldown individuel)"""
        return current_time - self.last_displayed >= self.cooldown
    
    def mark_displayed(self, current_time: float):
        """Marque le conseil comme affiché"""
        self.last_displayed = current_time

class HintGenerator:
    """Générateur de conseils intelligents basé sur les métriques"""
    
    def __init__(self):
        self.last_hint_time = 0
        self.min_hint_interval = 2.0  # Secondes minimum entre deux générations

    def generate_hints(self, metrics, game_state) -> List[Hint]:
        """
        Logique principale de génération.
        Analyse les métriques et retourne une liste de conseils potentiels.
        """
        hints = []
        current_time = time.time()
        
        # 1. Analyse de danger immédiat (CRITICAL)
        # Si un troll est très proche (< 60 pixels)
        player_pos = game_state.player_pos
        for troll in game_state.trolls_pos:
            dist = math.sqrt((player_pos[0] - troll[0])**2 + (player_pos[1] - troll[1])**2)
            if dist < 80:
                hints.append(Hint(
                    message="Attention ! Ennemi proche !",
                    priority=HintPriority.CRITICAL,
                    category="combat",
                    duration=2.0,
                    cooldown=5.0
                ))

        # 2. Analyse de stratégie (MEDIUM)
        # Si le joueur n'utilise pas ses blocs de glace
        if metrics.ice_block_usage == 0 and metrics.death_count > 0:
            hints.append(Hint(
                message="Espace pour créer/détruire des murs de glace !",
                priority=HintPriority.MEDIUM,
                category="mechanic",
                duration=4.0,
                cooldown=20.0
            ))

        # 3. Analyse de mouvement (HIGH)
        # Si le joueur meurt souvent au même endroit (Zone à risque)
        # On convertit la pos joueur en grille grossière (50x50)
        grid_pos = (int(player_pos[0]//50)*50, int(player_pos[1]//50)*50)
        if metrics.risk_zones.get(grid_pos, 0) > 300: # ~5 secondes passé en zone dangereuse
            hints.append(Hint(
                message="Cette zone est dangereuse, fuyez !",
                priority=HintPriority.HIGH,
                category="movement",
                duration=3.0,
                cooldown=15.0
            ))

        return hints