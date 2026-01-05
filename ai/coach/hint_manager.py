# Emplacement: ai/coach/hint_manager.py
import time
from typing import List, Dict
from dataclasses import dataclass

# IMPORT CORRIGÉ ICI
from .hints import Hint, HintGenerator, HintPriority

@dataclass
class DisplayedHint:
    """Conseil actuellement affiché à l'écran"""
    hint: Hint
    start_time: float
    expires_at: float

class HintManager:
    """Gère l'affichage, la file d'attente et la priorisation des conseils"""
    
    def __init__(self, max_concurrent_hints: int = 2):
        self.hint_generator = HintGenerator()
        self.max_concurrent_hints = max_concurrent_hints
        
        self.current_hints: List[DisplayedHint] = []
        self.hint_history: List[Hint] = []
        
        # NOUVEAU : Empêche le spam de conseils du même type
        self.category_cooldowns = {} 
        self.enabled = True
    
    def update(self, metrics, game_state) -> List[Hint]:
        """Met à jour et retourne la liste des conseils à afficher maintenant"""
        if not self.enabled:
            return []
        
        current_time = time.time()
        
        # 1. Nettoyer les conseils dont le temps est écoulé
        self._clean_expired_hints(current_time)
        
        # 2. Demander au générateur de créer de nouveaux conseils potentiels
        new_hints = self.hint_generator.generate_hints(metrics, game_state)
        
        # 3. Filtrer et sélectionner les meilleurs conseils
        hints_to_display = self._select_hints_to_display(new_hints, current_time)
        
        # 4. Les ajouter à la liste active
        for hint in hints_to_display:
            # On vérifie qu'on a de la place à l'écran
            if len(self.current_hints) < self.max_concurrent_hints:
                # Créer un wrapper d'affichage
                display_wrapper = DisplayedHint(
                    hint=hint,
                    start_time=current_time,
                    expires_at=current_time + hint.duration
                )
                self.current_hints.append(display_wrapper)
                
                # Mettre à jour les métriques internes du conseil
                hint.mark_displayed(current_time)
                self.hint_history.append(hint)
        
        # Retourner seulement les objets Hint pour l'affichage
        return [dh.hint for dh in self.current_hints]
    
    def _clean_expired_hints(self, current_time: float):
        """Supprime de la liste les conseils expirés"""
        self.current_hints = [
            dh for dh in self.current_hints 
            if current_time < dh.expires_at
        ]
    
    def _select_hints_to_display(self, new_hints, current_time):
        """Logique de filtrage anti-spam"""
        selected = []
        
        # Trier par priorité (CRITICAL en premier)
        # HintPriority: LOW=1 ... CRITICAL=4
        new_hints.sort(key=lambda h: h.priority.value, reverse=True)

        for hint in new_hints:
            # Vérifier si le conseil individuel est prêt
            if not hint.is_ready(current_time):
                continue

            # Vérifier si on a déjà un conseil affiché identique
            if any(dh.hint.message == hint.message for dh in self.current_hints):
                continue

            # --- LOGIQUE ANTI-SPAM ---
            # Vérifier le cooldown de la CATÉGORIE
            last_cat_time = self.category_cooldowns.get(hint.category, 0)
            
            # Si le dernier conseil de cette catégorie était il y a moins de 5 sec
            # ET que ce n'est pas une urgence critique -> On ignore
            if (current_time - last_cat_time < 5.0) and (hint.priority != HintPriority.CRITICAL):
                continue
                
            # Si on arrive ici, le conseil est validé
            selected.append(hint)
            self.category_cooldowns[hint.category] = current_time
            
            # Si on a rempli notre quota de nouveaux conseils, on arrête
            if len(selected) >= self.max_concurrent_hints:
                break
                
        return selected