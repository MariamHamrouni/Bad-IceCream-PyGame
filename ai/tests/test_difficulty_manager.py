from ai.design.difficulty_manager import DifficultyManager, DifficultyBounds
from ai.coach.analyzer import Metrics


def test_difficulty_easy_when_player_struggles():
    manager = DifficultyManager(base_enemy_count=5, base_spawn_interval=100)

    metrics = Metrics(
        death_count=5,
        fruit_collected=0,
        ticks_played=500,
        time_between_deaths=[30, 40, 20],
    )

    config = manager.adjust_difficulty(metrics)

    assert config.enemy_count < 5
    assert config.spawn_interval >= 100


def test_difficulty_hard_when_player_is_good():
    manager = DifficultyManager(base_enemy_count=3, base_spawn_interval=90)

    metrics = Metrics(
        death_count=0,
        fruit_collected=10,
        ticks_played=800,
        time_between_deaths=[],
    )

    config = manager.adjust_difficulty(metrics)

    assert config.enemy_count >= 3
    assert config.spawn_interval <= 90


def test_ratios_are_normalized():
    manager = DifficultyManager()
    metrics = Metrics(
        death_count=1,
        fruit_collected=2,
        ticks_played=200,
        time_between_deaths=[150],
    )

    config = manager.adjust_difficulty(metrics)
    total = config.hunter_ratio + config.patroller_ratio + config.blocker_ratio

    assert abs(total - 1.0) < 1e-6
