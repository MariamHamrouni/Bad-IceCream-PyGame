# ai/coach/analyzer.py
import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

from ai.utils.game_api import GameState, GameAPI

@dataclass
class PerformanceMetrics:
    """Conteneur pour toutes les métriques de performance"""
    death_count: int = 0
    fruit_order: List[str] = None  # Types de fruits dans l'ordre de collecte
    time_between_deaths: List[float] = None  # Temps entre chaque mort
    average_fruit_time: float = 0.0  # Temps moyen par fruit
    player_routes: List[List[Tuple[int, int]]] = None  # Trajectoires du joueur
    risk_zones: Dict[Tuple[int, int], int] = None  # Zones à haut risque
    ice_block_usage: int = 0  # Nombre de blocs de glace placés
    session_start_time: float = 0.0
    last_death_time: float = 0.0
    fruits_collected_this_session: int = 0

class PerformanceAnalyzer:
    """
    Analyse les performances du joueur en temps réel
    et génère des métriques pour le coach
    """
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.previous_state: Optional[GameState] = None
        self.current_session_start = time.time()
        self.tick_count = 0
        
        # Réinitialiser les listes
        self.metrics.fruit_order = []
        self.metrics.time_between_deaths = []
        self.metrics.player_routes = []
        self.metrics.risk_zones = {}
        
        # Route actuelle du joueur
        self.current_route: List[Tuple[int, int]] = []
    
    def analyze_snapshot(self, game_state: GameState) -> Dict:
        """
        Analyse un snapshot du jeu et met à jour les métriques
        
        Args:
            game_state: État actuel du jeu
            
        Returns:
            Dict: Métriques calculées
        """
        self.tick_count += 1
        self.last_game_state = game_state  #Stocker le dernier état pour l'export
        if self.tick_count == 1:
            self.current_session_start = game_state.timer
        # Détection des événements
        self._detect_death(game_state)
        self._detect_fruit_collection(game_state)
        self._track_player_movement(game_state)
        self._analyze_risk_zones(game_state)
        
        # Calcul des métriques dérivées
        self._calculate_derived_metrics(game_state)
        
        self.previous_state = game_state
        
        return self._get_current_metrics(game_state)
    
    def _detect_death(self, game_state: GameState):
        """Détecte si le joueur vient de mourir"""
        if self.previous_state and self.previous_state.player_alive and not game_state.player_alive:
            self.metrics.death_count += 1
            
            # Calcul du temps depuis la dernière mort
            current_time = game_state.timer
            if self.metrics.last_death_time > 0:
                time_since_last_death = current_time - self.metrics.last_death_time
                self.metrics.time_between_deaths.append(time_since_last_death)
            
            self.metrics.last_death_time = current_time
            
            # Réinitialiser le compteur de fruits pour la nouvelle session
            self.metrics.fruits_collected_this_session = 0
            self.current_session_start = current_time
    
    def _detect_fruit_collection(self, game_state: GameState):
        """Détecte la collecte de nouveaux fruits"""
        if not self.previous_state:
            return
        
        # Fruits dans l'état précédent
        previous_fruits = set(self.previous_state.fruits_pos)
        current_fruits = set(game_state.fruits_pos)
        
        # Fruits collectés (disparus entre les deux états)
        collected_fruits = previous_fruits - current_fruits
        print(f"🔍 Debug: {len(collected_fruits)} fruits collectés")
        for fruit_pos in collected_fruits:
            # Pour l'instant on utilise une représentation simple du fruit
            # Plus tard, on pourrait avoir des types de fruits différents
            fruit_type = self._get_fruit_type(fruit_pos, game_state)
            self.metrics.fruit_order.append(fruit_type)
            self.metrics.fruits_collected_this_session += 1
    
    def _get_fruit_type(self, fruit_pos: Tuple[int, int], game_state: GameState) -> str:
        """
        Détermine le type de fruit basé sur la position
        (À adapter selon la logique réelle de votre jeu)
        """
        # Exemple simple - dans la réalité, vous auriez cette information dans game_state
        fruit_types = ["apple", "banana", "grape", "orange", "strawberry"]
        hash_val = hash(fruit_pos) % len(fruit_types)
        return fruit_types[hash_val]
    
    def _track_player_movement(self, game_state: GameState):
        """Track la trajectoire du joueur"""
        current_pos = game_state.player_pos
        
        if not self.current_route:
            self.current_route.append(current_pos)
        else:
            last_pos = self.current_route[-1]
            # N'ajouter que si le joueur a bougé significativement
            if self._distance(last_pos, current_pos) > 20:  # Seuil de mouvement
                self.current_route.append(current_pos)
        
        # Si la route devient trop longue, enregistrer et recommencer
        if len(self.current_route) > 50:
            self.metrics.player_routes.append(self.current_route.copy())
            self.current_route = [current_pos]
    
    def _analyze_risk_zones(self, game_state: GameState):
        """Identifie les zones à risque (proches des ennemis)"""
        player_pos = game_state.player_pos
        
        for troll_pos in game_state.trolls_pos:
            distance = self._distance(player_pos, troll_pos)
            if distance < 100:  # Zone de risque si ennemi à moins de 100 pixels
                zone_key = self._quantize_position(player_pos)
                self.metrics.risk_zones[zone_key] = self.metrics.risk_zones.get(zone_key, 0) + 1
    
    def _calculate_derived_metrics(self, game_state: GameState):
        """Calcule les métriques dérivées"""
        # Temps moyen par fruit dans cette session
        if self.metrics.fruits_collected_this_session > 0:
            session_duration = game_state.timer - self.current_session_start
            self.metrics.average_fruit_time = session_duration / self.metrics.fruits_collected_this_session
    
    def _distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calcule la distance euclidienne entre deux points"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    
    def _quantize_position(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Quantize une position pour regrouper les zones proches"""
        grid_size = 40  # Même que votre grille de jeu
        return (pos[0] // grid_size * grid_size, pos[1] // grid_size * grid_size)
    
    def _get_current_metrics(self,game_state:GameState) -> Dict:
        """Retourne les métriques actuelles sous forme de dict"""
        session_duration = game_state.timer - self.current_session_start
        return {
            "tick_count": self.tick_count,
            "death_count": self.metrics.death_count,
            "fruit_order": self.metrics.fruit_order,
            "time_between_deaths": self.metrics.time_between_deaths,
            "average_fruit_time": self.metrics.average_fruit_time,
            "current_route_length": len(self.current_route),
            "total_routes_recorded": len(self.metrics.player_routes),
            "high_risk_zones": len(self.metrics.risk_zones),
            "fruits_collected_this_session": self.metrics.fruits_collected_this_session,
            "session_duration": session_duration,
            "total_fruits_collected": len(self.metrics.fruit_order)
        }
    
    def export_metrics(self, filename: str = None):
        """Exporte les métriques en JSON"""
        if filename is None:
            filename = f"metrics_tick_{self.tick_count}.json"
        if hasattr(self, 'last_game_state'):
            current_metrics = self._get_current_metrics(self.last_game_state)
        else:
        # Valeurs par défaut si pas de game_state disponible
            current_metrics = self._get_current_metrics(GameState((0,0), True, [], [], [], [], 1, 1, 0.0, 0))
    
        metrics_data = {
            "schema_version": GameAPI.SCHEMA_VERSION,
            "export_time": time.time(),  # ← Ceci est normal, c'est le timestamp réel de l'export
            "tick_count": self.tick_count,
            **current_metrics
        }
        GameAPI.export_metrics(metrics_data, filename)
        return metrics_data
    
    def reset(self):
        """Réinitialise l'analyseur pour une nouvelle session"""
        self.__init__()
        