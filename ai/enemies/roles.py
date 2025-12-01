"""
Rôles intelligents pour les ennemis
"""
from enum import Enum
from typing import List, Tuple, Optional, Dict
import random
from dataclasses import dataclass
from .a_star import AStarPathfinder
from ai.utils.game_api import GameState

class EnemyRole(Enum):
    """Types de rôles pour les ennemis"""
    HUNTER = "hunter"      # Chasse le joueur
    PATROLLER = "patroller" # Patrouille des waypoints
    BLOCKER = "blocker"    # Bloque les passages stratégiques

@dataclass
class Waypoint:
    """Point de patrouille pour les patrouilleurs"""
    x: int
    y: int
    wait_time: float = 0.0

class EnemyAI:
    """Classe de base pour l'IA des ennemis"""
    
    def __init__(self, role: EnemyRole, grid_width: int = 20, grid_height: int = 15):
        self.role = role
        self.pathfinder = AStarPathfinder(grid_width, grid_height)
        self.current_path: List[Tuple[int, int]] = []
        self.current_target: Optional[Tuple[int, int]] = None
        self.state: Dict = {}
        
    def update(self, enemy_pos: Tuple[int, int], game_state: GameState) -> Tuple[int, int]:
        """
        Met à jour l'IA et retourne la prochaine position cible
        
        Returns:
            Position (x, y) vers laquelle se déplacer
        """
        raise NotImplementedError

