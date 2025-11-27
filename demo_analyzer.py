# demo_analyzer_fixed.py
"""
Script de démonstration CORRIGÉ pour le PerformanceAnalyzer
"""
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'ai'))

from coach.analyzer import PerformanceAnalyzer
from utils.game_api import GameState

def demo_analyzer_fixed():
    """Démonstration CORRIGÉE du PerformanceAnalyzer"""
    print("🚀 Démonstration CORRIGÉE du PerformanceAnalyzer")
    print("=" * 50)
    
    analyzer = PerformanceAnalyzer()
    
    # Simuler une session de jeu avec des timers RÉALISTES
    print("📊 Simulation d'une session de jeu réaliste...")
    
    # État 1: Début de jeu (timer = 0.0)
    state1 = GameState(
        player_pos=(100, 100),
        player_alive=True,
        trolls_pos=[(200, 150)],
        iceblocks_pos=[(150, 100)],
        fruits_pos=[(120, 120), (180, 180)],
        fruits_collected=[],
        level=1,
        round=1,
        timer=0.0,  # Début du jeu
        score=0
    )
    
    print("\n🎮 État 1 - Début de partie (timer=0.0s):")
    metrics1 = analyzer.analyze_snapshot(state1)
    print(f"  • Fruits cette session: {metrics1['fruits_collected_this_session']}")
    print(f"  • Total fruits: {metrics1['total_fruits_collected']}")
    print(f"  • Nombre de morts: {metrics1['death_count']}")
    
    # État 2: Après 3 secondes, joueur collecte un fruit
    state2 = GameState(
        player_pos=(120, 120),
        player_alive=True,
        trolls_pos=[(200, 150)],
        iceblocks_pos=[(150, 100)],
        fruits_pos=[(180, 180)],  # Un fruit collecté
        fruits_collected=[(120, 120)],
        level=1,
        round=1,
        timer=3.0,  # 3 secondes écoulées
        score=50
    )
    
    print("\n🎮 État 2 - Fruit collecté (timer=3.0s):")
    metrics2 = analyzer.analyze_snapshot(state2)
    print(f"  • Fruits cette session: {metrics2['fruits_collected_this_session']}")
    print(f"  • Total fruits: {metrics2['total_fruits_collected']}")
    print(f"  • Ordre des fruits: {metrics2['fruit_order']}")
    print(f"  • Temps moyen/fruit: {metrics2['average_fruit_time']:.2f}s")
    
    # État 3: Après 8 secondes, joueur collecte un autre fruit
    state3 = GameState(
        player_pos=(180, 180),
        player_alive=True,
        trolls_pos=[(200, 150)],
        iceblocks_pos=[(150, 100)],
        fruits_pos=[],  # Tous fruits collectés
        fruits_collected=[(120, 120), (180, 180)],
        level=1,
        round=1,
        timer=8.0,  # 8 secondes écoulées
        score=100
    )
    
    print("\n🎮 État 3 - Tous fruits collectés (timer=8.0s):")
    metrics3 = analyzer.analyze_snapshot(state3)
    print(f"  • Fruits cette session: {metrics3['fruits_collected_this_session']}")
    print(f"  • Total fruits: {metrics3['total_fruits_collected']}")
    print(f"  • Ordre complet: {metrics3['fruit_order']}")
    print(f"  • Temps moyen/fruit: {metrics3['average_fruit_time']:.2f}s")
    print(f"  • Zones à risque: {metrics3['high_risk_zones']}")
    
    # État 4: Après 12 secondes, joueur meurt
    state4 = GameState(
        player_pos=(200, 200),
        player_alive=False,  # Mort!
        trolls_pos=[(200, 200)],
        iceblocks_pos=[(150, 100)],
        fruits_pos=[],
        fruits_collected=[(120, 120), (180, 180)],
        level=1,
        round=1,
        timer=12.0,  # 12 secondes écoulées
        score=100
    )
    
    print("\n🎮 État 4 - Joueur meurt (timer=12.0s):")
    metrics4 = analyzer.analyze_snapshot(state4)
    print(f"  • Fruits cette session: {metrics4['fruits_collected_this_session']}")  # Doit être 0 après mort
    print(f"  • Total fruits: {metrics4['total_fruits_collected']}")  # Doit rester 2
    print(f"  • Nombre de morts: {metrics4['death_count']}")
    print(f"  • Temps entre morts: {metrics4['time_between_deaths']}")
    
    # Exporter les métriques finales
    print(f"\n💾 Export des métriques...")
    final_metrics = analyzer.export_metrics("demo_session_fixed.json")
    
    print(f"\n📈 RÉSUMÉ FINAL CORRECT:")
    print(f"  • Total fruits (historique): {final_metrics['total_fruits_collected']}")  # Doit être 2
    print(f"  • Fruits cette session: {final_metrics['fruits_collected_this_session']}")  # Doit être 0 (mort réinitialise)
    print(f"  • Total morts: {final_metrics['death_count']}")  # Doit être 1
    print(f"  • Zones à risque: {final_metrics['high_risk_zones']}")
    print(f"  • Ticks analysés: {final_metrics['tick_count']}")
    print(f"  • Durée session: {final_metrics['session_duration']:.2f}s")  # Doit être ~12.0s
    print(f"  • Temps moyen par fruit: {final_metrics['average_fruit_time']:.2f}s")  # Doit être ~4.0s
    
    print(f"\n✅ Démonstration CORRIGÉE terminée!")
    print(f"📁 Métriques exportées dans: data/logs/demo_session_fixed.json")

if __name__ == "__main__":
    demo_analyzer_fixed()