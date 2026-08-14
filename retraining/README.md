# Retraining Workspace

This directory is a reserved workspace for future reproducible retraining assets. It is **not** the active online-retraining implementation used by the current ABHEDYA runtime.

The implemented DQN adaptation path is:

```text
backend/dqn_retrain.py
```

That module reads recent detection telemetry from SQLite, prepares the configured DQN feature schema, performs an adaptation cycle, writes the updated model artifact, and records a training diagnostic.

The empty `features/`, `models/`, `scoring/`, `training/`, and `utils/` directories are retained only as a planned structure for a future offline/reproducible training pipeline. They should not be cited as implemented functionality.

See [`../docs/EVALUATION.md`](../docs/EVALUATION.md) for the evaluation standard and the limitations of the current online adaptation metric.
