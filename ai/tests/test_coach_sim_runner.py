from pathlib import Path
import json

from ai.coach.sim_runner import run_simulation


def test_run_simulation_creates_logs(tmp_path: Path):
    # 1) créer un mini dossier de snapshots
    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir()

    s0 = {
        "tick": 0,
        "grid": [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
        "player": {"x": 1, "y": 1, "lives": 3},
        "enemies": [],
        "fruits": [[1, 1]],
    }
    s1 = {
        "tick": 10,
        "grid": [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
        "player": {"x": 1, "y": 1, "lives": 2},
        "enemies": [],
        "fruits": [],
    }

    (snapshots_dir / "runX_tick0.json").write_text(json.dumps(s0), encoding="utf-8")
    (snapshots_dir / "runX_tick10.json").write_text(json.dumps(s1), encoding="utf-8")

    # 2) dossier de logs
    logs_dir = tmp_path / "logs"

    # 3) lancer la simulation
    run_simulation(snapshots_dir, prefix="runX_", logs_dir=logs_dir)

    # 4) vérifier que les fichiers existent
    metrics_path = logs_dir / "metrics_runX.json"
    hints_path = logs_dir / "hints_runX.json"

    assert metrics_path.exists()
    assert hints_path.exists()

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    hints = json.loads(hints_path.read_text(encoding="utf-8"))

    assert metrics["death_count"] == 1
    assert metrics["fruit_collected"] == 1
    assert isinstance(hints, list)
    assert len(hints) >= 1
    assert "hint" in hints[0]
