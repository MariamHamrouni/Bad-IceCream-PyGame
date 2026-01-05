# Emplacement: ai/coach/analyzer.py
import time
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

# Assurez-vous que GameState est accessible via ce chemin
from ai.utils.game_api import GameState

@dataclass
class PerformanceMetrics:
    """Conteneur pour toutes les métriques de performance"""
    death_count: int = 0
    fruit_order: List[str] = field(default_factory=list)
    time_between_deaths: List[float] = field(default_factory=list)
    
    # Optimisation : On initialise à None pour ne pas allouer de mémoire inutilement
    player_routes: List[List[Tuple[int, int]]] = None 
    
    risk_zones: Dict[Tuple[int, int], int] = field(default_factory=dict)
    ice_block_usage: int = 0
    start_time: float = 0.0
    last_death_time: float = 0.0
    fruits_collected_session: int = 0

    def add_route_point(self, pos: Tuple[int, int]):
        """Ajoute un point à la route actuelle avec optimisation mémoire"""
        if self.player_routes is None:
            self.player_routes = [[]]
        
        current_route = self.player_routes[-1]
        
        # OPTIMISATION : N'ajouter que si le joueur a bougé significativement (> 5 pixels)
        if current_route:
            last_pos = current_route[-1]
            dist = math.sqrt((pos[0]-last_pos[0])**2 + (pos[1]-last_pos[1])**2)
            if dist < 5.0:
                return # On ignore ce point, pas assez de mouvement

        current_route.append(pos)
        
        # SÉCURITÉ MÉMOIRE : Limiter la taille de l'historique (Rolling buffer)
        # Si la route dépasse 2000 points, on retire les plus anciens
        if len(current_route) > 2000: 
            current_route.pop(0)

class PerformanceAnalyzer:
    """Analyse les performances du joueur en temps réel"""
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.metrics.start_time = time.time()
        self.metrics.last_death_time = time.time()
        self.last_player_alive = True
        self.last_fruits_count = -1 # -1 indique pas encore initialisé

    def analyze_snapshot(self, state: GameState):
        """Met à jour les métriques à partir d'un snapshot du jeu"""
        current_time = time.time()
        
        # Initialisation du compteur de fruits au premier tick
        if self.last_fruits_count == -1:
            self.last_fruits_count = len(state.fruits_pos)

        # 1. Détection de Mort (Transition Vivant -> Mort)
        if self.last_player_alive and not state.player_alive:
            self.metrics.death_count += 1
            time_since_death = current_time - self.metrics.last_death_time
            self.metrics.time_between_deaths.append(time_since_death)
            self.metrics.last_death_time = current_time
            
            # On commence une nouvelle route pour la nouvelle vie
            if self.metrics.player_routes:
                self.metrics.player_routes.append([])

        self.last_player_alive = state.player_alive

        # 2. Suivi de position (Path tracking) si vivant
        if state.player_alive:
            self.metrics.add_route_point(state.player_pos)
            self._analyze_risk_zones(state)

        # 3. Détection de fruits collectés
        current_fruits_count = len(state.fruits_pos)
        if current_fruits_count < self.last_fruits_count:
            # Un ou plusieurs fruits ont été mangés
            diff = self.last_fruits_count - current_fruits_count
            self.metrics.fruits_collected_session += diff
            # Note: Pour savoir quel type de fruit, il faudrait comparer les listes précises
            # Ici on fait simple pour la performance
            
        self.last_fruits_count = current_fruits_count

    def _analyze_risk_zones(self, state: GameState):
        """Identifie si le joueur reste trop longtemps près des ennemis"""
        player_x, player_y = state.player_pos
        
        # Vérifier la distance avec chaque troll
        for troll_pos in state.trolls_pos:
            tx, ty = troll_pos
            dist = math.sqrt((player_x - tx)**2 + (player_y - ty)**2)
            
            if dist < 120: # Zone de danger (proche)
                # On arrondit la position à la grille (50px) pour regrouper les données
                grid_pos = (int(player_x // 50) * 50, int(player_y // 50) * 50)
                # On incrémente le compteur de "danger" pour cette zone
                self.metrics.risk_zones[grid_pos] = self.metrics.risk_zones.get(grid_pos, 0) + 1
    def reset(self):
        """
        Réinitialise les métriques pour commencer un nouveau niveau
        tout en gardant l'instance de l'analyseur vivante.
        """
        # On recrée une structure de métriques vierge
        self.metrics = PerformanceMetrics()
        
        # On réinitialise le temps de départ
        self.metrics.session_start_time = time.time()
        
        print("🧠 Coach IA : Mémoire effacée pour le nouveau niveau.")