# Emplacement: ai/enemies/roles.py
from enum import Enum
import time
import math
from typing import Tuple, Dict
from .a_star import AStarPathfinder

class EnemyRole(Enum):
    HUNTER = "hunter"      # Chasse le joueur activement
    PATROLLER = "patroller" # Fait des rondes

class EnemyAI:
    def __init__(self, enemy_id: int, role: EnemyRole, start_pos: Tuple[int, int]):
        self.id = enemy_id
        self.role = role
        self.pos = list(start_pos) # [x, y] mutable
        self.speed = 2.0
        
        # Pathfinding
        self.pathfinder = AStarPathfinder()
        self.current_path = []
        self.path_index = 0
        
        # Optimisation FPS : Timers
        self.last_repath_time = 0
        self.repath_interval = 0.5 # Recalculer chemin max tous les 0.5s
        
        # Patrouille
        self.patrol_points = [] 
        self.current_patrol_target = 0

    def update(self, game_state) -> Tuple[int, int]:
        """
        Met à jour l'IA et retourne la nouvelle position (x, y).
        """
        current_time = time.time()
        
        # 1. Décision : Où aller ?
        target_pos = None
        
        if self.role == EnemyRole.HUNTER:
            target_pos = game_state.player_pos
            # Pour le chasseur, on rafraîchit le chemin régulièrement car le joueur bouge
            if current_time - self.last_repath_time > self.repath_interval:
                self._calculate_path(target_pos, game_state)
                self.last_repath_time = current_time
                
        elif self.role == EnemyRole.PATROLLER:
            # Logique patrouille (simple aller-retour ou points fixes)
            if not self.patrol_points:
                # Créer des points de patrouille par défaut si vides
                self.patrol_points = [(self.pos[0], self.pos[1]), (self.pos[0], self.pos[1] + 200)]
            
            target_pos = self.patrol_points[self.current_patrol_target]
            
            # Si on est proche du point de patrouille, on passe au suivant
            dist = math.sqrt((self.pos[0]-target_pos[0])**2 + (self.pos[1]-target_pos[1])**2)
            if dist < 10:
                self.current_patrol_target = (self.current_patrol_target + 1) % len(self.patrol_points)
                
            # Patroller recalcule moins souvent (seulement si pas de chemin)
            if not self.current_path:
                self._calculate_path(target_pos, game_state)

        # 2. Mouvement : Suivre le chemin
        return self._move_along_path()

    def _calculate_path(self, target: Tuple[int, int], game_state):
        """Appelle A* avec les obstacles actuels (glace)"""
        # On considère les murs de glace comme obstacles
        obstacles = game_state.iceblocks_pos
        
        path = self.pathfinder.find_path(
            tuple(self.pos), 
            target, 
            obstacles
        )
        
        if path:
            self.current_path = path
            self.path_index = 0

    def _move_along_path(self) -> Tuple[int, int]:
        """Avance vers le prochain point du chemin"""
        if not self.current_path or self.path_index >= len(self.current_path):
            return tuple(map(int, self.pos))

        # Cible immédiate (prochaine case du chemin)
        target_node = self.current_path[self.path_index]
        
        dx = target_node[0] - self.pos[0]
        dy = target_node[1] - self.pos[1]
        dist = math.sqrt(dx**2 + dy**2)

        if dist < self.speed:
            # On est arrivé au noeud, on passe au suivant
            self.pos = list(target_node)
            self.path_index += 1
        else:
            # On avance vers le noeud (vecteur normalisé)
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed

        return tuple(map(int, self.pos))