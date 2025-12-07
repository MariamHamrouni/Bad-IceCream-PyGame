from ai.coach.hints import HintEngine, HintConfig
from ai.coach.analyzer import Metrics


def test_hint_trigger_on_deaths():
    metrics = Metrics(death_count=2, ticks_played=50)
    engine = HintEngine(HintConfig(cooldown_ticks=0))

    hint = engine.generate_hint(metrics, current_tick=50)

    assert hint is not None
    assert "vie" in hint.lower() or "perds" in hint.lower()


def test_hint_cooldown():
    metrics = Metrics(death_count=1, ticks_played=10)
    engine = HintEngine(HintConfig(cooldown_ticks=50))

    h1 = engine.generate_hint(metrics, current_tick=0)
    h2 = engine.generate_hint(metrics, current_tick=10)  # trop tôt, cooldown

    assert h1 is not None
    assert h2 is None


def test_hint_fruit_warning():
    metrics = Metrics(fruit_collected=0, ticks_played=200)
    engine = HintEngine(HintConfig(cooldown_ticks=0))

    hint = engine.generate_hint(metrics, current_tick=200)

    assert hint is not None
    assert "fruit" in hint.lower()
