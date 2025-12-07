from ai.coach.analyzer import GameAnalyzer
from ai.utils.game_api import GameState, PlayerState, EnemyState


def make_state(tick: int, lives: int, fruits):
    """
    Petit helper pour fabriquer un GameState minimal pour les tests.
    - fruits: liste de tuples (x, y)
    """
    grid = [[0]]  # peu importe pour ces tests
    player = PlayerState(x=0, y=0, lives=lives)
    enemies = [EnemyState(id="e1", x=0, y=0)]
    return GameState(
        tick=tick,
        grid=grid,
        player=player,
        enemies=enemies,
        fruits=list(fruits),
    )


def test_analyzer_counts_deaths_and_fruits():
    analyzer = GameAnalyzer()

    # tick 0 : 3 vies, 2 fruits
    s0 = make_state(tick=0, lives=3, fruits=[(1, 1), (2, 2)])
    analyzer.update(s0)

    # tick 10 : joueur perd une vie, mange un fruit
    s1 = make_state(tick=10, lives=2, fruits=[(2, 2)])
    analyzer.update(s1)

    # tick 20 : pas de changement de vie, un autre fruit mangé
    s2 = make_state(tick=20, lives=2, fruits=[])
    analyzer.update(s2)

    data = analyzer.to_dict()

    assert data["death_count"] == 1
    assert data["fruit_collected"] == 2
    # l’ordre peut être vérifié si besoin
    assert (1, 1) in data["fruit_order"]
    assert (2, 2) in data["fruit_order"]
    assert data["ticks_played"] == 3
    # temps entre les morts : ici une seule mort => liste vide ou de taille 0
    assert data["time_between_deaths"] in ([], [])
