import json
import time
import sys
import random
from pathlib import Path
from typing import Dict, List

# Configuration des chemins
sys.path.append(str(Path(__file__).parent.parent))

from ai.utils.game_api import GameState
from ai.enemies.roles import EnemyAI, EnemyRole
from ai.enemies.coordinator import get_global_coordinator

class SimulationRunner:
    """Simulateur 'Headless' pour tester l'IA rapidement"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.enemies: List[EnemyAI] = []
        self.coordinator = get_global_coordinator()
        
        # Statistiques
        self.stats = {
            "ticks": 0,
            "catches": 0,
            "path_recalculations": 0
        }

    def setup_scenario(self, num_hunters=2, num_patrollers=1):
        """Prépare une arène de test"""
        self.enemies = []
        
        # Création des Chasseurs
        for i in range(num_hunters):
            start_pos = (random.randint(50, 750), random.randint(50, 550))
            # Notez l'utilisation de la classe unique EnemyAI
            ai = EnemyAI(
                enemy_id=i, 
                role=EnemyRole.HUNTER, 
                start_pos=start_pos
            )
            self.enemies.append(ai)
            
        # Création des Patrouilleurs
        for i in range(num_patrollers):
            start_pos = (random.randint(50, 750), random.randint(50, 550))
            ai = EnemyAI(
                enemy_id=100+i, 
                role=EnemyRole.PATROLLER, 
                start_pos=start_pos
            )
            self.enemies.append(ai)

    def run(self, duration_seconds=10):
        """Lance la simulation"""
        print(f"🚀 Lancement de la simulation ({duration_seconds}s simulées)...")
        
        # Position fixe du joueur pour le test
        player_pos = (400, 300)
        
        # On simule 60 ticks par seconde
        total_ticks = duration_seconds * 60
        start_real_time = time.time()
        
        for tick in range(total_ticks):
            # Créer un état factice
            fake_state = GameState(
                player_pos=player_pos,
                player_alive=True,
                trolls_pos=[tuple(e.pos) for e in self.enemies],
                iceblocks_pos=[], # Pas de murs pour ce test simple
                fruits_pos=[],
                fruits_collected=[],
                level=1, round=1, timer=tick/60.0, score=0
            )
            
            # Mise à jour des IA
            for enemy in self.enemies:
                # L'ennemi réfléchit et bouge
                new_pos = enemy.update(fake_state)
                
                # Vérification capture (distance < 30px)
                dist = ((new_pos[0]-player_pos[0])**2 + (new_pos[1]-player_pos[1])**2)**0.5
                if dist < 30:
                    self.stats["catches"] += 1
                    # On téléporte le joueur pour continuer le test
                    player_pos = (random.randint(50, 750), random.randint(50, 550))

        end_real_time = time.time()
        calc_time = end_real_time - start_real_time
        
        print(f"✅ Simulation terminée en {calc_time:.4f}s (temps réel)")
        print(f"📊 Résultats :")
        print(f"   - Ticks simulés : {total_ticks}")
        print(f"   - Captures du joueur : {self.stats['catches']}")
        print(f"   - Efficacité : {self.stats['catches'] / (duration_seconds/60):.2f} captures/minute")

if __name__ == "__main__":
    sim = SimulationRunner()
    sim.setup_scenario()
    sim.run()