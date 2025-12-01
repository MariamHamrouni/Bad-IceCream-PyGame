# demo_coach_hints.py
"""
Script de démonstration pour le système de conseils du coach IA
"""
import time
import sys
import os

# Ajouter le dossier ai au path Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai'))

from coach.analyzer import PerformanceAnalyzer
from coach.hint_manager import HintManager
from utils.game_api import GameState

def simulate_game_scenarios():
    """Simule différents scénarios de jeu pour tester les conseils"""
    scenarios = [
        {
            "name": "🎯 Débutant qui meurt souvent",
            "metrics": {
                'death_count': 4,
                'fruit_order': ['apple'],
                'time_between_deaths': [8.0, 6.0, 5.0],
                'average_fruit_time': 12.0,
                'high_risk_zones': 7,
                'total_fruits_collected': 1,
                'tick_count': 200,
                'ice_block_usage': 0
            },
            "game_state": GameState(
                player_pos=(400, 300),
                player_alive=True,
                trolls_pos=[(380, 290), (420, 310)],
                iceblocks_pos=[],
                fruits_pos=[(350, 250)],
                fruits_collected=[],
                level=1,
                round=1,
                timer=60.0,
                score=50
            )
        },
        {
            "name": "🚨 Danger immédiat",
            "metrics": {
                'death_count': 0,
                'fruit_order': [],
                'time_between_deaths': [],
                'average_fruit_time': 0,
                'high_risk_zones': 1,
                'total_fruits_collected': 0,
                'tick_count': 50,
                'ice_block_usage': 0
            },
            "game_state": GameState(
                player_pos=(400, 300),
                player_alive=True,
                trolls_pos=[(405, 305)],  # Très proche!
                iceblocks_pos=[],
                fruits_pos=[],
                fruits_collected=[],
                level=1,
                round=1,
                timer=10.0,
                score=0
            )
        },
        {
            "name": "🏆 Presque fin de niveau",
            "metrics": {
                'death_count': 1,
                'fruit_order': ['apple', 'banana', 'grape', 'orange'],
                'time_between_deaths': [45.0],
                'average_fruit_time': 5.5,
                'high_risk_zones': 2,
                'total_fruits_collected': 4,
                'tick_count': 180,
                'ice_block_usage': 3
            },
            "game_state": GameState(
                player_pos=(400, 300),
                player_alive=True,
                trolls_pos=[(200, 200)],
                iceblocks_pos=[(350, 300)],
                fruits_pos=[(450, 350)],  # Un seul fruit restant
                fruits_collected=[(100, 100), (200, 200), (300, 300), (400, 400)],
                level=1,
                round=1,
                timer=90.0,
                score=200
            )
        },
        {
            "name": "🔄 Pattern répétitif",
            "metrics": {
                'death_count': 0,
                'fruit_order': ['apple', 'banana', 'apple', 'banana', 'apple', 'banana'],
                'time_between_deaths': [],
                'average_fruit_time': 6.0,
                'high_risk_zones': 3,
                'total_fruits_collected': 6,
                'tick_count': 300,
                'ice_block_usage': 1
            },
            "game_state": GameState(
                player_pos=(400, 300),
                player_alive=True,
                trolls_pos=[(300, 300)],
                iceblocks_pos=[(350, 300)],
                fruits_pos=[(500, 400)],
                fruits_collected=[],
                level=1,
                round=1,
                timer=120.0,
                score=300
            )
        }
    ]
    
    return scenarios

def demo_coach_hints():
    """Démonstration du système de conseils du coach IA"""
    print("🎓 Démonstration du Système de Conseils - Coach IA")
    print("=" * 60)
    
    # Initialisation
    analyzer = PerformanceAnalyzer()
    hint_manager = HintManager()
    
    scenarios = simulate_game_scenarios()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'#'*50}")
        print(f"Scénario {i}: {scenario['name']}")
        print(f"{'#'*50}")
        
        # Analyser les métriques (simulées pour la démo)
        metrics = scenario['metrics']
        game_state = scenario['game_state']
        
        print(f"\n📊 Métriques du joueur:")
        print(f"  • Morts: {metrics['death_count']}")
        print(f"  • Fruits collectés: {metrics['total_fruits_collected']}")
        print(f"  • Temps moyen/fruit: {metrics['average_fruit_time']:.1f}s")
        print(f"  • Zones à risque: {metrics['high_risk_zones']}")
        print(f"  • Blocs utilisés: {metrics['ice_block_usage']}")
        print(f"  • Ordre des fruits: {metrics['fruit_order']}")
        
        # Générer les conseils
        print(f"\n💡 Conseils générés:")
        hints = hint_manager.update(metrics, game_state)
        
        if hints:
            for j, hint in enumerate(hints, 1):
                priority_icon = {
                    "LOW": "💡",
                    "MEDIUM": "📝", 
                    "HIGH": "⚠️",
                    "CRITICAL": "🚨"
                }.get(hint.priority.name, "💬")
                
                print(f"  {j}. {priority_icon} [{hint.priority.name}] {hint.message}")
                print(f"     📁 Catégorie: {hint.category} | ⏱️ Durée: {hint.duration}s")
        else:
            print("  🔇 Aucun conseil pour le moment (cooldown ou pas pertinent)")
        
        # Statistiques du gestionnaire
        stats = hint_manager.get_stats()
        print(f"\n📈 Stats du coach: {stats['total_hints_generated']} conseils générés au total")
        
        # Pause entre les scénarios
        if i < len(scenarios):
            input("\n⏎ Appuyez sur Entrée pour le scénario suivant...")
        else:
            print("\n" + "="*60)
            print("🎉 DÉMONSTRATION TERMINÉE!")
            print("="*60)
    
    # Résumé final
    final_stats = hint_manager.get_stats()
    print(f"\n📊 RÉSUMÉ FINAL:")
    print(f"  • Total conseils générés: {final_stats['total_hints_generated']}")
    print(f"  • Conseils actuellement affichés: {final_stats['currently_displayed']}")
    print(f"  • Système activé: {'✅ OUI' if final_stats['enabled'] else '❌ NON'}")
    
    if final_stats['recent_hints']:
        print(f"  • 3 derniers conseils:")
        for hint_info in final_stats['recent_hints'][-3:]:
            print(f"    - {hint_info['message']}")

if __name__ == "__main__":
    demo_coach_hints()