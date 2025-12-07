from __future__ import annotations

from pathlib import Path
import json
from typing import List

from ai.utils.game_api import SnapshotGameAPI
from ai.coach.analyzer import GameAnalyzer
from ai.coach.hints import HintEngine, HintConfig


def load_snapshot_names(snapshots_dir: Path, prefix: str) -> List[str]:
    """
    Retourne les noms de snapshots (sans .json) correspondant au préfixe.
    Ex: prefix='run1_' -> ['run1_tick0', 'run1_tick10']
    """
    names: List[str] = []
    for path in snapshots_dir.glob(f"{prefix}*.json"):
        names.append(path.stem)
    names.sort()
    return names


def run_simulation(
    snapshots_dir: str | Path,
    prefix: str,
    logs_dir: str | Path = "data/logs",
) -> None:
    """
    Simulation headless du coach :
    - lit des snapshots JSON
    - met à jour GameAnalyzer
    - génère des hints avec HintEngine
    - sauvegarde métriques + hints dans logs_dir
    """

    snapshots_dir = Path(snapshots_dir)
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)

    api = SnapshotGameAPI(snapshots_dir)
    analyzer = GameAnalyzer()
    hint_engine = HintEngine(HintConfig(cooldown_ticks=5))

    snapshot_names = load_snapshot_names(snapshots_dir, prefix)
    if not snapshot_names:
        raise RuntimeError(
            f"Aucun snapshot trouvé avec le préfixe '{prefix}' dans {snapshots_dir}"
        )

    hints_log: List[dict] = []

    for name in snapshot_names:
        state = api.load_snapshot(name)
        analyzer.update(state)

        hint = hint_engine.generate_hint(analyzer.metrics, current_tick=state.tick)
        if hint:
            hints_log.append(
                {
                    "tick": state.tick,
                    "hint": hint,
                    "death_count": analyzer.metrics.death_count,
                    "fruit_collected": analyzer.metrics.fruit_collected,
                }
            )

    # métriques finales
    metrics_path = logs_dir / f"metrics_{prefix.rstrip('_')}.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(analyzer.to_dict(), f, indent=2)

    # hints
    hints_path = logs_dir / f"hints_{prefix.rstrip('_')}.json"
    with hints_path.open("w", encoding="utf-8") as f:
        json.dump(hints_log, f, indent=2)

    print(f"[coach_sim] Metrics saved to: {metrics_path}")
    print(f"[coach_sim] Hints saved to:   {hints_path}")


if __name__ == "__main__":
    # Exemple: python -m ai.coach.sim_runner
    run_simulation("data/snapshots", prefix="run1_")
