# Emplacement: ai/utils/game_api.py
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Union

@dataclass(frozen=True)  # frozen=True rend l'objet immuable (plus sûr pour le multi-threading/IA)
class GameState:
    """
    Snapshot immuable du jeu transféré à l'IA.
    Contient toutes les données nécessaires pour prendre une décision à l'instant T.
    """
    player_pos: Tuple[int, int]
    player_alive: bool
    trolls_pos: List[Tuple[int, int]]
    iceblocks_pos: List[Tuple[int, int]]
    fruits_pos: List[Tuple[int, int]]
    
    # Métadonnées contextuelles
    timer: float
    score: int
    level: int = 1
    
    # Données enrichies (Optionnel)
    trolls_info: List[Dict] = field(default_factory=list) # Contient {'id': 1, 'role': 'hunter'}
    fruit_types: Dict[Tuple[int, int], str] = field(default_factory=dict)
    player_has_block: bool = False

def create_game_state_for_analyzer(
    player_pos: Union[Tuple[int, int], Any], # Accepte un Tuple ou un Sprite/Rect
    player_alive: bool,
    trolls_info: List[Any], # Liste de dicts ou de Sprites
    fruits: List[Any],
    iceblocks: List[Any],
    timer: float,
    score: int,
    player_has_block: bool = False
) -> GameState:
    """
    Convertit les données brutes du moteur de jeu en un objet GameState propre.
    Gère automatiquement l'extraction des positions depuis des Sprites Pygame ou des Dictionnaires.
    """
    
    # 1. Extraction Position Joueur
    # Si c'est un rect ou un sprite, on prend le center
    p_pos = player_pos
    if hasattr(player_pos, 'rect'):
        p_pos = player_pos.rect.center
    elif hasattr(player_pos, 'center'):
        p_pos = player_pos.center
        
    # 2. Nettoyage des Trolls
    clean_trolls_pos = []
    clean_trolls_info = []
    
    for t in trolls_info:
        pos = (0, 0)
        info = {'id': 0, 'role': 'unknown'}
        
        # Cas 1: C'est un Dictionnaire (ex: venant de la simu)
        if isinstance(t, dict):
            pos = t.get('pos', (0, 0))
            info = t
        # Cas 2: C'est un Sprite Troll (ex: venant du jeu)
        elif hasattr(t, 'rect'):
            pos = t.rect.center
            info = {'id': id(t), 'role': getattr(t, 'role_type', 'unknown'), 'pos': pos}
            
        clean_trolls_pos.append(pos)
        clean_trolls_info.append(info)

    # 3. Nettoyage des Fruits
    clean_fruits_pos = []
    clean_fruit_types = {}
    
    for f in fruits:
        pos = (0, 0)
        ftype = 'apple'
        
        if isinstance(f, dict):
            pos = f.get('pos', (0, 0))
            ftype = f.get('type', 'apple')
        elif hasattr(f, 'rect'):
            pos = f.rect.center
            ftype = getattr(f, 'fruit_type', 'apple')
            
        clean_fruits_pos.append(pos)
        clean_fruit_types[pos] = ftype

    # 4. Nettoyage des Murs (Iceblocks)
    clean_ice = []
    for i in iceblocks:
        if isinstance(i, (tuple, list)):
            clean_ice.append(tuple(i))
        elif hasattr(i, 'rect'): # Sprite
            clean_ice.append(i.rect.topleft) # On utilise topleft pour les murs pour l'alignement grille

    return GameState(
        player_pos=p_pos,
        player_alive=player_alive,
        trolls_pos=clean_trolls_pos,
        trolls_info=clean_trolls_info,
        iceblocks_pos=clean_ice,
        fruits_pos=clean_fruits_pos,
        fruit_types=clean_fruit_types,
        timer=timer,
        score=score,
        player_has_block=player_has_block
    )