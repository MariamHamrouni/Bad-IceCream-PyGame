# ai/coach/hints.py
from enum import Enum
from typing import List, Dict, Optional, Tuple
import time
from dataclasses import dataclass

from ai.utils.game_api import GameState

class HintPriority(Enum):
    """Priorité des conseils pour la gestion de l'affichage"""
    LOW = 1      # Conseils d'amélioration générale
    MEDIUM = 2   # Suggestions stratégiques  
    HIGH = 3     # Alertes importantes
    CRITICAL = 4 # Danger immédiat

@dataclass
class Hint:
    """Représentation d'un conseil avec métadonnées"""
    message: str
    priority: HintPriority
    category: str
    duration: float  # Durée d'affichage en secondes
    cooldown: float  # Temps avant de pouvoir réafficher ce conseil
    last_displayed: float = 0  # Timestamp de dernier affichage
    
    def is_ready(self, current_time: float) -> bool:
        """Vérifie si le conseil peut être affiché"""
        return current_time - self.last_displayed >= self.cooldown
    
    def mark_displayed(self, current_time: float):
        """Marque le conseil comme affiché"""
        self.last_displayed = current_time
class HintGenerator:
    """
    Génère des conseils contextuels basés sur l'analyse des performances
    et l'état actuel du jeu
    """
    
    def __init__(self):
        self.hint_templates = self._load_hint_templates()
        self.last_hint_time = 0
        self.min_hint_interval = 3.0  # Secondes entre deux conseils
    
    def generate_hints(self, metrics: Dict, game_state: GameState) -> List[Hint]:
        """
        Génère une liste de conseils basés sur les métriques et l'état du jeu
        
        Args:
            metrics: Métriques du PerformanceAnalyzer
            game_state: État actuel du jeu
            
        Returns:
            List[Hint]: Liste des conseils générés, triés par priorité
        """
        current_time = time.time()
        
        # Vérifier le cooldown global
        if current_time - self.last_hint_time < self.min_hint_interval:
            return []
        
        hints = []
        
        # 1. Conseils basés sur les PERFORMANCES (vos métriques de la semaine 1)
        hints.extend(self._generate_performance_hints(metrics, current_time))
        
        # 2. Conseils basés sur l'ÉTAT ACTUEL du jeu
        hints.extend(self._generate_situational_hints(game_state, current_time))
        
        # 3. Conseils basés sur les PATTERNS de jeu
        hints.extend(self._generate_pattern_hints(metrics, game_state, current_time))
        
        # 4. Conseils de STRATÉGIE avancée
        hints.extend(self._generate_strategic_hints(metrics, game_state, current_time))
        
        # Trier par priorité (critique > haute > moyenne > basse)
        hints.sort(key=lambda h: h.priority.value, reverse=True)
        
        if hints:
            self.last_hint_time = current_time
            
        return hints
    
    def _generate_performance_hints(self, metrics: Dict, current_time: float) -> List[Hint]:
        """Génère des conseils basés sur les métriques de performance"""
        hints = []
        
        # VOS MÉTRIQUES DE LA SEMAINE 1 SONT UTILISÉES ICI !
        
        # Conseils sur la MORT
        if metrics.get('death_count', 0) > 0:
            if len(metrics.get('time_between_deaths', [])) > 0:
                last_death_interval = metrics['time_between_deaths'][-1]
                if last_death_interval < 10:  # Mort très rapide
                    hints.append(Hint(
                        message="⚡ Tu meurs trop vite! Essaie de mieux anticiper les ennemis.",
                        priority=HintPriority.HIGH,
                        category="survie",
                        duration=5.0,
                        cooldown=30.0,
                        last_displayed=0
                    ))
            
            death_count = metrics['death_count']
            if death_count >= 3:
                hints.append(Hint(
                    message="🛡️ Tu meurs souvent. Utilise les blocs de glace pour te protéger!",
                    priority=HintPriority.MEDIUM,
                    category="survie",
                    duration=6.0,
                    cooldown=45.0,
                    last_displayed=0
                ))
        
        # Conseils sur la COLLECTE DE FRUITS
        avg_fruit_time = metrics.get('average_fruit_time', 0)
        if avg_fruit_time > 8.0:
            hints.append(Hint(
                message="🎯 Tu peux collecter les fruits plus rapidement! Planifie ton chemin.",
                priority=HintPriority.LOW,
                category="efficacité",
                duration=4.0,
                cooldown=60.0,
                last_displayed=0
            ))
        
        total_fruits = metrics.get('total_fruits_collected', 0)
        if total_fruits == 0 and metrics.get('tick_count', 0) > 50:
            hints.append(Hint(
                message="🍎 N'oublie pas de collecter les fruits! C'est l'objectif principal.",
                priority=HintPriority.MEDIUM,
                category="objectif",
                duration=5.0,
                cooldown=40.0,
                last_displayed=0
            ))
        
        # Conseils sur les ZONES À RISQUE
        risk_zones = metrics.get('high_risk_zones', 0)
        if risk_zones > 5:
            hints.append(Hint(
                message="🗺️ Tu fréquentes beaucoup de zones dangereuses. Sois plus prudent!",
                priority=HintPriority.MEDIUM,
                category="navigation",
                duration=5.0,
                cooldown=50.0,
                last_displayed=0
            ))
        
        return hints
    
    def _generate_situational_hints(self, game_state: GameState, current_time: float) -> List[Hint]:
        """Génère des conseils basés sur la situation actuelle du jeu"""
        hints = []
        player_pos = game_state.player_pos
        
        # Détection de danger IMMÉDIAT
        immediate_danger = self._check_immediate_danger(game_state)
        if immediate_danger:
            hints.append(Hint(
                message=f"🚨 {immediate_danger}",
                priority=HintPriority.CRITICAL,
                category="danger",
                duration=3.0,
                cooldown=10.0,
                last_displayed=0
            ))
        
        # Conseils sur les FRUITS proches
        nearby_fruits = self._find_nearby_fruits(player_pos, game_state.fruits_pos)
        if nearby_fruits and len(nearby_fruits) > 2:
            hints.append(Hint(
                message="💰 Plusieurs fruits proches! Profites-en pour faire le plein.",
                priority=HintPriority.LOW,
                category="opportunité",
                duration=4.0,
                cooldown=30.0,
                last_displayed=0
            ))
        
        # Conseils sur les ENNEMIS proches
        nearby_enemies = self._find_nearby_enemies(player_pos, game_state.trolls_pos)
        if len(nearby_enemies) >= 2:
            hints.append(Hint(
                message="👥 Deux ennemis ou plus proches! Utilise F pour créer des barrières.",
                priority=HintPriority.HIGH,
                category="défense",
                duration=4.0,
                cooldown=25.0,
                last_displayed=0
            ))
        
        # Conseils de BLOCAGE stratégique
        if self._is_player_cornered(player_pos, game_state):
            hints.append(Hint(
                message="🚧 Tu es coincé! Utilise ESPACE pour détruire les blocs et t'échapper.",
                priority=HintPriority.HIGH,
                category="évasion",
                duration=4.0,
                cooldown=20.0,
                last_displayed=0
            ))
        
        return hints
    
    def _generate_pattern_hints(self, metrics: Dict, game_state: GameState, current_time: float) -> List[Hint]:
        """Génère des conseils basés sur les patterns de jeu détectés"""
        hints = []
        
        # VOS DONNÉES DE PATTERN DE LA SEMAINE 1
        fruit_order = metrics.get('fruit_order', [])
        player_routes = metrics.get('total_routes_recorded', 0)
        
        # Détection de patterns répétitifs
        if len(fruit_order) >= 3:
            # Vérifier si le joueur collecte toujours dans le même ordre
            if self._has_repetitive_pattern(fruit_order):
                hints.append(Hint(
                    message="🔄 Tu suis toujours le même chemin. Essaie de varier ta stratégie!",
                    priority=HintPriority.LOW,
                    category="stratégie",
                    duration=5.0,
                    cooldown=90.0,
                    last_displayed=0
                ))
        
        # Conseils sur l'utilisation des blocs de glace
        ice_usage = metrics.get('ice_block_usage', 0)
        if ice_usage == 0 and metrics.get('tick_count', 0) > 100:
            hints.append(Hint(
                message="❄️ N'oublie pas que tu peux créer des blocs avec F! Très utile pour bloquer les ennemis.",
                priority=HintPriority.MEDIUM,
                category="mécanique",
                duration=6.0,
                cooldown=120.0,
                last_displayed=0
            ))
        
        return hints
    
    def _generate_strategic_hints(self, metrics: Dict, game_state: GameState, current_time: float) -> List[Hint]:
        """Génère des conseils stratégiques avancés"""
        hints = []
        
        # Conseils de fin de niveau
        fruits_remaining = len(game_state.fruits_pos)
        total_fruits_collected = metrics.get('total_fruits_collected', 0)
        
        if fruits_remaining == 0 and total_fruits_collected > 0:
            hints.append(Hint(
                message="✅ Niveau terminé! Bravo!",
                priority=HintPriority.LOW,
                category="réussite",
                duration=3.0,
                cooldown=10.0,
                last_displayed=0
            ))
        
        elif fruits_remaining == 1 and total_fruits_collected > 0:
            hints.append(Hint(
                message="🎉 Plus qu'un fruit! Fais attention aux derniers ennemis.",
                priority=HintPriority.MEDIUM,
                category="objectif",
                duration=4.0,
                cooldown=15.0,
                last_displayed=0
        ))
        
        # Conseils selon le niveau
        level = game_state.level
        if level == 1 and metrics.get('tick_count', 0) < 50:
            hints.append(Hint(
                message="🎮 Astuce: Déplace-toi avec ZQSD ou les flèches, F pour la glace, ESPACE pour casser.",
                priority=HintPriority.LOW,
                category="tutoriel",
                duration=8.0,
                cooldown=300.0,  # Long cooldown pour ne pas répéter
                last_displayed=0
            ))
        
        return hints
    
    def _check_immediate_danger(self, game_state: GameState) -> Optional[str]:
        """Vérifie les dangers immédiats nécessitant une alerte critique"""
        player_pos = game_state.player_pos
        
        for troll_pos in game_state.trolls_pos:
            distance = self._calculate_distance(player_pos, troll_pos)
            if distance < 60:  # Très proche - danger immédiat
                # Déterminer la direction
                dx = troll_pos[0] - player_pos[0]
                dy = troll_pos[1] - player_pos[1]
                
                if abs(dx) > abs(dy):
                    direction = "DROITE" if dx > 0 else "GAUCHE"
                else:
                    direction = "BAS" if dy > 0 else "HAUT"
                
                return f"Ennemi très proche à ta {direction}! FUIS ou BLOQUE!"
        
        return None
    
    def _find_nearby_fruits(self, player_pos: Tuple[int, int], fruits_pos: List[Tuple[int, int]], radius: int = 100) -> List[Tuple[int, int]]:
        """Trouve les fruits proches du joueur"""
        nearby = []
        for fruit_pos in fruits_pos:
            if self._calculate_distance(player_pos, fruit_pos) <= radius:
                nearby.append(fruit_pos)
        return nearby
    
    def _find_nearby_enemies(self, player_pos: Tuple[int, int], enemies_pos: List[Tuple[int, int]], radius: int = 150) -> List[Tuple[int, int]]:
        """Trouve les ennemis proches du joueur"""
        nearby = []
        for enemy_pos in enemies_pos:
            if self._calculate_distance(player_pos, enemy_pos) <= radius:
                nearby.append(enemy_pos)
        return nearby
    
    def _is_player_cornered(self, player_pos: Tuple[int, int], game_state: GameState) -> bool:
        """Vérifie si le joueur est coincé"""
        # Vérifier les directions possibles
        directions = [
            (player_pos[0] + 40, player_pos[1]),  # droite
            (player_pos[0] - 40, player_pos[1]),  # gauche
            (player_pos[0], player_pos[1] + 58),  # bas
            (player_pos[0], player_pos[1] - 58)   # haut
        ]
        
        blocked_directions = 0
        for direction in directions:
            if not self._is_valid_position(direction, game_state):
                blocked_directions += 1
        
        # Coincé si au moins 3 directions sur 4 sont bloquées
        return blocked_directions >= 3
    
    def _has_repetitive_pattern(self, fruit_order: List[str]) -> bool:
        """Détecte les patterns répétitifs dans l'ordre de collecte"""
        if len(fruit_order) < 3:
            return False
        
        # Vérifier les séquences répétées
        for pattern_length in range(2, min(4, len(fruit_order) // 2 + 1)):
            for i in range(len(fruit_order) - pattern_length * 2 + 1):
                sequence1 = fruit_order[i:i + pattern_length]
                sequence2 = fruit_order[i + pattern_length:i + pattern_length * 2]
                if sequence1 == sequence2:
                    return True
        
        return False
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calcule la distance entre deux points"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    
    def _is_valid_position(self, pos: Tuple[int, int], game_state: GameState) -> bool:
        """Vérifie si une position est valide (pas d'obstacles)"""
        # Vérifier les bords
        if pos[0] < 50 or pos[0] >= 770 or pos[1] < 50 or pos[1] >= 572:
            return False
        
        # Vérifier les blocs de glace
        for ice_pos in game_state.iceblocks_pos:
            if self._calculate_distance(pos, ice_pos) < 30:
                return False
        
        return True
    
    def _load_hint_templates(self) -> Dict[str, List[str]]:
        """Charge les templates de conseils par catégorie"""
        return {
            "survie": [
                "Attention aux ennemis! Garde tes distances.",
                "Utilise les blocs de glace comme bouclier!",
                "Quand tu es entouré, casse les blocs avec ESPACE!"
            ],
            "stratégie": [
                "Planifie ton chemin pour collecter plusieurs fruits rapidement!",
                "Varie tes routes pour surprendre les ennemis!",
                "N'oublie pas de bloquer les passages stratégiques!"
            ],
            "efficacité": [
                "Tu peux collecter les fruits en séquence pour gagner du temps!",
                "Utilise la glace pour créer des raccourcis!",
                "Observe les patterns des ennemis pour les éviter!"
            ]
        }