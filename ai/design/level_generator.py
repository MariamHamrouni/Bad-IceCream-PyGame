# Emplacement: ai/design/level_generator.py
import random
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# Assurez-vous d'avoir ce fichier geometry.py corrigé précédemment
from ai.utils.geometry import Rectangle

class LevelTheme(Enum):
    FOREST = "forest"
    ICE = "ice"
    CAVE = "cave"

@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def rect(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)

class LevelGenerator:
    """Générateur de niveaux via BSP (Binary Space Partitioning)"""
    
    def __init__(self, width: int = 820, height: int = 622, min_room_size: int = 100):
        self.width = width
        self.height = height
        self.min_room_size = min_room_size
        self.rooms: List[Room] = []
        self.corridors: List[Dict] = []
        self.map_data = {}  # Stockage temporaire

    def generate(self, theme: LevelTheme = LevelTheme.FOREST, difficulty: float = 0.5) -> Dict:
        """Point d'entrée principal pour générer un niveau complet"""
        self.rooms = []
        self.corridors = []
        
        # 1. Création de l'arbre BSP et des salles
        root_node = Room(50, 50, self.width - 100, self.height - 100) # Marges de sécurité
        self._split_node(root_node, iteration=0)
        
        # 2. Remplissage des données
        level_data = {
            "metadata": {"theme": theme.value, "difficulty": difficulty},
            "iceblocks": [],
            "fruits": [],
            "trolls": [],
            "player_start": (100, 100)
        }
        
        # 3. Génération des Murs (Glace)
        # On remplit tout d'abord, puis on creuse les salles
        self._generate_walls(level_data)
        
        # 4. Placement du Joueur (Sécurisé)
        self._place_player_safe(level_data)
        
        # 5. Placement des Entités (Fruits & Ennemis)
        self._place_entities(level_data, difficulty)
        
        return level_data

    def _split_node(self, node: Room, iteration: int):
        """Divise récursivement l'espace"""
        if iteration > 4 or (node.width < self.min_room_size * 2 and node.height < self.min_room_size * 2):
            # Feuille atteinte : on crée une salle ici
            # On la rétrécit un peu pour créer des murs naturels
            room_w = random.randint(int(node.width * 0.6), int(node.width * 0.9))
            room_h = random.randint(int(node.height * 0.6), int(node.height * 0.9))
            room_x = node.x + (node.width - room_w) // 2
            room_y = node.y + (node.height - room_h) // 2
            
            self.rooms.append(Room(room_x, room_y, room_w, room_h))
            return

        # Division
        split_horizontally = random.choice([True, False])
        
        if split_horizontally:
            split_y = random.randint(int(node.height * 0.4), int(node.height * 0.6))
            child1 = Room(node.x, node.y, node.width, split_y)
            child2 = Room(node.x, node.y + split_y, node.width, node.height - split_y)
        else:
            split_x = random.randint(int(node.width * 0.4), int(node.width * 0.6))
            child1 = Room(node.x, node.y, split_x, node.height)
            child2 = Room(node.x + split_x, node.y, node.width - split_x, node.height)

        self._split_node(child1, iteration + 1)
        self._split_node(child2, iteration + 1)
        
        # Créer un couloir entre les deux enfants (approximatif)
        self._create_corridor(child1, child2)

    def _create_corridor(self, room1: Room, room2: Room):
        c1 = room1.center
        c2 = room2.center
        
        # On ajoute deux segments (L-shape)
        # Horizontal
        self.corridors.append({"type": "h", "x": min(c1[0], c2[0]), "y": c1[1], "len": abs(c2[0] - c1[0])})
        # Vertical
        self.corridors.append({"type": "v", "x": c2[0], "y": min(c1[1], c2[1]), "len": abs(c2[1] - c1[1])})

    def _generate_walls(self, level_data):
        """Génère les blocs de glace en évitant les salles et couloirs"""
        block_size_x, block_size_y = 40, 58
        
        # Grille virtuelle
        for y in range(50, self.height - 50, block_size_y):
            for x in range(50, self.width - 50, block_size_x):
                # Par défaut on met un mur
                place_wall = True
                
                # Si c'est dans une salle, on enlève
                rect = Rectangle(x, y, block_size_x, block_size_y)
                for room in self.rooms:
                    # On utilise une tolérance pour ne pas coller aux murs
                    if (x > room.x and x < room.x + room.width and 
                        y > room.y and y < room.y + room.height):
                        place_wall = False
                        break
                
                # Si c'est dans un couloir, on enlève (avec largeur min de 60px)
                if place_wall:
                    for corr in self.corridors:
                        if corr["type"] == "h":
                            if abs(y - corr["y"]) < 40 and (corr["x"] <= x <= corr["x"] + corr["len"]):
                                place_wall = False
                        else: # v
                            if abs(x - corr["x"]) < 40 and (corr["y"] <= y <= corr["y"] + corr["len"]):
                                place_wall = False
                
                if place_wall:
                    level_data["iceblocks"].append((x, y))

    def _place_player_safe(self, level_data):
        """Trouve une position de départ GARANTIE sans collision"""
        if not self.rooms:
            level_data['player_start'] = (100, 100)
            return

        # On prend la première salle
        start_room = self.rooms[0]
        cx, cy = start_room.center
        
        # Vérification ultime : est-ce qu'il y a un bloc ici ?
        # Si oui, on nettoie la zone autour
        safe_zone = Rectangle(cx - 50, cy - 50, 100, 100)
        
        # Filtrer les blocs qui sont dans la zone de départ
        level_data["iceblocks"] = [
            b for b in level_data["iceblocks"] 
            if not (safe_zone.x < b[0] < safe_zone.right and safe_zone.y < b[1] < safe_zone.bottom)
        ]
        
        level_data['player_start'] = (cx, cy)

    def _place_entities(self, level_data, difficulty):
        """Place fruits et ennemis dans les autres salles"""
        # ... Logique de placement aléatoire dans self.rooms[1:] ...
        # (Simplifié pour la démo)
        for room in self.rooms[1:]:
            if random.random() < difficulty:
                level_data["trolls"].append({"pos": room.center, "role": "patroller"})
            
            level_data["fruits"].append({"pos": (room.x + 20, room.y + 20), "type": "apple"})