class HunterAI(EnemyAI):
    """IA Chasseur - Poursuit activement le joueur"""
    
    def __init__(self, aggression: float = 0.8):
        super().__init__(EnemyRole.HUNTER)
        self.aggression = aggression  # 0.0 = prudent, 1.0 = agressif
        self.last_player_pos: Optional[Tuple[int, int]] = None
        self.patience = 0  # Compteur de patience avant changement de stratégie
        
    def update(self, enemy_pos: Tuple[int, int], game_state: GameState) -> Tuple[int, int]:
        player_pos = game_state.player_pos
        
        # Si joueur mort ou invulnérable, patrouiller
        if not game_state.player_alive:
            return self._patrol(enemy_pos, game_state)
        
        # Calculer la distance au joueur
        distance = self._calculate_distance(enemy_pos, player_pos)
        
        # Déterminer la stratégie basée sur la distance et l'agressivité
        if distance < 100:  # Très proche
            # Attaquer directement
            obstacles = game_state.iceblocks_pos
            self.current_path = self.pathfinder.find_path(enemy_pos, player_pos, obstacles)
            self.last_player_pos = player_pos
            self.patience = 0
            
        elif distance < 300:  # Distance moyenne
            # Chasser avec prédiction
            if self.last_player_pos:
                # Prédire le mouvement du joueur
                predicted_pos = self._predict_player_position(player_pos, self.last_player_pos)
                obstacles = game_state.iceblocks_pos
                self.current_path = self.pathfinder.find_path(enemy_pos, predicted_pos, obstacles)
            self.last_player_pos = player_pos
            self.patience = 0
            
        else:  # Loin
            # Patience ou patrouille
            self.patience += 1
            if self.patience > 30:  # Attendre 30 frames avant de patrouiller
                return self._patrol(enemy_pos, game_state)
            elif self.last_player_pos:
                # Continuer vers la dernière position connue
                obstacles = game_state.iceblocks_pos
                self.current_path = self.pathfinder.find_path(enemy_pos, self.last_player_pos, obstacles)
        
        # Retourner la prochaine position du chemin
        if self.current_path and len(self.current_path) > 1:
            return self.current_path[1]  # La première position est la position actuelle
        else:
            return enemy_pos  # Rester sur place
    
    def _predict_player_position(self, current_pos: Tuple[int, int], 
                                 last_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Prédit la position future du joueur"""
        dx = current_pos[0] - last_pos[0]
        dy = current_pos[1] - last_pos[1]
        
        # Extrapoler la position
        predicted_x = current_pos[0] + dx * 2
        predicted_y = current_pos[1] + dy * 2
        
        # Limiter aux bornes du jeu
        predicted_x = max(50, min(predicted_x, 770))
        predicted_y = max(50, min(predicted_y, 572))
        
        return (predicted_x, predicted_y)
    
    def _patrol(self, enemy_pos: Tuple[int, int], game_state: GameState) -> Tuple[int, int]:
        """Patrouille autour de la position actuelle"""
        # Générer des points de patrouille aléatoires autour de l'ennemi
        patrol_radius = 200
        target_x = enemy_pos[0] + random.randint(-patrol_radius, patrol_radius)
        target_y = enemy_pos[1] + random.randint(-patrol_radius, patrol_radius)
        
        # Limiter aux bornes
        target_x = max(50, min(target_x, 770))
        target_y = max(50, min(target_y, 572))
        
        obstacles = game_state.iceblocks_pos
        self.current_path = self.pathfinder.find_path(enemy_pos, (target_x, target_y), obstacles)
        
        if self.current_path and len(self.current_path) > 1:
            return self.current_path[1]
        return enemy_pos
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

class PatrollerAI(EnemyAI):
    """IA Patrouilleur - Suit un circuit de waypoints"""
    
    def __init__(self, waypoints: List[Waypoint]):
        super().__init__(EnemyRole.PATROLLER)
        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.wait_timer = 0.0
        
    def update(self, enemy_pos: Tuple[int, int], game_state: GameState) -> Tuple[int, int]:
        current_waypoint = self.waypoints[self.current_waypoint_index]
        
        # Vérifier si on est arrivé au waypoint
        distance = self._calculate_distance(enemy_pos, (current_waypoint.x, current_waypoint.y))
        
        if distance < 20:  # Arrivé au waypoint
            # Attendre si nécessaire
            if self.wait_timer < current_waypoint.wait_time:
                self.wait_timer += 1.0 / 60.0  # Incrémenter par frame
                return enemy_pos  # Rester sur place
            
            # Passer au waypoint suivant
            self.wait_timer = 0.0
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.waypoints)
            current_waypoint = self.waypoints[self.current_waypoint_index]
        
        # Calculer le chemin vers le waypoint
        obstacles = game_state.iceblocks_pos
        self.current_path = self.pathfinder.find_path(
            enemy_pos, 
            (current_waypoint.x, current_waypoint.y), 
            obstacles
        )
        
        if self.current_path and len(self.current_path) > 1:
            return self.current_path[1]
        return enemy_pos
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

class BlockerAI(EnemyAI):
    """IA Bloqueur - Bloque les passages stratégiques"""
    
    def __init__(self, strategic_points: List[Tuple[int, int]]):
        super().__init__(EnemyRole.BLOCKER)
        self.strategic_points = strategic_points
        self.current_strategic_index = 0
        self.blocking_timer = 0.0
        self.block_duration = 5.0  # Secondes à bloquer un point
        
    def update(self, enemy_pos: Tuple[int, int], game_state: GameState) -> Tuple[int, int]:
        strategic_point = self.strategic_points[self.current_strategic_index]
        
        # Si proche du point stratégique, bloquer
        distance = self._calculate_distance(enemy_pos, strategic_point)
        
        if distance < 30:  # Positionné sur le point stratégique
            if self.blocking_timer < self.block_duration:
                self.blocking_timer += 1.0 / 60.0
                
                # Tourner sur place pour surveiller
                if random.random() < 0.1:  # 10% de chance de changer de direction
                    return self._look_around(enemy_pos)
                return enemy_pos  # Rester en place
            else:
                # Passer au point suivant
                self.blocking_timer = 0.0
                self.current_strategic_index = (self.current_strategic_index + 1) % len(self.strategic_points)
                strategic_point = self.strategic_points[self.current_strategic_index]
        
        # Se déplacer vers le point stratégique
        obstacles = game_state.iceblocks_pos
        self.current_path = self.pathfinder.find_path(enemy_pos, strategic_point, obstacles)
        
        if self.current_path and len(self.current_path) > 1:
            return self.current_path[1]
        return enemy_pos
    
    def _look_around(self, current_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Simule l'ennemi qui regarde autour de lui"""
        # Petits mouvements aléatoires sur place
        dx = random.randint(-10, 10)
        dy = random.randint(-10, 10)
        return (current_pos[0] + dx, current_pos[1] + dy)
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

# Factory pour créer des IA selon le rôle
def create_enemy_ai(role: EnemyRole, **kwargs) -> EnemyAI:
    """Crée une instance d'IA selon le rôle spécifié"""
    if role == EnemyRole.HUNTER:
        return HunterAI(**kwargs)
    elif role == EnemyRole.PATROLLER:
        return PatrollerAI(**kwargs)
    elif role == EnemyRole.BLOCKER:
        return BlockerAI(**kwargs)
    else:
        raise ValueError(f"Rôle inconnu: {role}")