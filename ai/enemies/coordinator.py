# Emplacement: ai/enemies/coordinator.py
from typing import List, Dict, Tuple
import time

class EnemyCoordinator:
    """Singleton qui gère la communication entre ennemis"""
    _instance = None
    
    @staticmethod
    def get_instance():
        if EnemyCoordinator._instance is None:
            EnemyCoordinator._instance = EnemyCoordinator()
        return EnemyCoordinator._instance
    
    def __init__(self):
        self.shared_memory = {
            "last_player_pos": None,
            "last_seen_time": 0
        }
        self.messages = []
    
    def report_player_location(self, pos: Tuple[int, int]):
        """Un ennemi signale la position du joueur à tous"""
        current_time = time.time()
        
        # Anti-spam : Mise à jour seulement si l'info est nouvelle (> 0.5s)
        if (current_time - self.shared_memory["last_seen_time"]) > 0.5:
            self.shared_memory["last_player_pos"] = pos
            self.shared_memory["last_seen_time"] = current_time
            self._add_message(f"Player spotted at {pos}")

    def get_last_known_player_pos(self) -> Tuple[int, int]:
        """Retourne la dernière position connue ou None si trop vieux"""
        if time.time() - self.shared_memory["last_seen_time"] < 5.0:
             # L'info est valide pendant 5 secondes
            return self.shared_memory["last_player_pos"]
        return None

    def _add_message(self, msg: str):
        """Ajoute un message au log et nettoie"""
        self.messages.append({"time": time.time(), "msg": msg})
        
        # Nettoyage mémoire : garde max 50 messages
        if len(self.messages) > 50:
            self.messages.pop(0)

# Fonction helper globale
def get_coordinator():
    return EnemyCoordinator.get_instance()