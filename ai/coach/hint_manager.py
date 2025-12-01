# ai/coach/hint_manager.py
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

from .hints import Hint, HintGenerator, HintPriority

@dataclass
class DisplayedHint:
    """Conseil actuellement affiché"""
    hint: Hint
    start_time: float
    expires_at: float

class HintManager:
    """
    Gère l'affichage et la priorisation des conseils
    Évite le spam et gère les conflits
    """
    
    def __init__(self, max_concurrent_hints: int = 2):
        self.hint_generator = HintGenerator()
        self.max_concurrent_hints = max_concurrent_hints
        self.current_hints: List[DisplayedHint] = []
        self.hint_history: List[Hint] = []
        
        # Configuration d'affichage
        self.enabled = True
        self.min_display_time = 2.0  # Temps minimum d'affichage
    
    def update(self, metrics: Dict, game_state) -> List[Hint]:
        """
        Met à jour le système de conseils et retourne les conseils à afficher
        
        Returns:
            List[Hint]: Conseils à afficher (peut être vide)
        """
        if not self.enabled:
            return []
        
        current_time = time.time()
        
        # Nettoyer les conseils expirés
        self._clean_expired_hints(current_time)
        
        # Générer de nouveaux conseils
        new_hints = self.hint_generator.generate_hints(metrics, game_state)
        
        # Filtrer et prioriser
        hints_to_display = self._select_hints_to_display(new_hints, current_time)
        
        # Ajouter à l'affichage
        for hint in hints_to_display:
            if len(self.current_hints) < self.max_concurrent_hints:
                self.current_hints.append(DisplayedHint(
                    hint=hint,
                    start_time=current_time,
                    expires_at=current_time + hint.duration
                ))
                hint.mark_displayed(current_time)
                self.hint_history.append(hint)
        
        return [dh.hint for dh in self.current_hints]
    
    def get_current_hints(self) -> List[Hint]:
        """Retourne les conseils actuellement affichés"""
        return [dh.hint for dh in self.current_hints]
    
    def clear_hints(self):
        """Efface tous les conseils affichés"""
        self.current_hints.clear()
    
    def disable(self):
        """Désactive le système de conseils"""
        self.enabled = False
        self.clear_hints()
    
    def enable(self):
        """Active le système de conseils"""
        self.enabled = True
    
    def _clean_expired_hints(self, current_time: float):
        """Supprime les conseils expirés"""
        self.current_hints = [
            dh for dh in self.current_hints 
            if current_time < dh.expires_at
        ]
    
    def _select_hints_to_display(self, new_hints: List[Hint], current_time: float) -> List[Hint]:
        """
        Sélectionne les conseils à afficher selon la priorité et les limitations
        """
        if not new_hints:
            return []
        
        # Filtrer les conseils qui sont prêts (cooldown respecté)
        available_hints = [h for h in new_hints if h.is_ready(current_time)]
        
        if not available_hints:
            return []
        
        # Trier par priorité
        available_hints.sort(key=lambda h: h.priority.value, reverse=True)
        
        # Prendre les plus prioritaires jusqu'à la limite
        selected_hints = available_hints[:self.max_concurrent_hints]
        
        # Éviter les doublons avec les conseils déjà affichés
        current_messages = {dh.hint.message for dh in self.current_hints}
        selected_hints = [h for h in selected_hints if h.message not in current_messages]
        
        return selected_hints
    
    def get_stats(self) -> Dict:
        """Retourne des statistiques sur l'utilisation des conseils"""
        return {
            "total_hints_generated": len(self.hint_history),
            "currently_displayed": len(self.current_hints),
            "enabled": self.enabled,
            "recent_hints": [
                {
                    "message": h.message,
                    "priority": h.priority.name,
                    "category": h.category,
                    "timestamp": h.last_displayed
                }
                for h in self.hint_history[-5:]  # 5 derniers conseils
            ]
        }