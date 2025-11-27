# ai/utils/game_api.py
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class GameState:
    """Représentation de l'état du jeu pour l'IA"""
    player_pos: Tuple[int, int]
    player_alive: bool
    trolls_pos: List[Tuple[int, int]]
    iceblocks_pos: List[Tuple[int, int]]
    fruits_pos: List[Tuple[int, int]]
    fruits_collected: List[Tuple[int, int]]  # Fruits déjà collectés
    level: int
    round: int
    timer: float  # Temps écoulé dans la partie
    score: int

class GameAPI:
    """Interface pour communiquer avec le jeu"""
    
    SCHEMA_VERSION = 1
    
    @classmethod
    def load_snapshot(cls, json_file: str) -> GameState:
        """Charge un snapshot JSON du jeu"""
        file_path = Path(json_file)
        if not file_path.exists():
            # Retourner un état mock pour les tests
            return cls._create_mock_state()
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls._parse_game_state(data)
    
    @classmethod
    def get_current_state(cls) -> GameState:
        """Récupère l'état actuel du jeu (pour intégration future)"""
        # Pour l'instant, retourne un état mock
        return cls._create_mock_state()
    
    @staticmethod
    def _create_mock_state() -> GameState:
        """Crée un état de jeu mock pour les tests"""
        return GameState(
            player_pos=(100, 100),
            player_alive=True,
            trolls_pos=[(200, 150), (300, 200)],
            iceblocks_pos=[(150, 100), (250, 150)],
            fruits_pos=[(120, 120), (180, 180), (220, 220)],
            fruits_collected=[],
            level=1,
            round=1,
            timer=0.0,
            score=0
        )
    
    @staticmethod
    def _parse_game_state(data: Dict[str, Any]) -> GameState:
        """Parse les données JSON en GameState"""
        return GameState(
            player_pos=tuple(data['player_pos']),
            player_alive=data['player_alive'],
            trolls_pos=[tuple(pos) for pos in data['trolls_pos']],
            iceblocks_pos=[tuple(pos) for pos in data['iceblocks_pos']],
            fruits_pos=[tuple(pos) for pos in data['fruits_pos']],
            fruits_collected=[tuple(pos) for pos in data.get('fruits_collected', [])],
            level=data['level'],
            round=data['round'],
            timer=data['timer'],
            score=data['score']
        )
    
    @staticmethod
    def export_metrics(metrics: Dict, filename: str):
        """Exporte les métriques en JSON"""
        output_dir = Path("data/logs")
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / filename
        with open(file_path, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)