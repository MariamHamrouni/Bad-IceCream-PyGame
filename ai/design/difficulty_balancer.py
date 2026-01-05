from typing import Dict, List

class DifficultyBalancer:
    """Ajuste la difficulté du jeu en fonction des performances passées"""
    
    def __init__(self):
        self.player_history = []
    
    def record_session(self, metrics: Dict):
        self.player_history.append(metrics)
        if len(self.player_history) > 10:
            self.player_history.pop(0)

    def get_suggested_difficulty(self) -> float:
        if not self.player_history:
            return 0.3 
            
        win_rate = sum(1 for m in self.player_history if m.get('win')) / len(self.player_history)
        avg_deaths = sum(m.get('death_count', 0) for m in self.player_history) / len(self.player_history)
        
        difficulty = 0.5
        if win_rate > 0.8: difficulty += 0.2
        elif win_rate < 0.2: difficulty -= 0.2
        
        if avg_deaths > 3: difficulty -= 0.15
        if avg_deaths == 0: difficulty += 0.1
        
        return max(0.1, min(1.0, difficulty))